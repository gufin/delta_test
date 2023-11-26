import asyncio

from core.settings import settings
from infrastructure.mysql_repository import DeltaMySQLRepository
from infrastructure.redis_temporary_storage import RedisTemporaryStorage
from services.use_cases.package_cost_calculator import PackageCostCalculator

my_sql_repository = DeltaMySQLRepository(config=settings.storage_url)
redis_repository = RedisTemporaryStorage(config=settings)
cost_calculator = PackageCostCalculator(my_sql_repository, redis_repository, settings)


async def main():
    while True:
        await cost_calculator.calculate_delivery_cost()
        await asyncio.sleep(300)


if __name__ == "__main__":
    asyncio.run(main())
