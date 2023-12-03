from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from schemas import (
    CalculationLogAggregatedModel,
    CalculationLogModel,
    MyPackages,
    PackageCreate,
    PackageInfo,
    PackageResponse,
    PackageToCalc,
    PackageTypeModel,
    UserInfo,
)


class DeltaAbstractRepository(ABC):
    @abstractmethod
    async def register_package(
        self, package_data: PackageCreate, user_id: str
    ) -> PackageResponse:
        pass

    @abstractmethod
    async def get_package_types(self) -> list[PackageTypeModel]:
        pass

    @abstractmethod
    async def get_my_packages(
        self,
        user_id: int,
        type_id: Optional[int],
        delivery_cost_calculated: Optional[bool],
        offset: int,
        limit: int,
    ) -> MyPackages:
        pass

    @abstractmethod
    async def get_package(self, user_id: str, package_id: int) -> PackageInfo:
        pass

    @abstractmethod
    async def get_or_create_user(self, user_id: str) -> UserInfo:
        pass

    @abstractmethod
    async def get_packages_to_calc(self) -> list[PackageToCalc]:
        pass

    @abstractmethod
    async def update_delivery_costs(
        self, packages_to_update: list[PackageToCalc]
    ) -> None:
        pass

    @abstractmethod
    async def assign_package(self, package_id: int, company_id: int) -> None:
        pass


class AbstractCalculationLogRepository(ABC):
    @abstractmethod
    async def add_calc_data(self, calc_log_models: list[CalculationLogModel]) -> None:
        pass

    @abstractmethod
    async def get_aggregated_data(
        self, date: datetime
    ) -> list[CalculationLogAggregatedModel]:
        pass


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
