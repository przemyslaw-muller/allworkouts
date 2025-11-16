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

    class Config:
        env_file = '.env'
        case_sensitive = False


settings = Settings()
