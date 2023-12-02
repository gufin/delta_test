from pydantic import BaseSettings


class Settings(BaseSettings):
    project_name: str = 'delta_test_task'
    db_host: str = '127.0.0.1'
    db_port: int = 3306
    mysql_db: str = 'mysql'
    mysql_user: str = 'root'
    mysql_password: str = 'password'
    currency_data_source: str = "https://www.cbr-xml-daily.ru/daily_json.js"
    currency_calc_code: str = "USD"
    redis_host: str = '127.0.0.1'
    redis_port: int = 6380
    mongo_host: str = '127.0.0.1'
    mongo_port: int = 27017

    @property
    def storage_url(self):
        return (
            f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.db_host}:{self.db_port}/{self.mysql_db}"
        )

    @property
    def storage_url_sync(self):
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.db_host}:{self.db_port}/{self.mysql_db}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
