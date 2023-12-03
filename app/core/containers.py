from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.infrastructure.models import get_sessionmaker
from app.infrastructure.mongo_client import MongoClient
from app.infrastructure.mysql_repository import DeltaMySQLRepository
from app.infrastructure.redis_temporary_storage import RedisTemporaryStorage
from app.services.use_cases.package_cost_calculator import PackageCostCalculator
from app.services.use_cases.package_service import PackageService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["app.endpoints"])
    config = providers.Configuration()

    sessionmaker: providers.Factory[AsyncSession] = providers.Factory(get_sessionmaker)

    repository: providers.Provider[DeltaMySQLRepository] = providers.Singleton(
        DeltaMySQLRepository,
        config=config.storage_url,
        sessionmaker=sessionmaker,
    )

    redis_repository: providers.Provider[RedisTemporaryStorage] = providers.Singleton(
        RedisTemporaryStorage,
        config=settings,
    )

    log_repository: providers.Singleton[MongoClient] = providers.Singleton(
        MongoClient,
        config=settings,
    )

    cost_calculator: providers.Provider[PackageCostCalculator] = providers.Factory(
        PackageCostCalculator,
        repository=repository,
        temp_storage=redis_repository,
        log_repository=log_repository,
        config=settings,
    )

    package_service: providers.Provider[PackageService] = providers.Factory(
        PackageService, repository=repository
    )
