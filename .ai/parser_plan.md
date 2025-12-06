# Workout Plan Parser Implementation Plan

## Overview
This plan outlines the implementation of an AI-powered workout plan parser using LiteLLM as the LLM gateway. The parser will accept plain text workout plans and convert them into structured data with exercise matching, confidence scoring, and equipment validation.

## 1. Dependencies & Configuration

### 1.1 Add Dependencies
**File**: `backend/pyproject.toml`

Add the following dependencies:
```toml
litellm = "^1.17.0"  # LLM gateway with multi-provider support
rapidfuzz = "^3.5.0"  # Fast fuzzy string matching for exercise names
python-dotenv = "^1.0.0"  # Already may be included, ensure present
```

### 1.2 Environment Configuration
**File**: `backend/app/config.py`

Add LLM-related settings:
```python
# LLM Configuration
llm_provider: str = 'openai'  # openai, anthropic, azure, etc.
llm_model: str = 'gpt-4-turbo-preview'
llm_api_key: str = ''  # Set via env var
llm_temperature: float = 0.1  # Low temp for consistent parsing
llm_max_tokens: int = 4000
llm_timeout: int = 60  # Request timeout in seconds

# Parser Configuration
exercise_match_threshold: float = 0.80  # 80% confidence threshold
exercise_match_high_threshold: float = 0.90  # High confidence threshold
exercise_match_low_threshold: float = 0.70  # Low confidence threshold
```

### 1.3 Environment Variables
**File**: `backend/.env.example`

Add:
```bash
# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
LLM_API_KEY=your-api-key-here
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4000
LLM_TIMEOUT=60

# Parser Configuration
EXERCISE_MATCH_THRESHOLD=0.80
EXERCISE_MATCH_HIGH_THRESHOLD=0.90
EXERCISE_MATCH_LOW_THRESHOLD=0.70
```

## 2. Schema Definitions

### 2.1 Parser Request/Response Schemas
**File**: `backend/app/schemas/workout_plans.py`

Add new schemas:

```python
class ParsedExerciseMatch(BaseModel):
    '''Matched exercise from database with confidence'''
    
    exercise_id: UUID
    exercise_name: str
    original_text: str
    confidence: float
    confidence_level: ConfidenceLevelEnum
    primary_muscle_groups: list[MuscleGroupEnum]
    secondary_muscle_groups: list[MuscleGroupEnum]
    
    class Config:
        from_attributes = True


class ParsedExerciseItem(BaseModel):
    '''Single parsed exercise with matching info'''
    
    matched_exercise: Optional[ParsedExerciseMatch] = None
    original_text: str
    sets: int
    reps_min: int
    reps_max: int
    rest_seconds: Optional[int] = None
    notes: Optional[str] = None
    sequence: int
    # Alternatives if confidence is low
    alternatives: list[ParsedExerciseMatch] = []


class WorkoutPlanParseRequest(BaseModel):
    '''Request for parsing workout plan text'''
    
    text: str
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        if len(v.strip()) < 10:
            raise ValueError('Text must be at least 10 characters')
        if len(v) > 50000:
            raise ValueError('Text must be less than 50,000 characters')
        return v.strip()


class ParsedWorkoutPlan(BaseModel):
    '''Parsed workout plan structure from text'''
    
    name: str
    description: Optional[str] = None
    exercises: list[ParsedExerciseItem]
    raw_text: str
    import_log_id: UUID  # Reference to import log


class WorkoutPlanParseResponse(BaseModel):
    '''Response from parse endpoint'''
    
    parsed_plan: ParsedWorkoutPlan
    total_exercises: int
    high_confidence_count: int
    medium_confidence_count: int
    low_confidence_count: int
    unmatched_count: int


class WorkoutPlanFromParsedRequest(BaseModel):
    '''Create workout plan from parsed data (Step 2)'''
    
    import_log_id: UUID
    name: str
    description: Optional[str] = None
    exercises: list[WorkoutExerciseCreateItem]
    
    @field_validator('exercises')
    @classmethod
    def validate_exercises(cls, v: list) -> list:
        if len(v) < 1:
            raise ValueError('Workout plan must have at least 1 exercise')
        return v
```

## 3. Core Parser Service

### 3.1 LLM Service Module
**File**: `backend/app/services/__init__.py` (create directory)
```python
# Empty file to make services a package
```

**File**: `backend/app/services/llm_service.py`

