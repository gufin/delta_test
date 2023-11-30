from dependency_injector import containers, providers

from core.settings import settings
from infrastructure.models import get_sessionmaker
from infrastructure.mysql_repository import DeltaMySQLRepository
from infrastructure.redis_temporary_storage import RedisTemporaryStorage
from services.use_cases.package_cost_calculator import PackageCostCalculator
from services.use_cases.package_service import PackageService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["endpoints"])
    config = providers.Configuration()

    sessionmaker = providers.Factory(get_sessionmaker)

    repository: providers.Provider[DeltaMySQLRepository] = providers.Singleton(
        DeltaMySQLRepository,
        config=config.storage_url,
    )

    redis_repository: providers.Provider[RedisTemporaryStorage] = providers.Singleton(
        RedisTemporaryStorage,
        config=settings,
    )

    cost_calculator: providers.Provider[PackageCostCalculator] = providers.Factory(
        PackageCostCalculator,
        repository=repository,
        temp_storage=redis_repository,
        config=settings,
    )

    package_service: providers.Provider[PackageService] = providers.Factory(PackageService, repository=repository)
