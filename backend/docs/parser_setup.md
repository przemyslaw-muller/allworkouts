# Workout Plan Parser - Setup Guide

## Overview

This guide covers the setup and configuration of the AI-powered workout plan parser using LiteLLM.

## Prerequisites

- Python 3.9+
- Poetry for dependency management
- PostgreSQL database
- API key for LLM provider (OpenAI, Anthropic, Azure, etc.)

## Installation

### 1. Install Dependencies

Add to `pyproject.toml`:

```toml
[tool.poetry.dependencies]
litellm = "^1.17.0"
rapidfuzz = "^3.5.0"
```

Install via Poetry:

```bash
cd backend
poetry install
```

### 2. Environment Configuration

Create or update `.env` file:

```bash
# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
LLM_API_KEY=sk-your-api-key-here
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4000
LLM_TIMEOUT=60

# Parser Configuration
EXERCISE_MATCH_THRESHOLD=0.80
EXERCISE_MATCH_HIGH_THRESHOLD=0.90
EXERCISE_MATCH_LOW_THRESHOLD=0.70
```

### 3. Update Config

The `app/config.py` should include:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... existing settings ...
    
    # LLM Configuration
    llm_provider: str = 'openai'
    llm_model: str = 'gpt-4-turbo-preview'
    llm_api_key: str = ''
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4000
    llm_timeout: int = 60
    
    # Parser Configuration
    exercise_match_threshold: float = 0.80
    exercise_match_high_threshold: float = 0.90
    exercise_match_low_threshold: float = 0.70
    
    class Config:
        env_file = '.env'
        case_sensitive = False
```

## LLM Provider Setup

### OpenAI (Recommended for MVP)

1. Get API key from https://platform.openai.com/api-keys
2. Set in `.env`:
   ```bash
   LLM_PROVIDER=openai
   LLM_MODEL=gpt-4-turbo-preview
   LLM_API_KEY=sk-...
   ```

**Recommended Models:**
- `gpt-4-turbo-preview` - Best accuracy, higher cost
- `gpt-3.5-turbo` - Good accuracy, lower cost (for testing)

**Pricing (as of 2024):**
- GPT-4 Turbo: $0.01/1K input tokens, $0.03/1K output tokens
- GPT-3.5 Turbo: $0.0005/1K input tokens, $0.0015/1K output tokens

**Estimated Cost per Parse:**
- Typical workout plan: ~500 input tokens, ~300 output tokens
- GPT-4 Turbo: ~$0.014 per parse
- GPT-3.5 Turbo: ~$0.0007 per parse

### Anthropic Claude

1. Get API key from https://console.anthropic.com/
2. Set in `.env`:
   ```bash
   LLM_PROVIDER=anthropic
   LLM_MODEL=claude-3-sonnet-20240229
   LLM_API_KEY=sk-ant-...
   ```

**Recommended Models:**
- `claude-3-opus-20240229` - Highest accuracy
- `claude-3-sonnet-20240229` - Good balance
- `claude-3-haiku-20240307` - Fast and cheap

### Azure OpenAI

1. Set up Azure OpenAI resource
2. Deploy a model
3. Set in `.env`:
   ```bash
   LLM_PROVIDER=azure
   LLM_MODEL=azure/<deployment-name>
   LLM_API_KEY=your-azure-key
   AZURE_API_BASE=https://your-resource.openai.azure.com
   AZURE_API_VERSION=2024-02-15-preview
   ```

### Local LLM (Ollama)

For development/testing without API costs:

1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull mistral`
3. Set in `.env`:
   ```bash
   LLM_PROVIDER=ollama
   LLM_MODEL=ollama/mistral
   LLM_API_KEY=not-needed
   ```

**Note:** Local models may have lower accuracy than cloud models.

## Database Setup

Ensure the `workout_import_log` table exists. If not, create migration:

```bash
cd backend
docker-compose exec backend alembic revision -m "add workout import log table"
```

The migration should create:
```python
def upgrade():
    op.create_table(
        'workout_import_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('workout_plan_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workout_plan.id'), nullable=True),
        sa.Column('raw_text', sa.Text, nullable=False),
        sa.Column('parsed_exercises', postgresql.JSONB, nullable=True),
        sa.Column('confidence_scores', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    # Add indexes
    op.create_index('idx_workout_import_log_user_id', 'workout_import_log', ['user_id'])
    op.create_index('idx_workout_import_log_workout_plan_id', 'workout_import_log', ['workout_plan_id'])
    op.create_index('idx_workout_import_log_created_at', 'workout_import_log', ['user_id', 'created_at'])
```

Run migration:
```bash
docker-compose exec backend alembic upgrade head
```

## Verification

### 1. Test LLM Connection

Create `test_llm.py`:

```python
import asyncio
from app.config import settings
from app.services.llm_service import llm_service

async def test():
    text = """
    Day 1: Upper Body
    Bench Press: 3x8
    Rows: 3x10
    """
    result = await llm_service.parse_workout_text(text)
    print(result)

asyncio.run(test())
```

Run:
```bash
docker-compose exec backend python test_llm.py
```

Expected output: JSON with parsed exercises

### 2. Test Exercise Matching

Create `test_matcher.py`:

```python
from app.database import SessionLocal
from app.services.exercise_matcher import ExerciseMatcher

db = SessionLocal()
matcher = ExerciseMatcher(db)

exercise, confidence, alternatives = matcher.match_exercise("Bench Press")
print(f"Match: {exercise.name if exercise else 'None'}")
print(f"Confidence: {confidence:.2f}")
print(f"Alternatives: {len(alternatives)}")
```

