'''
LLM service for AI-powered workout plan parsing using LiteLLM.
'''

import json
import logging

import litellm
from litellm import completion

from app.config import settings

logger = logging.getLogger(__name__)

# Configure LiteLLM
litellm.set_verbose = settings.debug


class LLMService:
    '''Service for interacting with LLM providers via LiteLLM'''

    def __init__(self):
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens
        self.timeout = settings.llm_timeout

    async def parse_workout_text(self, text: str) -> dict:
        '''
        Parse workout plan text into structured format.

        Args:
            text: Raw workout plan text

        Returns:
            Structured workout plan data

        Raises:
            Exception: If LLM request fails
        '''
        prompt = self._build_parsing_prompt(text)

        try:
            response = await completion(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': self._get_system_prompt()},
                    {'role': 'user', 'content': prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
                api_key=settings.llm_api_key,
            )

            # Extract and parse JSON response
            content = response.choices[0].message.content
            parsed_data = self._extract_json(content)

            logger.info(
                f'Successfully parsed workout plan with {len(parsed_data.get("exercises", []))} exercises'
            )
            return parsed_data

        except Exception as e:
            logger.error(f'LLM parsing failed: {str(e)}')
            raise Exception(f'Failed to parse workout plan: {str(e)}')

    def _get_system_prompt(self) -> str:
        '''System prompt for workout plan parsing'''
        return '''You are a workout plan parser that extracts structured information from text.

Your task is to:
1. Identify the workout plan name and description
2. Extract all exercises with their parameters
3. Parse sets, reps (as min/max range), and rest times
4. Preserve the original exercise names exactly as written
5. Extract any notes or special instructions

Return ONLY valid JSON with this exact structure:
{
  "name": "Plan name (or 'Workout Plan' if not specified)",
  "description": "Plan description (or null)",
  "exercises": [
    {
      "original_text": "Exact exercise name from text",
      "sets": 3,
      "reps_min": 8,
      "reps_max": 12,
      "rest_seconds": 90,
      "notes": "Any special instructions",
      "sequence": 0
    }
  ]
}

Rules:
- If reps is a single number (e.g., "5"), set both min and max to that number
- If reps is a range (e.g., "8-12"), parse as min and max
- If rest time not specified, set to null
- Sequence starts at 0 and increments
- Preserve original exercise name exactly (e.g., "Squat", "Back Squat", "Barbell Squat")
- If no plan name found, use "Workout Plan"
- Notes should capture tempo, RPE, special instructions, etc.

Return ONLY the JSON object, no explanations.'''

    def _build_parsing_prompt(self, text: str) -> str:
        '''Build user prompt with workout text'''
        return f'''Parse this workout plan:

{text}

Return the structured JSON data.'''

    def _extract_json(self, content: str) -> dict:
        '''Extract JSON from LLM response'''
        # Try to find JSON in markdown code blocks
        if '```json' in content:
            start = content.find('```json') + 7
            end = content.find('```', start)
            content = content[start:end].strip()
        elif '```' in content:
            start = content.find('```') + 3
            end = content.find('```', start)
            content = content[start:end].strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f'Failed to parse JSON from LLM response: {content}')
            raise Exception(f'Invalid JSON response from LLM: {str(e)}')


# Singleton instance
llm_service = LLMService()
