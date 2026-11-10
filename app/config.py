from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ESG Mining Intelligence System"
    host: str = "0.0.0.0"
    port: int = 3000
    database_url: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
