import redis

from services.use_cases.abstract_repositories import DeltaAbstractTemporaryStorage


class RedisTemporaryStorage(DeltaAbstractTemporaryStorage):
    def __init__(self, config):
        self.config = config
        self.redis_client = redis.StrictRedis(
            host=self.config.redis_host, port=self.config.redis_port, db=0
        )

    def save_key_value(self, key: str, value: str, expiration_time: int) -> None:
        self.redis_client.setex(key, expiration_time, value)

    def save_key_value_without_exp(self, key: str, value: str) -> None:
        self.redis_client.set(key, value, keepttl=True)

    def get_value(self, key: str) -> None:
        return self.redis_client.get(key)

    def delete_key(self, key: str) -> None:
        self.redis_client.delete(key)