```python
'''
LLM service for AI-powered workout plan parsing using LiteLLM.
'''

import json
import logging
from typing import Optional

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
                    {
                        'role': 'system',
                        'content': self._get_system_prompt()
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
                api_key=settings.llm_api_key,
            )
            
            # Extract and parse JSON response
            content = response.choices[0].message.content
            parsed_data = self._extract_json(content)
            
            logger.info(f'Successfully parsed workout plan with {len(parsed_data.get("exercises", []))} exercises')
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
```

### 3.2 Exercise Matching Service
**File**: `backend/app/services/exercise_matcher.py`

```python
'''
Exercise matching service using fuzzy string matching.
'''

import logging
from typing import Optional
from uuid import UUID

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
        self,
        exercise_text: str,
        top_n: int = 5
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
            exercise_text,
            exercise_names.keys(),
            scorer=fuzz.token_sort_ratio,
            limit=top_n
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
        
        logger.info(
            f'Matched "{exercise_text}" to "{best_name}" '
            f'(confidence: {best_score:.2f})'
        )
        
        return best_exercise, best_score, alternatives
    
    def get_confidence_level(self, score: float) -> ConfidenceLevelEnum:
        '''Convert numeric score to confidence level enum'''
        if score >= self.high_threshold:
            return ConfidenceLevelEnum.HIGH
        elif score >= self.medium_threshold:
            return ConfidenceLevelEnum.MEDIUM
        else:
            return ConfidenceLevelEnum.LOW
```

### 3.3 Parser Service (Orchestrator)
**File**: `backend/app/services/parser_service.py`

```python
'''
Main workout plan parser service orchestrating LLM and exercise matching.
'''

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.models import Exercise, WorkoutImportLog
from app.schemas.workout_plans import (
    ParsedExerciseItem,
    ParsedExerciseMatch,
    ParsedWorkoutPlan,
    WorkoutPlanParseResponse,
)
from app.services.exercise_matcher import ExerciseMatcher
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class ParserService:
    '''Service for parsing workout plans from text'''
    
    def __init__(self, db: Session, user_id: UUID):
        self.db = db
        self.user_id = user_id
        self.matcher = ExerciseMatcher(db)
    
    async def parse_workout_plan(self, text: str) -> WorkoutPlanParseResponse:
        '''
        Parse workout plan text into structured format with exercise matching.
        
        Args:
            text: Raw workout plan text
            
        Returns:
            WorkoutPlanParseResponse with parsed data and statistics
        '''
        # Step 1: Use LLM to extract structure
        logger.info(f'Parsing workout plan for user {self.user_id}')
        llm_result = await llm_service.parse_workout_text(text)
        
        # Step 2: Match exercises to database
        parsed_exercises = []
        stats = {
            'high': 0,
            'medium': 0,
            'low': 0,
            'unmatched': 0
        }
        
        for ex_data in llm_result.get('exercises', []):
            parsed_ex = await self._match_and_build_exercise(ex_data, stats)
            parsed_exercises.append(parsed_ex)
        
        # Step 3: Create import log
        import_log = WorkoutImportLog(
            user_id=self.user_id,
            workout_plan_id=None,  # Will be set when plan is created
            raw_text=text,
            parsed_exercises=llm_result.get('exercises', []),
            confidence_scores={
                'high_confidence': stats['high'],
                'medium_confidence': stats['medium'],
                'low_confidence': stats['low'],
                'unmatched': stats['unmatched']
            },
            created_at=datetime.utcnow()
        )
        self.db.add(import_log)
        self.db.commit()
        self.db.refresh(import_log)
        
        logger.info(
            f'Parsed {len(parsed_exercises)} exercises: '
            f'{stats["high"]} high, {stats["medium"]} medium, '
            f'{stats["low"]} low, {stats["unmatched"]} unmatched'
        )
        
        # Step 4: Build response
        parsed_plan = ParsedWorkoutPlan(
            name=llm_result.get('name', 'Workout Plan'),
            description=llm_result.get('description'),
            exercises=parsed_exercises,
            raw_text=text,
            import_log_id=import_log.id
        )
        
        return WorkoutPlanParseResponse(
            parsed_plan=parsed_plan,
            total_exercises=len(parsed_exercises),
            high_confidence_count=stats['high'],
            medium_confidence_count=stats['medium'],
            low_confidence_count=stats['low'],
            unmatched_count=stats['unmatched']
        )
    
    async def _match_and_build_exercise(
        self,
        ex_data: dict,
        stats: dict
    ) -> ParsedExerciseItem:
        '''Match exercise and build ParsedExerciseItem'''
        original_text = ex_data.get('original_text', '')
        
        # Match to database
        best_match, confidence, alternatives = self.matcher.match_exercise(
            original_text,
            top_n=5
        )
        
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
                secondary_muscle_groups=best_match.secondary_muscle_groups or []
            )
            
            # Update stats
            if confidence_level.value == 'high':
                stats['high'] += 1
            elif confidence_level.value == 'medium':
                stats['medium'] += 1
            else:
                stats['low'] += 1
        else:
            stats['unmatched'] += 1
        
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
                    secondary_muscle_groups=alt_ex.secondary_muscle_groups or []
                )
            )
        
        # Build ParsedExerciseItem
        return ParsedExerciseItem(
            matched_exercise=matched_exercise,
            original_text=original_text,
            sets=ex_data.get('sets', 3),
            reps_min=ex_data.get('reps_min', 8),
            reps_max=ex_data.get('reps_max', 12),
            rest_seconds=ex_data.get('rest_seconds'),
            notes=ex_data.get('notes'),
            sequence=ex_data.get('sequence', 0),
            alternatives=alternative_matches
        )
```

