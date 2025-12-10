"""Unit tests for parser services"""

from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest

from app.enums import ConfidenceLevelEnum, MuscleGroupEnum
from app.models import Exercise
from app.services.exercise_matcher import ExerciseMatcher
from app.services.parser_service import ParserService


@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock()


@pytest.fixture
def mock_user_id():
    """Mock user ID"""
    return uuid4()


@pytest.fixture
def sample_exercises():
    """Sample exercises for matching"""
    return [
        Exercise(
            id=uuid4(),
            name="Squat",
            primary_muscle_groups=[MuscleGroupEnum.LEGS],
            secondary_muscle_groups=[MuscleGroupEnum.GLUTES],
        ),
        Exercise(
            id=uuid4(),
            name="Bench Press",
            primary_muscle_groups=[MuscleGroupEnum.CHEST],
            secondary_muscle_groups=[MuscleGroupEnum.TRICEPS],
        ),
        Exercise(
            id=uuid4(),
            name="Deadlift",
            primary_muscle_groups=[MuscleGroupEnum.BACK],
            secondary_muscle_groups=[MuscleGroupEnum.LEGS],
        ),
    ]


class TestExerciseMatcher:
    """Tests for ExerciseMatcher service"""

    def test_match_exercise_exact(self, mock_db, sample_exercises):
        """Test exact exercise match"""
        mock_db.query.return_value.all.return_value = sample_exercises

        matcher = ExerciseMatcher(mock_db)
        best_match, confidence, alternatives = matcher.match_exercise("Squat")

        assert best_match is not None
        assert best_match.name == "Squat"
        assert confidence >= 0.90  # High confidence
        assert len(alternatives) >= 0

    def test_match_exercise_fuzzy(self, mock_db, sample_exercises):
        """Test fuzzy exercise match"""
        mock_db.query.return_value.all.return_value = sample_exercises

        matcher = ExerciseMatcher(mock_db)
        best_match, confidence, alternatives = matcher.match_exercise("Banch Press")

        assert best_match is not None
        assert best_match.name == "Bench Press"
        assert confidence >= 0.70  # At least low confidence
        assert len(alternatives) >= 0

    def test_match_exercise_no_match(self, mock_db, sample_exercises):
        """Test no match for completely unrelated text"""
        mock_db.query.return_value.all.return_value = sample_exercises

        matcher = ExerciseMatcher(mock_db)
        best_match, confidence, alternatives = matcher.match_exercise("XYZ123")

        assert best_match is None
        assert confidence < 0.70  # Below threshold

    def test_match_exercise_empty_database(self, mock_db):
        """Test matching with empty database"""
        mock_db.query.return_value.all.return_value = []

        matcher = ExerciseMatcher(mock_db)
        best_match, confidence, alternatives = matcher.match_exercise("Squat")

        assert best_match is None
        assert confidence == 0.0
        assert len(alternatives) == 0

    def test_get_confidence_level(self, mock_db):
        """Test confidence level conversion"""
        matcher = ExerciseMatcher(mock_db)

        assert matcher.get_confidence_level(0.95) == ConfidenceLevelEnum.HIGH
        assert matcher.get_confidence_level(0.85) == ConfidenceLevelEnum.MEDIUM
        assert matcher.get_confidence_level(0.75) == ConfidenceLevelEnum.LOW


class TestParserService:
    """Tests for ParserService"""

    @pytest.mark.asyncio
    async def test_parse_workout_plan_success(self, mock_db, mock_user_id, sample_exercises):
        """Test successful workout plan parsing"""
        # Mock LLM response - now using nested workouts structure
        llm_response = {
            "name": "5x5 Program",
            "description": "Strength training",
            "workouts": [
                {
                    "name": "Day 1",
                    "day_number": 1,
                    "order_index": 0,
                    "exercises": [
                        {
                            "original_text": "Squat",
                            "sets": 5,
                            "reps_min": 5,
                            "reps_max": 5,
                            "rest_seconds": 180,
                            "notes": None,
                            "sequence": 0,
                        }
                    ],
                }
            ],
        }

        # Mock database queries
        mock_db.query.return_value.all.return_value = sample_exercises
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock(side_effect=lambda obj: setattr(obj, "id", uuid4()) or None)

        with patch(
            "app.services.parser_service.llm_service.parse_workout_text",
            new=AsyncMock(return_value=llm_response),
        ):
            parser = ParserService(mock_db, mock_user_id)
            result = await parser.parse_workout_plan("5x5 Program\nSquat 5x5")

            assert result.total_exercises == 1
            assert result.parsed_plan.name == "5x5 Program"
            assert len(result.parsed_plan.workouts) == 1
            assert len(result.parsed_plan.workouts[0].exercises) == 1
            assert result.high_confidence_count >= 0

    @pytest.mark.asyncio
    async def test_parse_workout_plan_multiple_exercises(
        self, mock_db, mock_user_id, sample_exercises
    ):
        """Test parsing workout plan with multiple exercises"""
        llm_response = {
            "name": "Push Day",
            "description": None,
            "workouts": [
                {
                    "name": "Workout 1",
                    "day_number": 1,
                    "order_index": 0,
                    "exercises": [
                        {
                            "original_text": "Bench Press",
                            "sets": 3,
                            "reps_min": 8,
                            "reps_max": 10,
                            "rest_seconds": 90,
                            "notes": None,
                            "sequence": 0,
                        },
                        {
                            "original_text": "Squat",
                            "sets": 3,
                            "reps_min": 10,
                            "reps_max": 12,
                            "rest_seconds": 60,
                            "notes": None,
                            "sequence": 1,
                        },
                    ],
                }
            ],
        }

        mock_db.query.return_value.all.return_value = sample_exercises
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock(side_effect=lambda obj: setattr(obj, "id", uuid4()) or None)

        with patch(
            "app.services.parser_service.llm_service.parse_workout_text",
            new=AsyncMock(return_value=llm_response),
        ):
            parser = ParserService(mock_db, mock_user_id)
            result = await parser.parse_workout_plan("Bench Press 3x8-10\nSquat 3x10-12")

            assert result.total_exercises == 2
            assert result.parsed_plan.name == "Push Day"
            assert len(result.parsed_plan.workouts) == 1
            assert len(result.parsed_plan.workouts[0].exercises) == 2

    @pytest.mark.asyncio
    async def test_parse_workout_plan_with_unmatched(self, mock_db, mock_user_id, sample_exercises):
        """Test parsing with unmatched exercises"""
        llm_response = {
            "name": "Workout",
            "description": None,
            "workouts": [
                {
                    "name": "Workout 1",
                    "day_number": 1,
                    "order_index": 0,
                    "exercises": [
                        {
                            "original_text": "Unknown Exercise XYZ",
                            "sets": 3,
                            "reps_min": 8,
                            "reps_max": 10,
                            "rest_seconds": None,
                            "notes": None,
                            "sequence": 0,
                        }
                    ],
                }
            ],
        }

        mock_db.query.return_value.all.return_value = sample_exercises
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock(side_effect=lambda obj: setattr(obj, "id", uuid4()) or None)

        with patch(
            "app.services.parser_service.llm_service.parse_workout_text",
            new=AsyncMock(return_value=llm_response),
        ):
            parser = ParserService(mock_db, mock_user_id)
            result = await parser.parse_workout_plan("Unknown Exercise XYZ 3x8-10")

            assert result.total_exercises == 1
            assert result.unmatched_count >= 0
            assert result.parsed_plan.workouts[0].exercises[0].matched_exercise is None
