from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PGHOST: str
    PGDATABASE: str
    PGUSER: str
    PGPASSWORD: str
    PGSSLMODE: str = "require"

    STACK_AUTH_PROJECT_ID: str
    STACK_AUTH_SECRET_SERVER_KEY: str

    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.PGUSER}:{self.PGPASSWORD}@{self.PGHOST}/{self.PGDATABASE}?ssl=require"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
