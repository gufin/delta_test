from dependency_injector import containers, providers

from core.settings import settings
from infrastructure.mysql_repository import DeltaMySQLRepository
from infrastructure.redis_temporary_storage import RedisTemporaryStorage
from services.use_cases.package_service import PackageService
from services.use_cases.package_cost_calculator import PackageCostCalculator


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["endpoints"])
    config = providers.Configuration()

    repository = providers.Singleton(
        DeltaMySQLRepository,
        config=config.storage_url,
    )

    redis_repository = providers.Singleton(
        RedisTemporaryStorage,
        config=settings,
    )

    cost_calculator = providers.Factory(
        PackageCostCalculator,
        repository=repository,
        temp_storage=redis_repository,
        config=settings,
    )

    package_service = providers.Factory(PackageService, repository=repository)
