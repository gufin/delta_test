from abc import ABC, abstractmethod


class DeltaAbstractTemporaryStorage(ABC):
    @abstractmethod
    def save_key_value(self, key: str, value: str, expiration_time: int) -> None:
        pass

    @abstractmethod
    def get_value(self, key: str):
        pass

    @abstractmethod
    def delete_key(self, key: str):
        pass

    @abstractmethod
    def save_key_value_without_exp(self, key: str, value: str) -> None:
        pass
