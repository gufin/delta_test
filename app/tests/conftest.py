# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
from os import environ
from uuid import uuid4

import pytest
import pytest_asyncio
from alembic.command import upgrade
from alembic.config import Config
from dependency_injector import providers
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy_utils import create_database, database_exists, drop_database

from app.core.containers import Container
from app.core.settings import settings
from app.infrastructure.models import User
from app.main import get_application


@pytest.fixture
def temp_postgres() -> str:
    """
    Создает временную БД для запуска теста.
    """

    tmp_name = ".".join([uuid4().hex, "pytest"])
    environ["mysql_db"] = tmp_name
    settings.mysql_db = tmp_name
    tmp_url = settings.storage_url_sync

    if not database_exists(tmp_url):
        create_database(tmp_url)

    try:
        yield settings.storage_url
    finally:
        drop_database(tmp_url)


@pytest.fixture
def alembic_config(temp_postgres):
    config = Config("app/alembic.ini")
    config.set_main_option("sqlalchemy.url", settings.storage_url_sync)
    return config


@pytest_asyncio.fixture(scope="function")
async def engine_async(temp_postgres) -> AsyncEngine:
    engine = create_async_engine(temp_postgres, future=True, echo=True)
    yield engine
    await engine.dispose()


@pytest.fixture
def session_factory_async(engine_async) -> async_sessionmaker:
    return async_sessionmaker(
        engine_async, class_=AsyncSession, expire_on_commit=False
    )  # noqa: W0621


@pytest_asyncio.fixture
async def session(session_factory_async) -> AsyncSession:
    async with session_factory_async() as session:  # noqa: W0621
        yield session  # noqa: W0621


def run_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    upgrade(cfg, "head")


@pytest_asyncio.fixture
async def migrated_postgres(engine_async: AsyncEngine, alembic_config):
    async with engine_async.begin() as conn:
        await conn.run_sync(run_upgrade, alembic_config)


@pytest.fixture
def container(session_factory_async):
    test_container = Container()
    test_container.config.from_pydantic(settings)

    def get_temp_sessionmaker():
        return session_factory_async

    test_container.sessionmaker.override(providers.Factory(get_temp_sessionmaker))

    yield test_container
    test_container.unwire()  # pylint: disable=no-member


@pytest_asyncio.fixture(autouse=True)
async def user_data_sample(migrated_postgres, session):
    """
    Create courier sample for tests.
    """
    new_object_1 = User(id='34447757-bc8f-447d-b7c8-960f7476c436')
    new_object_2 = User(id='35cc6b42-55fe-43f0-a8a2-a8ac7105616f')
    async with session.begin():
        session.add(new_object_1)
        session.add(new_object_2)
    await session.commit()



@pytest.fixture
def client(migrated_postgres, session_factory_async):
    app = get_application()

    def get_temp_sessionmaker():
        return session_factory_async

    app.container.sessionmaker.override(
        providers.Factory(get_temp_sessionmaker)
    )  # pylint: disable=no-member
    yield AsyncClient(app=app, base_url="http://test")
    app.container.unwire()  # pylint: disable=no-member
