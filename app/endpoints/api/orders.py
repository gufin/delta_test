from datetime import datetime
from typing import Optional
from uuid import uuid4

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Cookie, Depends, HTTPException
from starlette.responses import JSONResponse

from core.containers import Container
from schemas import (
    CalculationLogAggregatedModel, MyPackages,
    PackageCreate,
    PackageInfo,
    PackageResponse,
    PackageTypeModel,
)
from services.use_cases.package_cost_calculator import PackageCostCalculator
from services.use_cases.package_service import PackageService

router = APIRouter()


@router.get("/start_session")
@inject
async def start_session(session_id: Optional[str] = Cookie(None),
                        package_service: PackageService = Depends(Provide[Container.package_service]),
                        ):
    if not session_id:
        session_id = str(uuid4())
        await package_service.save_session(session_id)
    response = JSONResponse(content={"message": "Session started", "session_id": session_id})
    response.set_cookie(key="session_id", value=session_id)
    return response


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
        session_id: str = Cookie(...),
        package_service: PackageService = Depends(Provide[Container.package_service]),
) -> PackageResponse:
    return await package_service.register_package(package_data, session_id)


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
        session_id: Optional[str] = Cookie(None),
        offset: int = 0,
        limit: int = 10,
        package_service: PackageService = Depends(Provide[Container.package_service]),
) -> MyPackages:
    return await package_service.get_my_packages(
        session_id, type_id, delivery_cost_calculated, offset, limit
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
        session_id: Optional[str] = Cookie(None),
        package_service: PackageService = Depends(Provide[Container.package_service]),
) -> PackageInfo:
    result = await package_service.get_package(session_id, package_id)
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


@router.post(
    "/aggregated_data",
    response_model=list[CalculationLogAggregatedModel],
    summary="Show aggregated data by type by period",
    description="Show aggregated data by type by period",
)
@inject
async def aggregated_data(
        date: datetime,
        cost_calculator: PackageCostCalculator = Depends(
            Provide[Container.cost_calculator]
        ),
):
    return await cost_calculator.get_aggregated_data(date)
