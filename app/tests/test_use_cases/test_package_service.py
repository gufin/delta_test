import pytest
from starlette import status
from alembic.command import downgrade, upgrade
from alembic.script import Script, ScriptDirectory
from alembic.config import Config

from infrastructure.models import User

pytestmark = pytest.mark.asyncio

def get_revisions():
    # Create Alembic configuration object
    config = Config("alembic.ini")

    # Get directory object with Alembic migrations
    revisions_dir = ScriptDirectory.from_config(config)

    # Get & sort migrations, from first to last
    revisions = list(revisions_dir.walk_revisions("base", "heads"))
    revisions.reverse()
    return revisions


@pytest.mark.parametrize("revision", get_revisions())
async def test_register_package(client, alembic_config, revision: Script, session):

    upgrade(alembic_config, revision.revision)

    new_object = User(id='34447757-bc8f-447d-b7c8-960f7476c436')
    async with session.begin():
        session.add(new_object)
    await session.commit()

    package_data = {
        "name": "Test Package",
        "weight": 1.5,
        "content_value": 100.0,
        "type_id": 1
    }

    response = await client.post(
        url="/packages/register",
        json=package_data,
        cookies={"session_id": '34447757-bc8f-447d-b7c8-960f7476c436'},
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize("cookies, package_data", [
    ({"session_id": '34447757-bc8f-447d-b7c8-960f7476c436'}, {"name": "Test Package", "weight": 1.5, "type_id": 1}),
    (None, {"name": "Test Package", "weight": 1.5, "content_value": 100.0, "type_id": 1})
])
async def test_register_package_variants(client, cookies, package_data):
    response = await client.post(
        url="/packages/register", json=package_data, cookies=cookies or {}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_package_types(client):
    response = await client.get(
        url="/package-types",
        headers={"accept": "application/json"},
    )
    assert response.status_code == status.HTTP_200_OK
    expected_data = [{'id': 1, 'name': 'одежда'}, {'id': 3, 'name': 'разное'}, {'id': 2, 'name': 'электроника'}]
    assert response.json() == expected_data


async def test_my_package(client):
    package_data = {
        "name": "Test Package",
        "weight": 1.5,
        "content_value": 100.0,
        "type_id": 1
    }

    await client.post(
        url="/packages/register",
        json=package_data,
        cookies={"session_id": '34447757-bc8f-447d-b7c8-960f7476c436'},
    )

    expected_data = {
        "page": 1,
        "page_size": 10,
        "total_items": 1,
        "data": [package_data]
    }
    response = await client.get(url="/my-packages", cookies={"session_id": '34447757-bc8f-447d-b7c8-960f7476c436'})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_data
