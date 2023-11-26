from abc import ABC, abstractmethod
from typing import Optional

from models import (
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
        self, package_data: PackageCreate, user_id: int
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
    async def get_package(self, user_id: int, package_id: int) -> PackageInfo:
        pass

    @abstractmethod
    async def get_or_create_user(self, user_id: int) -> UserInfo:
        pass

    @abstractmethod
    async def get_packages_to_calc(self) -> list[PackageToCalc]:
        pass

    @abstractmethod
    async def update_delivery_costs(
        self, packages_to_update: list[PackageToCalc]
    ) -> None:
        pass
