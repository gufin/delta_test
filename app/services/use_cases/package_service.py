import logging
from typing import Optional

from schemas import (
    MyPackages,
    PackageCreate,
    PackageInfo,
    PackageResponse,
    PackageTypeModel,
)
from services.use_cases.abstract_repositories import DeltaAbstractRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("package_service")


class PackageService:
    def __init__(self, repository: DeltaAbstractRepository):
        self.repository = repository

    async def register_package(
        self, package_data: PackageCreate, user_id: str
    ) -> PackageResponse:
        logger.info("Registering package for user_id: %s", user_id)
        response = await self.repository.register_package(package_data, user_id)
        logger.info("Package registered with id: %s", response.id)
        return response

    async def get_package_types(self) -> list[PackageTypeModel]:
        logger.info("Retrieving package types")
        package_types = await self.repository.get_package_types()
        logger.info("Package types retrieved: %s", package_types)
        return package_types

    async def get_my_packages(
        self,
        user_id: str,
        type_id: Optional[int],
        delivery_cost_calculated: Optional[bool],
        offset: int,
        limit: int,
    ) -> MyPackages:
        logger.info("Retrieving packages for user_id: %s", user_id)
        my_packages = await self.repository.get_my_packages(
            user_id, type_id, delivery_cost_calculated, offset, limit
        )
        logger.info("Packages retrieved for user_id: %s", user_id)
        return my_packages

    async def get_package(self, user_id: str, package_id: int) -> PackageInfo:
        logger.info(
            "Retrieving package with id: %s for user_id: %s", package_id, user_id
        )
        package_info = await self.repository.get_package(user_id, package_id)
        if package_info:
            logger.info("Package retrieved with id: %s", package_info.id)
        else:
            logger.info("Cant find package: %s for user %s", package_id, user_id)
        return package_info

    async def save_session(self, session_id: str) -> None:
        await self.repository.get_or_create_user(session_id)
