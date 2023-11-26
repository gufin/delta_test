from typing import Optional

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException, Request

from core.containers import Container
from models import (
    MyPackages,
    PackageCreate,
    PackageInfo,
    PackageResponse,
    PackageTypeModel,
)
from services.use_cases.package_cost_calculator import PackageCostCalculator
from services.use_cases.package_service import PackageService

router = APIRouter()


def get_user_id(request: Request) -> int:
    user_id = request.headers.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=400, detail="User ID is missing in the headers")
    try:
        return int(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid User ID format") from e


@router.post(
    "/packages/register",
    response_model=PackageResponse,
    summary="Register a new package",
    description=(
        "Creates a new package with the given details and associates it with the user ID provided "
        "in the header."
    ),
)
@inject
async def register_package(
    package_data: PackageCreate,
    user_id: int = Depends(get_user_id),
    package_service: PackageService = Depends(Provide[Container.package_service]),
) -> PackageResponse:
    return await package_service.register_package(package_data, user_id)


@router.get(
    "/package-types",
    response_model=list[PackageTypeModel],
    summary="Get all package types",
    description="Retrieves a list of all available package types from the database.",
)
@inject
async def get_package_types(
    package_service: PackageService = Depends(Provide[Container.package_service]),
) -> list[PackageTypeModel]:
    return await package_service.get_package_types()


@router.get(
    "/my-packages",
    response_model=MyPackages,
    summary="Get user's packages",
    description=(
        "Retrieves packages associated with the user, with optional filters for type and delivery "
        "cost calculation status."
    ),
)
@inject
async def get_my_packages(
    type_id: Optional[int] = None,
    delivery_cost_calculated: Optional[bool] = None,
    user_id: int = Depends(get_user_id),
    offset: int = 0,
    limit: int = 10,
    package_service: PackageService = Depends(Provide[Container.package_service]),
) -> MyPackages:
    return await package_service.get_my_packages(
        user_id, type_id, delivery_cost_calculated, offset, limit
    )


@router.get(
    "/packages/{package_id}",
    response_model=PackageInfo,
    summary="Get a specific package",
    description="Retrieves detailed information about a specific package by its ID for the user.",
)
@inject
async def get_package(
    package_id: int,
    user_id: int = Depends(get_user_id),
    package_service: PackageService = Depends(Provide[Container.package_service]),
) -> PackageInfo:
    result = await package_service.get_package(user_id, package_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Package not found")
    return result


@router.post(
    "/run_calculation",
    summary="Run delivery cost calculation",
    description="Triggers the delivery cost calculation process for all packages.",
)
@inject
async def run_calculation(
    cost_calculator: PackageCostCalculator = Depends(
        Provide[Container.cost_calculator]
    ),
):
    await cost_calculator.calculate_delivery_cost()
    return {"message": "Calculation is complete."}
