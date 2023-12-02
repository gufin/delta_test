import asyncio

from core.settings import settings
from infrastructure.models import get_sessionmaker
from infrastructure.mongo_client import MongoClient
from infrastructure.mysql_repository import DeltaMySQLRepository
from infrastructure.redis_temporary_storage import RedisTemporaryStorage
from services.use_cases.package_cost_calculator import PackageCostCalculator

sessionmaker = get_sessionmaker()
my_sql_repository = DeltaMySQLRepository(config=settings.storage_url, sessionmaker=sessionmaker)
redis_repository = RedisTemporaryStorage(config=settings)
log_repository = MongoClient(config=settings)
cost_calculator = PackageCostCalculator(my_sql_repository, redis_repository, log_repository, settings)


async def main():
    await cost_calculator.calculate_delivery_cost()


if __name__ == "__main__":
    asyncio.run(main())
