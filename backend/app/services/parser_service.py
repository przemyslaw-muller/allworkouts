"""
Main workout plan parser service orchestrating LLM and exercise matching.
"""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import WorkoutImportLog
from app.schemas.workout_plans import (
    ParsedExerciseItem,
    ParsedExerciseMatch,
    ParsedWorkoutItem,
    ParsedWorkoutPlan,
    WorkoutPlanParseResponse,
)
from app.services.exercise_matcher import ExerciseMatcher
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class ParserService:
    """Service for parsing workout plans from text"""

    def __init__(self, db: Session, user_id: UUID):
        self.db = db
        self.user_id = user_id
        self.matcher = ExerciseMatcher(db)

    async def parse_workout_plan(self, text: str) -> WorkoutPlanParseResponse:
        """
        Parse workout plan text into structured format with exercise matching.

        Args:
            text: Raw workout plan text

        Returns:
            WorkoutPlanParseResponse with parsed data and statistics
        """
        # Step 1: Use LLM to extract structure
        logger.info(f"Parsing workout plan for user {self.user_id}")
        llm_result = await llm_service.parse_workout_text(text)

        # Step 2: Process workouts and match exercises
        parsed_workouts = []
        stats = {"high": 0, "medium": 0, "low": 0, "unmatched": 0}
        total_exercises = 0

        for workout_data in llm_result.get("workouts", []):
            parsed_workout = await self._process_workout(workout_data, stats)
            parsed_workouts.append(parsed_workout)
            total_exercises += len(parsed_workout.exercises)

        # Step 3: Create import log
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

        # Step 4: Build response
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

    async def _process_workout(self, workout_data: dict, stats: dict) -> ParsedWorkoutItem:
        """Process a single workout and its exercises"""
        parsed_exercises = []

        for ex_data in workout_data.get("exercises", []):
            parsed_ex = await self._match_and_build_exercise(ex_data, stats)
            parsed_exercises.append(parsed_ex)

        return ParsedWorkoutItem(
            name=workout_data.get("name", "Workout"),
            day_number=workout_data.get("day_number"),
            order_index=workout_data.get("order_index", 0),
            exercises=parsed_exercises,
        )

    async def _match_and_build_exercise(self, ex_data: dict, stats: dict) -> ParsedExerciseItem:
        """Match exercise and build ParsedExerciseItem"""
        original_text = ex_data.get("original_text", "")

        # Match to database
        best_match, confidence, alternatives = self.matcher.match_exercise(original_text, top_n=5)

        # Build matched exercise
        matched_exercise = None
        if best_match:
            confidence_level = self.matcher.get_confidence_level(confidence)
            matched_exercise = ParsedExerciseMatch(
                exercise_id=best_match.id,
                exercise_name=best_match.name,
                original_text=original_text,
                confidence=confidence,
                confidence_level=confidence_level,
                primary_muscle_groups=best_match.primary_muscle_groups,
                secondary_muscle_groups=best_match.secondary_muscle_groups or [],
            )

            # Update stats
            if confidence_level.value == "high":
                stats["high"] += 1
            elif confidence_level.value == "medium":
                stats["medium"] += 1
            else:
                stats["low"] += 1
        else:
            stats["unmatched"] += 1

        # Build alternatives
        alternative_matches = []
        for alt_ex, alt_score in alternatives[:3]:  # Top 3 alternatives
            alt_level = self.matcher.get_confidence_level(alt_score)
            alternative_matches.append(
                ParsedExerciseMatch(
                    exercise_id=alt_ex.id,
                    exercise_name=alt_ex.name,
                    original_text=original_text,
                    confidence=alt_score,
                    confidence_level=alt_level,
                    primary_muscle_groups=alt_ex.primary_muscle_groups,
                    secondary_muscle_groups=alt_ex.secondary_muscle_groups or [],
                )
            )

        # Build ParsedExerciseItem
        return ParsedExerciseItem(
            matched_exercise=matched_exercise,
            original_text=original_text,
            sets=ex_data.get("sets", 3),
            reps_min=ex_data.get("reps_min", 8),
            reps_max=ex_data.get("reps_max", 12),
            rest_seconds=ex_data.get("rest_seconds"),
            notes=ex_data.get("notes"),
            sequence=ex_data.get("sequence", 0),
            alternatives=alternative_matches,
        )
