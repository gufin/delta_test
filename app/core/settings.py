from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    project_name: str = Field(..., env="PROJECT_NAME")
    storage_url: str
    currency_data_source: str = "https://www.cbr-xml-daily.ru/daily_json.js"
    currency_calc_code: str = "USD"
    redis_host: str
    redis_port: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
