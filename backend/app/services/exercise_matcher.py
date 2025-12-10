'''
Exercise matching service using fuzzy string matching.
'''

import logging
from typing import Optional

from rapidfuzz import fuzz, process
from sqlalchemy.orm import Session

from app.config import settings
from app.enums import ConfidenceLevelEnum
from app.models import Exercise

logger = logging.getLogger(__name__)


class ExerciseMatcher:
    '''Service for matching parsed exercise names to database exercises'''

    def __init__(self, db: Session):
        self.db = db
        self.high_threshold = settings.exercise_match_high_threshold
        self.medium_threshold = settings.exercise_match_threshold
        self.low_threshold = settings.exercise_match_low_threshold

    def match_exercise(
        self, exercise_text: str, top_n: int = 5
    ) -> tuple[Optional[Exercise], float, list[tuple[Exercise, float]]]:
        '''
        Match exercise text to database exercise.

        Args:
            exercise_text: Original exercise name from parsed text
            top_n: Number of alternative matches to return

        Returns:
            Tuple of (best_match, confidence_score, alternatives)
            best_match is None if no match above low threshold
        '''
        # Get all exercises from database
        exercises = self.db.query(Exercise).all()

        if not exercises:
            logger.warning('No exercises in database for matching')
            return None, 0.0, []

        # Create name mapping for fuzzy matching
        exercise_names = {ex.name: ex for ex in exercises}

        # Perform fuzzy matching
        matches = process.extract(
            exercise_text, exercise_names.keys(), scorer=fuzz.token_sort_ratio, limit=top_n
        )

        if not matches:
            return None, 0.0, []

        # Get best match
        best_name, best_score, _ = matches[0]
        best_score = best_score / 100.0  # Normalize to 0-1

        best_exercise = exercise_names[best_name] if best_score >= self.low_threshold else None

        # Get alternatives (excluding best match if it's valid)
        alternatives = []
        start_idx = 1 if best_exercise else 0
        for name, score, _ in matches[start_idx:]:
            normalized_score = score / 100.0
            if normalized_score >= self.low_threshold:
                alternatives.append((exercise_names[name], normalized_score))

        logger.info(f'Matched "{exercise_text}" to "{best_name}" (confidence: {best_score:.2f})')

        return best_exercise, best_score, alternatives

    def get_confidence_level(self, score: float) -> ConfidenceLevelEnum:
        '''Convert numeric score to confidence level enum'''
        if score >= self.high_threshold:
            return ConfidenceLevelEnum.HIGH
        elif score >= self.medium_threshold:
            return ConfidenceLevelEnum.MEDIUM
        else:
            return ConfidenceLevelEnum.LOW
