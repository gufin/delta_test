from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import joinedload

from infrastructure.models import (
    engine,
    Package,
    PackageType,
    User,
)
from schemas import (
    MyPackages,
    PackageCreate,
    PackageInfo,
    PackageResponse,
    PackageToCalc,
    PackageTypeModel,
    UserInfo,
)
from services.use_cases.abstract_repositories import DeltaAbstractRepository


class DeltaMySQLRepository(DeltaAbstractRepository):
    def __init__(self, *, config: dict, sessionmaker: async_sessionmaker[AsyncSession]):
        self.config = config
        self.sessionmaker = sessionmaker

    async def register_package(
        self, package_data: PackageCreate, user_id: str
    ) -> PackageResponse:
        new_package = Package(
            name=package_data.name,
            weight=package_data.weight,
            content_value=package_data.content_value,
            type_id=package_data.type_id,
            user_id=user_id,
        )

        async with self.sessionmaker() as session:
            async with session.begin():
                session.add(new_package)
                await session.flush()
                package_response = PackageResponse(id=str(new_package.id))
            await session.commit()
        return package_response

    async def get_package_types(self) -> list[PackageTypeModel]:
        async with self.sessionmaker() as session:
            async with session.begin():
                package_types = await session.execute(select(PackageType))
                package_types_list = package_types.scalars().all()

                return [
                    PackageTypeModel.from_orm(package_type)
                    for package_type in package_types_list
                ]

    async def get_my_packages(
        self,
        user_id: str,
        type_id: Optional[int],
        delivery_cost_calculated: Optional[bool],
        offset: int,
        limit: int,
    ) -> MyPackages:
        async with self.sessionmaker() as session:
            conditions = [Package.user_id == user_id]
            if type_id is not None:
                conditions.append(Package.type_id == type_id)
            if delivery_cost_calculated is not None:
                if delivery_cost_calculated:
                    conditions.append(Package.delivery_cost.isnot(None))
                else:
                    conditions.append(Package.delivery_cost.is_(None))

            packages_query = (
                select(Package)
                .options(joinedload(Package.type))
                .where(and_(*conditions))
                .offset(offset)
                .limit(limit)
            )
            packages_result = await session.execute(packages_query)
            packages = packages_result.scalars().all()

            total_count_query = (
                select(func.count()).select_from(Package).where(and_(*conditions))
            )
            total_count_result = await session.execute(total_count_query)
            total_items = total_count_result.scalar_one()

            package_infos = [
                PackageInfo(
                    id=package.id,
                    name=package.name,
                    weight=package.weight,
                    delivery_cost=package.delivery_cost,
                    content_value=package.content_value,
                    package_type=PackageTypeModel.from_orm(package.type),
                )
                for package in packages
            ]

            return MyPackages(
                page=offset // limit + 1,
                page_size=limit,
                total_items=total_items,
                data=package_infos,
            )

    async def get_package(self, user_id: str, package_id: int) -> Optional[PackageInfo]:
        async with self.sessionmaker() as session:
            conditions = [Package.user_id == user_id, Package.id == package_id]
            package_query = select(Package).where(and_(*conditions))
            package_result = await session.execute(package_query)
            package = package_result.scalar()

            if not package:
                return None

            package_type_query = select(PackageType).where(
                PackageType.id == package.type_id
            )
            package_type_result = await session.execute(package_type_query)
            package_type = package_type_result.scalar()

            return PackageInfo(
                id=package.id,
                name=package.name,
                weight=package.weight,
                content_value=package.content_value,
                delivery_cost=package.delivery_cost,
                package_type=PackageTypeModel.from_orm(package_type),
            )

    async def get_or_create_user(self, user_id: str) -> UserInfo:
        async with self.sessionmaker() as session:
            user_query = select(User).where(User.id == user_id)
            user_result = await session.execute(user_query)
            user = user_result.scalar()

            if not user:
                user = User(id=user_id)
                session.add(user)
                await session.commit()
                await session.refresh(user)

            return UserInfo.from_orm(user)

    async def get_packages_to_calc(self) -> list[PackageToCalc]:
        async with self.sessionmaker() as session:
            packages_query = select(Package).where(Package.delivery_cost.is_(None))
            packages_result = await session.execute(packages_query)
            packages = packages_result.scalars().all()

            return [
                PackageToCalc(
                    id=package.id,
                    package_type_id=package.type_id,
                    name=package.name,
                    weight=package.weight,
                    delivery_cost=package.delivery_cost,
                    content_value=package.content_value,
                )
                for package in packages
            ]

    async def update_delivery_costs(
        self, packages_to_update: list[PackageToCalc]
    ) -> None:
        async with self.sessionmaker() as session:
            async with session.begin():
                for package_calc in packages_to_update:
                    query = select(Package).where(Package.id == package_calc.id)
                    result = await session.execute(query)
                    if package := result.scalar_one_or_none():
                        package.delivery_cost = package_calc.delivery_cost
                await session.commit()
