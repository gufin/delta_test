from datetime import datetime

import pytest
from starlette import status

pytestmark = pytest.mark.asyncio


async def test_register_package(client):
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
        "data": [{
            "name": "Test Package",
            "weight": 1.5,
            "content_value": 100.0,
            "id": 1,
            "delivery_cost": "Не рассчитано",
            "package_type": {
                "id": 1,
                "name": "одежда"
            }
        }]
    }
    response = await client.get(url="/my-packages", cookies={"session_id": '34447757-bc8f-447d-b7c8-960f7476c436'})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_data

    expected_data = {
        "page": 1,
        "page_size": 10,
        "total_items": 0,
        "data": []
    }

    response = await client.get(url="/my-packages", cookies={"session_id": '35cc6b42-55fe-43f0-a8a2-a8ac7105616f'})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_data


async def test_get_package(client):
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

    response = await client.get(
        url="/packages/1",
        cookies={"session_id": '34447757-bc8f-447d-b7c8-960f7476c436'},
    )
    assert response.status_code == status.HTTP_200_OK
    expected_data = {
        'id': 1,
        'name': 'Test Package',
        'weight': 1.5,
        'content_value': 100.0,
        'delivery_cost': 'Не рассчитано',
        'package_type': {
            'id': 1,
            'name': 'одежда'
        }
    }
    assert response.json() == expected_data


async def test_get_package_different_session(client):
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

    response = await client.get(
        url="/packages/1",
        cookies={"session_id": '35cc6b42-55fe-43f0-a8a2-a8ac7105616f'},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_calculation(client):
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

    await client.post(
        url="/run_calculation",
    )

    response = await client.get(
        url="/packages/1",
        cookies={"session_id": '34447757-bc8f-447d-b7c8-960f7476c436'},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['delivery_cost'] > 0


async def test_aggregated_data(client):
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

    await client.post(
        url="/run_calculation",
    )
    current_date = datetime.now().isoformat()
    response = await client.get(url="/aggregated_data", params={"date": current_date})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0