## 4. API Endpoints

### 4.1 Parse Endpoint
**File**: `backend/app/api/workout_plans.py`

Add new endpoint:

```python
from app.services.parser_service import ParserService
from app.schemas.workout_plans import (
    WorkoutPlanParseRequest,
    WorkoutPlanParseResponse,
    WorkoutPlanFromParsedRequest
)

@router.post(
    '/parse',
    response_model=APIResponse[WorkoutPlanParseResponse],
    status_code=status.HTTP_200_OK,
)
async def parse_workout_plan(
    request: WorkoutPlanParseRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    Parse workout plan from text using AI (Step 1 of import).
    
    This endpoint:
    1. Uses LLM to extract workout structure
    2. Matches exercises to database with confidence scores
    3. Returns parsed data for user review
    4. Creates import log for audit trail
    
    Rate limit: 10 requests per hour per user
    '''
    try:
        parser = ParserService(db, user_id)
        result = await parser.parse_workout_plan(request.text)
        return APIResponse.success_response(result)
    except Exception as e:
        logger.error(f'Parse failed for user {user_id}: {str(e)}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to parse workout plan: {str(e)}'
        )


@router.post(
    '/from-parsed',
    response_model=APIResponse[WorkoutPlanCreateResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_workout_plan_from_parsed(
    request: WorkoutPlanFromParsedRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    Create workout plan from parsed data (Step 2 of import).
    
    This endpoint takes the import_log_id from the parse response
    and creates the actual workout plan with user-confirmed exercises.
    '''
    # Verify import log exists and belongs to user
    import_log = (
        db.query(WorkoutImportLog)
        .filter(
            WorkoutImportLog.id == request.import_log_id,
            WorkoutImportLog.user_id == user_id
        )
        .first()
    )
    
    if not import_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Import log not found'
        )
    
    if import_log.workout_plan_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Workout plan already created from this import'
        )
    
    # Validate all exercise IDs exist
    exercise_ids = [ex.exercise_id for ex in request.exercises]
    existing_exercises = (
        db.query(Exercise.id).filter(Exercise.id.in_(exercise_ids)).all()
    )
    existing_ids = {ex.id for ex in existing_exercises}
    missing_ids = set(exercise_ids) - existing_ids
    
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Exercise IDs not found: {[str(id) for id in missing_ids]}'
        )
    
    # Create workout plan
    plan = WorkoutPlan(
        user_id=user_id,
        name=request.name,
        description=request.description
    )
    db.add(plan)
    db.flush()
    
    # Create workout exercises
    for ex in request.exercises:
        workout_exercise = WorkoutExercise(
            workout_plan_id=plan.id,
            exercise_id=ex.exercise_id,
            sequence=ex.sequence,
            sets=ex.sets,
            reps_min=ex.reps_min,
            reps_max=ex.reps_max,
            rest_time_seconds=ex.rest_time_seconds,
            confidence_level=ex.confidence_level
        )
        db.add(workout_exercise)
    
    # Link import log to created plan
    import_log.workout_plan_id = plan.id
    
    db.commit()
    db.refresh(plan)
    
    logger.info(f'Created workout plan {plan.id} from import log {import_log.id}')
    
    return APIResponse.success_response(
        WorkoutPlanCreateResponse(
            id=plan.id,
            name=plan.name,
            created_at=plan.created_at
        )
    )
```

## 5. Testing

### 5.1 Unit Tests
**File**: `backend/tests/test_parser_service.py`

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from app.services.parser_service import ParserService
from app.services.exercise_matcher import ExerciseMatcher
from app.enums import ConfidenceLevelEnum, MuscleGroupEnum

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def mock_user_id():
    return uuid4()

