import logging
from datetime import datetime, timedelta

from motor.motor_asyncio import AsyncIOMotorClient as Mongo
from pymongo.errors import BulkWriteError

from app.core.settings import Settings
from app.schemas import CalculationLogAggregatedModel, CalculationLogModel
from app.services.use_cases.abstract_repositories import AbstractCalculationLogRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("package_service")


class MongoClient(AbstractCalculationLogRepository):
    def __init__(self, config: Settings):
        self.config = config
        self.mongo = Mongo(config.mongo_host, config.mongo_port)
        self.database = self.mongo.get_database("test")
        self.deliveries = self.database.get_collection("deliveries")

    async def add_calc_data(self, calc_log_models: list[CalculationLogModel]) -> None:
        try:
            update_result = await self.deliveries.insert_many(
                [model.dict() for model in calc_log_models]
            )
            if update_result.acknowledged:
                logger.info("Calculation data added to mongo")
        except BulkWriteError as e:
            logger.error(f"Error while adding calc data to mongo: {e}")
            raise

    async def get_aggregated_data(
        self, date: datetime
    ) -> list[CalculationLogAggregatedModel]:
        index_info = await self.deliveries.index_information()
        if "package_type_id_1" not in index_info or "date_1" not in index_info:
            await self.deliveries.create_index("package_type_id")
            await self.deliveries.create_index("date")
        formatted_date = date.strftime("%Y-%m-%d")
        pipeline = [
            {
                "$match": {
                    "date": {
                        "$gte": datetime.strptime(formatted_date, "%Y-%m-%d"),
                        "$lt": datetime.strptime(formatted_date, "%Y-%m-%d")
                        + timedelta(days=1),
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "package_type_id": "$package_type_id",
                        "date": {
                            "$dateToString": {"format": "%Y-%m-%d", "date": "$date"}
                        },
                    },
                    "delivery_cost_sum": {"$sum": "$delivery_cost"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "package_type_id": "$_id.package_type_id",
                    "delivery_cost_sum": 1,
                    "date": "$_id.date",
                }
            },
        ]

        cursor = self.deliveries.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        return [CalculationLogAggregatedModel(**result) for result in results]
