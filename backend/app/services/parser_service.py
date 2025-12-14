"""
Main workout plan parser service orchestrating LLM and exercise matching.
"""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.enums import ConfidenceLevelEnum
from app.models import Exercise, WorkoutImportLog
from app.schemas.workout_plans import (
    ParsedExerciseItem,
    ParsedExerciseMatch,
    ParsedWorkoutItem,
    ParsedWorkoutPlan,
    WorkoutPlanParseResponse,
)
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class ParserService:
    """Service for parsing workout plans from text"""

    def __init__(self, db: Session, user_id: UUID):
        self.db = db
        self.user_id = user_id

    async def parse_workout_plan(self, text: str) -> WorkoutPlanParseResponse:
        """
        Parse workout plan text into structured format with exercise matching.

        Args:
            text: Raw workout plan text

        Returns:
            WorkoutPlanParseResponse with parsed data and statistics
        """
        # Step 1: Load all exercises from database
        logger.info(f"Parsing workout plan for user {self.user_id}")
        exercises = self.db.query(Exercise).filter(
            (not Exercise.is_custom) | (Exercise.user_id == self.user_id)
        ).all()
        
        # Format exercises for LLM
        exercise_dicts = [
            {
                'id': str(ex.id),
                'name': ex.name,
                'primary_muscle_groups': [mg.value for mg in ex.primary_muscle_groups],
                'secondary_muscle_groups': [mg.value for mg in (ex.secondary_muscle_groups or [])],
            }
            for ex in exercises
        ]
        
        # Step 2: Use LLM to extract structure and match exercises
        llm_result = await llm_service.parse_workout_text(text, exercise_dicts)

        # Step 3: Process workouts with LLM-matched exercises
        parsed_workouts = []
        stats = {"high": 0, "medium": 0, "low": 0, "unmatched": 0}
        total_exercises = 0
        
        # Create exercise lookup
        exercise_map = {str(ex.id): ex for ex in exercises}

        for workout_data in llm_result.get("workouts", []):
            parsed_workout = self._process_workout(workout_data, exercise_map, stats)
            parsed_workouts.append(parsed_workout)
            total_exercises += len(parsed_workout.exercises)

        # Step 4: Create import log
        import_log = WorkoutImportLog(
            user_id=self.user_id,
            workout_plan_id=None,  # Will be set when plan is created
            raw_text=text,
            parsed_exercises=llm_result.get("workouts", []),
            confidence_scores={
                "high_confidence": stats["high"],
                "medium_confidence": stats["medium"],
                "low_confidence": stats["low"],
                "unmatched": stats["unmatched"],
            },
            created_at=datetime.utcnow(),
        )
        self.db.add(import_log)
        self.db.commit()
        self.db.refresh(import_log)

        logger.info(
            f"Parsed {len(parsed_workouts)} workouts with {total_exercises} exercises: "
            f"{stats['high']} high, {stats['medium']} medium, "
            f"{stats['low']} low, {stats['unmatched']} unmatched"
        )

        # Step 5: Build response
        parsed_plan = ParsedWorkoutPlan(
            name=llm_result.get("name", "Workout Plan"),
            description=llm_result.get("description"),
            workouts=parsed_workouts,
            raw_text=text,
            import_log_id=import_log.id,
        )

        return WorkoutPlanParseResponse(
            parsed_plan=parsed_plan,
            total_exercises=total_exercises,
            high_confidence_count=stats["high"],
            medium_confidence_count=stats["medium"],
            low_confidence_count=stats["low"],
            unmatched_count=stats["unmatched"],
        )

    def _process_workout(
        self, workout_data: dict, exercise_map: dict, stats: dict
    ) -> ParsedWorkoutItem:
        """Process a single workout and its exercises"""
        parsed_exercises = []

        for ex_data in workout_data.get("exercises", []):
            parsed_ex = self._build_exercise_from_llm(ex_data, exercise_map, stats)
            parsed_exercises.append(parsed_ex)

        return ParsedWorkoutItem(
            name=workout_data.get("name", "Workout"),
            day_number=workout_data.get("day_number"),
            order_index=workout_data.get("order_index", 0),
            exercises=parsed_exercises,
        )

    def _build_exercise_from_llm(
        self, ex_data: dict, exercise_map: dict, stats: dict
    ) -> ParsedExerciseItem:
        """Build ParsedExerciseItem from LLM-matched exercise data"""
        original_text = ex_data.get("original_text", "")
        exercise_id = ex_data.get("exercise_id")
        confidence = ex_data.get("confidence", 0.0)

        # Build matched exercise if LLM found a match
        matched_exercise = None
        if exercise_id and exercise_id in exercise_map and confidence >= 0.70:
            exercise = exercise_map[exercise_id]
            
            # Determine confidence level based on score
            if confidence >= 0.90:
                confidence_level = ConfidenceLevelEnum.HIGH
                stats["high"] += 1
            elif confidence >= 0.80:
                confidence_level = ConfidenceLevelEnum.MEDIUM
                stats["medium"] += 1
            else:  # 0.70-0.79
                confidence_level = ConfidenceLevelEnum.LOW
                stats["low"] += 1
            
            matched_exercise = ParsedExerciseMatch(
                exercise_id=exercise.id,
                exercise_name=exercise.name,
                original_text=original_text,
                confidence=confidence,
                confidence_level=confidence_level,
                primary_muscle_groups=exercise.primary_muscle_groups,
                secondary_muscle_groups=exercise.secondary_muscle_groups or [],
            )
        else:
            stats["unmatched"] += 1

        # Build set configurations from LLM response
        sets_data = ex_data.get("sets", [])
        if not sets_data:
            # Fallback if LLM didn't return sets array
            sets_data = [{"reps_min": 8, "reps_max": 12}] * 3
        
        from app.schemas.workout_plans import SetConfig
        set_configurations = [
            SetConfig(
                set_number=i + 1,
                reps_min=set_data.get("reps_min", 8),
                reps_max=set_data.get("reps_max", 12)
            )
            for i, set_data in enumerate(sets_data)
        ]

        # Build ParsedExerciseItem (no alternatives since LLM does the matching)
        return ParsedExerciseItem(
            matched_exercise=matched_exercise,
            original_text=original_text,
            set_configurations=set_configurations,
            rest_seconds=ex_data.get("rest_seconds"),
            notes=ex_data.get("notes"),
            sequence=ex_data.get("sequence", 0),
            alternatives=[],  # LLM handles matching, no alternatives
        )