Run:
```bash
docker-compose exec backend python test_matcher.py
```

### 3. Test API Endpoint

Using curl or httpx:

```bash
curl -X POST http://localhost:8000/api/v1/workout-plans/parse \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Bench Press: 3x8\nSquat: 5x5\nDeadlift: 1x5"
  }'
```

## Monitoring

### LiteLLM Logging

Enable verbose logging for debugging:

```python
# In app/services/llm_service.py
litellm.set_verbose = True  # Set to False in production
```

### Application Logging

Configure logging in `app/main.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set LiteLLM log level
logging.getLogger('litellm').setLevel(logging.INFO)
```

### Metrics to Track

1. **Parse Success Rate**
   - Track successful vs failed parses
   - Monitor by user and over time

2. **Confidence Distribution**
   - Track high/medium/low/unmatched counts
   - Aim for >80% high confidence

3. **Parse Duration**
   - Track time from request to response
   - Alert if >15 seconds

4. **LLM Token Usage**
   - Monitor tokens per request
   - Track costs

5. **Exercise Match Quality**
   - Track manual corrections after parsing
   - Identify commonly mismatched exercises

## Performance Tuning

### Optimize LLM Settings

**For Speed:**
```bash
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=2000
```

**For Accuracy:**
```bash
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4000
```

**For Cost:**
```bash
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=2000
```

### Optimize Exercise Matching

Cache exercise list in memory:

```python
# In app/services/exercise_matcher.py
class ExerciseMatcher:
    _exercise_cache = None
    _cache_timestamp = None
    
    def __init__(self, db: Session):
        self.db = db
        self._load_exercises()
    
    def _load_exercises(self):
        # Load all exercises once and cache
        if not self._exercise_cache or self._cache_expired():
            self._exercise_cache = self.db.query(Exercise).all()
            self._cache_timestamp = datetime.utcnow()
```

### Batch Processing

For bulk imports, implement queuing:

```python
# Use Celery or RQ for async processing
@celery_app.task
def parse_workout_plan_async(user_id: str, text: str):
    db = SessionLocal()
    parser = ParserService(db, UUID(user_id))
    result = await parser.parse_workout_plan(text)
    return result
```

## Security Considerations

### API Key Security

1. **Never commit API keys**
   - Use `.env` files (git ignored)
   - Use environment variables in production

2. **Rotate keys regularly**
   - Set up key rotation schedule
   - Monitor for unauthorized usage

3. **Use secret management**
   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault

### Rate Limiting

Implement at multiple levels:

1. **Application Level**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   
   @router.post('/parse')
   @limiter.limit('10/hour')
   async def parse_workout_plan(...):
       ...
   ```

2. **User Level**
   - Track usage in database
   - Implement tiered limits (free vs paid)

3. **LLM Provider Level**
   - Set spending limits in provider dashboard
   - Configure alerts for high usage

### Data Privacy

1. **Sanitize Input**
   - Remove PII before logging
   - Don't log full workout text in production

2. **Secure Storage**
   - Encrypt `raw_text` in database
   - Set retention policy for import logs

3. **User Consent**
   - Inform users that AI processes their data
   - Provide opt-out mechanism

## Troubleshooting

### Common Issues

**"Import litellm could not be resolved"**
- Run `poetry install` to install dependencies
- Verify `litellm` is in `pyproject.toml`

**"LLM API key not set"**
- Check `.env` file exists
- Verify `LLM_API_KEY` is set
- Restart application after changes

**"Rate limit exceeded" (from LLM provider)**
- Check provider dashboard for limits
- Implement request queuing
- Consider upgrading provider tier

**"Exercise matching always returns low confidence"**
- Check exercise database is populated
- Review exercise names for consistency
- Adjust threshold settings

**"Parse endpoint times out"**
- Increase `LLM_TIMEOUT` setting
- Check LLM provider status
- Consider using faster model

### Debug Mode

Enable detailed debugging:

```bash
# In .env
DEBUG=true
LLM_VERBOSE=true
```

View logs:
```bash
docker-compose logs -f backend
```

## Production Checklist

- [ ] Set appropriate LLM model for production
- [ ] Configure rate limiting
- [ ] Set up monitoring and alerting
- [ ] Enable error tracking (Sentry, etc.)
- [ ] Set spending limits with LLM provider
- [ ] Configure log retention
- [ ] Set up backup for import logs
- [ ] Document incident response procedure
- [ ] Test failover scenarios
- [ ] Configure auto-scaling if needed

## Cost Estimation

### Monthly Cost Examples

**Low Usage (100 users, 2 parses/user/month):**
- 200 parses × $0.014 = $2.80/month (GPT-4 Turbo)
- 200 parses × $0.0007 = $0.14/month (GPT-3.5 Turbo)

**Medium Usage (1,000 users, 5 parses/user/month):**
- 5,000 parses × $0.014 = $70/month (GPT-4 Turbo)
- 5,000 parses × $0.0007 = $3.50/month (GPT-3.5 Turbo)

**High Usage (10,000 users, 10 parses/user/month):**
- 100,000 parses × $0.014 = $1,400/month (GPT-4 Turbo)
- 100,000 parses × $0.0007 = $70/month (GPT-3.5 Turbo)

**Recommendation:** Start with GPT-3.5 Turbo, upgrade to GPT-4 if accuracy is insufficient.

## Support

For issues or questions:
1. Check this documentation
2. Review LiteLLM docs: https://docs.litellm.ai/
3. Check provider status pages
4. Contact development team