@pytest.mark.asyncio
async def test_parse_simple_workout_plan(mock_db, mock_user_id):
    '''Test parsing a simple workout plan'''
    # Mock LLM response
    llm_response = {
        'name': '5x5 Program',
        'description': 'Strength training',
        'exercises': [
            {
                'original_text': 'Squat',
                'sets': 5,
                'reps_min': 5,
                'reps_max': 5,
                'rest_seconds': 180,
                'notes': None,
                'sequence': 0
            }
        ]
    }
    
    with patch('app.services.llm_service.llm_service.parse_workout_text', return_value=llm_response):
        parser = ParserService(mock_db, mock_user_id)
        # Add more test implementation
```

### 5.2 Integration Tests
**File**: `backend/tests/test_workout_plan_parser_api.py`

```python
import pytest
from fastapi.testclient import TestClient

def test_parse_endpoint_success(client, auth_headers, db_session):
    '''Test successful workout plan parsing'''
    request_data = {
        'text': '''Day 1: Upper Body
        
Bench Press: 3x8-10
Rows: 3x10-12
Overhead Press: 3x8-10 (rest 90s)'''
    }
    
    response = client.post(
        '/api/v1/workout-plans/parse',
        json=request_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()['data']
    assert 'parsed_plan' in data
    assert len(data['parsed_plan']['exercises']) == 3

def test_parse_endpoint_invalid_text(client, auth_headers):
    '''Test parsing with invalid text'''
    request_data = {'text': 'abc'}  # Too short
    
    response = client.post(
        '/api/v1/workout-plans/parse',
        json=request_data,
        headers=auth_headers
    )
    
    assert response.status_code == 422  # Validation error
```

## 6. Error Handling & Logging

### 6.1 Custom Exceptions
**File**: `backend/app/exceptions.py` (create)

```python
class ParserException(Exception):
    '''Base exception for parser errors'''
    pass

class LLMException(ParserException):
    '''Exception for LLM-related errors'''
    pass

class ExerciseMatchException(ParserException):
    '''Exception for exercise matching errors'''
    pass
```

### 6.2 Logging Configuration
Add structured logging for parser operations:
- LLM request/response times
- Exercise matching confidence distribution
- Parse success/failure rates
- Token usage tracking

## 7. Rate Limiting

**File**: `backend/app/api/workout_plans.py`

Add rate limiting decorator (using slowapi or similar):
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post('/parse')
@limiter.limit('10/hour')  # 10 requests per hour
async def parse_workout_plan(...):
    ...
```

## 8. Documentation

### 8.1 API Documentation
Add comprehensive docstrings and OpenAPI examples to all endpoints.

### 8.2 Usage Guide
**File**: `backend/docs/parser_usage.md` (create)

Document:
- Supported text formats
- Parsing accuracy expectations
- Confidence level interpretations
- Troubleshooting common issues

## 9. Deployment Considerations

### 9.1 Environment Setup
- Set LLM API keys securely
- Configure appropriate model (balance cost vs accuracy)
- Set timeout values based on expected text length
- Monitor token usage and costs

### 9.2 Performance
- Cache exercise database in memory for matching
- Implement request queuing for LLM calls
- Add monitoring for parsing duration
- Consider async processing for large texts

## 10. Implementation Steps Summary

1. **Phase 1: Setup** (Day 1)
   - Add dependencies to pyproject.toml
   - Update config.py with LLM settings
   - Create services directory structure

2. **Phase 2: Core Services** (Days 2-3)
   - Implement LLMService with LiteLLM
   - Implement ExerciseMatcher with fuzzy matching
   - Implement ParserService orchestrator
   - Add comprehensive error handling

3. **Phase 3: API Integration** (Day 4)
   - Add schemas to workout_plans.py
   - Implement /parse endpoint
   - Implement /from-parsed endpoint
   - Add rate limiting

4. **Phase 4: Testing** (Day 5)
   - Write unit tests for all services
   - Write integration tests for API
   - Manual testing with various text formats
   - Load testing for LLM calls

5. **Phase 5: Documentation & Deployment** (Day 6)
   - Complete API documentation
   - Write usage guide
   - Environment setup guide
   - Deploy and monitor

## 11. Success Metrics

- **Parsing Accuracy**: 80%+ high confidence matches
- **API Response Time**: < 10 seconds for typical plans
- **Error Rate**: < 5% parser failures
- **User Acceptance**: < 20% user modifications to parsed data

## 12. Future Enhancements

- Image OCR support for screenshot parsing
- Multi-language support
- Custom exercise creation during import
- Training history-based exercise suggestions
- Bulk import of multiple plans
