from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    '''Application settings loaded from environment variables'''

    # Database
    database_url: str = 'postgresql://user:pass@db:5432/allworkouts'

    # JWT
    jwt_secret_key: str = 'your-secret-key-change-in-production'
    jwt_algorithm: str = 'HS256'
    jwt_expiration_minutes: int = 60 * 24 * 7  # 7 days

    # Application
    app_name: str = 'AllWorkouts API'
    debug: bool = False

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


settings = Settings()
