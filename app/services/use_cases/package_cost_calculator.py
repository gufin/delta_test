import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx

from core.settings import Settings
from services.use_cases.abstract_repositories import DeltaAbstractRepository
from services.use_cases.abstract_temporary_storage import DeltaAbstractTemporaryStorage

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class PackageCostCalculator:
    def __init__(
        self,
        repository: DeltaAbstractRepository,
        temp_storage: DeltaAbstractTemporaryStorage,
        config: Settings,
    ):
        self.repository = repository
        self.temp_storage = temp_storage
        self.config = config
        logger.info("PackageCostCalculator service has been initialized.")

    @staticmethod
    def get_date_code():
        today = datetime.now()
        if today.weekday() not in [5, 6]:
            date_code = today.strftime("%Y-%m-%d")
        else:
            last_friday = today - timedelta(days=today.weekday() - 4)
            date_code = last_friday.strftime("%Y-%m-%d")
        logger.debug(f"Date code for rate lookup: {date_code}")
        return date_code

    async def get_current_exchange_rate(self, currency: str) -> Optional[float]:
        currency_key = f"{self.get_date_code()}{currency}"
        if rate_raw := self.temp_storage.get_value(currency_key):
            logger.info(f"Exchange rate for {currency} found in temporary storage.")
            return float(rate_raw.decode("utf-8"))

        logger.info(
            f"Retrieving current exchange rate for {currency} from external service."
        )
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.config.currency_data_source)
                response.raise_for_status()
                data = response.json()
                current_date_key = self.get_date_code()
                rate = None
                for currency_code, currency_data in data["Valute"].items():
                    value = currency_data["Value"]
                    key = f"{current_date_key}{currency_code}"
                    self.temp_storage.save_key_value_without_exp(key, value)
                    if currency_code == currency:
                        rate = value
                logger.info(
                    f"Exchange rate for {currency} retrieved and stored in temporary storage."
                )
                return float(rate)
        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred while fetching exchange rate: {e}")
        except Exception as e:
            logger.error(f"An error occurred while fetching exchange rate: {e}")

    async def calculate_delivery_cost(self):
        logger.info("Starting delivery cost calculation.")
        rate = await self.get_current_exchange_rate(self.config.currency_calc_code)
        if rate is None:
            logger.critical(
                "Failed to retrieve the current exchange rate for currency calculation. Aborting calculation."
            )
            return
        packages_to_calc = await self.repository.get_packages_to_calc()
        if not packages_to_calc:
            logger.info("No packages found for delivery cost calculation.")
            return
        for package in packages_to_calc:
            package.delivery_cost = (
                package.weight * 0.5 + package.content_value * 0.01
            ) * rate
            logger.debug(
                f"Calculated delivery cost for package {package.id}: {package.delivery_cost}"
            )
        await self.repository.update_delivery_costs(packages_to_calc)
        logger.info("Delivery cost calculation completed.")
