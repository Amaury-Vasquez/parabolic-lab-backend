from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PGHOST: str
    PGDATABASE: str
    PGUSER: str
    PGPASSWORD: str
    PGSSLMODE: str = "require"

    STACK_AUTH_PROJECT_ID: str
    STACK_AUTH_SECRET_SERVER_KEY: str

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.PGUSER}:{self.PGPASSWORD}@{self.PGHOST}/{self.PGDATABASE}?ssl=require"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
