"""
LLM service for AI-powered workout plan parsing using LiteLLM.
"""

import json
import logging

import litellm
from litellm import acompletion

from app.config import settings

logger = logging.getLogger(__name__)

# Configure LiteLLM
litellm.set_verbose = settings.debug


class LLMService:
    """Service for interacting with LLM providers via LiteLLM"""

    def __init__(self):
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens
        self.timeout = settings.llm_timeout

    async def parse_workout_text(self, text: str, exercises: list[dict]) -> dict:
        """
        Parse workout plan text into structured format.

        Args:
            text: Raw workout plan text
            exercises: List of exercise dicts with id, name, and muscle groups

        Returns:
            Structured workout plan data

        Raises:
            Exception: If LLM request fails
        """
        prompt = self._build_parsing_prompt(text, exercises)

        try:
            response = await acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
                api_key=settings.llm_api_key,
            )

            # Extract and parse JSON response
            content = response.choices[0].message.content
            parsed_data = self._extract_json(content)

            workouts = parsed_data.get("workouts", [])
            total_exercises = sum(len(w.get("exercises", [])) for w in workouts)
            logger.info(
                f"Successfully parsed workout plan with {len(workouts)} workouts and {total_exercises} exercises"
            )
            return parsed_data

        except Exception as e:
            logger.error(f"LLM parsing failed: {str(e)}")
            raise Exception(f"Failed to parse workout plan: {str(e)}")

    def _get_system_prompt(self) -> str:
        """System prompt for workout plan parsing"""
        return """You are a workout plan parser that extracts structured information from text and matches exercises to a database.

Your task is to:
1. Identify the workout plan name and description
2. Group exercises into workouts (days/sessions)
3. Extract all exercises with their parameters
4. Match each exercise name to the closest exercise from the provided exercise database
5. Parse sets, reps (as min/max range), and rest times
6. Extract any notes or special instructions

Return ONLY valid JSON with this exact structure:
{
  "name": "Plan name (or 'Workout Plan' if not specified)",
  "description": "Plan description (or null)",
  "workouts": [
    {
      "name": "Day 1" or "Push Day" or workout name from text,
      "day_number": 1,
      "order_index": 0,
      "exercises": [
        {
          "exercise_id": "uuid-from-exercise-database",
          "original_text": "Exact exercise name from text",
          "confidence": 0.95,
          "sets": [
            {"reps_min": 10, "reps_max": 15},
            {"reps_min": 8, "reps_max": 12},
            {"reps_min": 6, "reps_max": 9}
          ],
          "rest_seconds": 90,
          "notes": "Any special instructions",
          "sequence": 0
        }
      ]
    }
  ]
}

Rules:
- Group exercises into workouts based on day labels, headers, or logical groupings
- If no workout groupings are clear, create a single workout named "Workout 1"
- Workout day_number starts at 1, order_index starts at 0
- For sets: return an array with one object per set, each containing reps_min and reps_max
- If text shows different reps per set (e.g., "Set 1: 10-15, Set 2: 6-9"), parse each set separately
- If text shows same reps for all sets (e.g., "3x8-12"), create array with 3 identical objects: [{"reps_min": 8, "reps_max": 12}, ...]
- If reps is a single number (e.g., "5"), set both min and max to that number
- If reps is a range (e.g., "8-12"), parse as min and max
- If rest time not specified, set to null
- Exercise sequence starts at 0 and increments within each workout
- For exercise matching: find the best match from the provided exercise list based on name similarity
- Use the exercise_id from the database for the matched exercise
- Provide a confidence score (0.0-1.0) for each match:
  * 0.90-1.0: Exact or very close match (e.g., "Squat" -> "Squat", "Bench Press" -> "Bench Press")
  * 0.80-0.89: Good match with minor variations (e.g., "Back Squat" -> "Squat", "Barbell Bench" -> "Bench Press")
  * 0.70-0.79: Reasonable match but notable differences (e.g., "Leg Press" -> "Squat", "DB Bench" -> "Bench Press")
  * Below 0.70: Poor match - set exercise_id to null instead
- If no good match exists (confidence < 0.70), set exercise_id to null and confidence to 0.0
- Preserve original exercise name in original_text field
- If no plan name found, use "Workout Plan"
- Notes should capture tempo, RPE, special instructions, etc.

Return ONLY the JSON object, no explanations."""

    def _build_parsing_prompt(self, text: str, exercises: list[dict]) -> str:
        """Build user prompt with workout text and exercise database"""
        # Format exercises for the prompt
        exercise_list = "\n".join(
            f"- {ex['name']} (ID: {ex['id']}) - Primary: {', '.join(ex['primary_muscle_groups'])}"
            for ex in exercises
        )
        
        return f"""Available exercises in database:
{exercise_list}

Parse this workout plan and match exercises to the database:

{text}

Return the structured JSON data with exercise_id for each matched exercise."""

    def _extract_json(self, content: str) -> dict:
        """Extract JSON from LLM response"""
        # Try to find JSON in markdown code blocks
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            content = content[start:end].strip()
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            content = content[start:end].strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {content}")
            raise Exception(f"Invalid JSON response from LLM: {str(e)}")


# Singleton instance
llm_service = LLMService()
