from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, condecimal, constr, root_validator


class PackageCreate(BaseModel):
    name: constr(max_length=255)
    weight: condecimal(gt=0)
    content_value: condecimal(gt=0)
    type_id: int

    class Config:
        orm_mode = True


class PackageResponse(BaseModel):
    id: int

    class Config:
        orm_mode = True


class PackageTypeModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class PackageInfo(BaseModel):
    id: int
    name: str
    weight: float
    content_value: float
    delivery_cost: Optional[Union[float, str]] = None
    package_type: PackageTypeModel

    class Config:
        orm_mode = True

    @root_validator(pre=True)
    def set_delivery_cost(cls, values):
        delivery_cost = values.get("delivery_cost")
        if delivery_cost is None:
            values["delivery_cost"] = "Не рассчитано"
        return values


class MyPackages(BaseModel):
    page: int
    page_size: int
    total_items: int
    data: list[PackageInfo]


class UserInfo(BaseModel):
    id: str
    last_access_time: Optional[datetime]

    class Config:
        orm_mode = True


class PackageToCalc(BaseModel):
    id: int
    name: str
    weight: float
    content_value: float
    delivery_cost: float | None

    class Config:
        orm_mode = True
