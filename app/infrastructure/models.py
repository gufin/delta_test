from sqlalchemy import (
    BigInteger,
    CHAR,
    Column,
    DateTime,
    Float,
    ForeignKey,
    func,
    Integer,
    String,
)
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from core.settings import settings

engine = create_async_engine(settings.storage_url, echo=False)
Base = declarative_base()
metadata = Base.metadata


def get_sessionmaker():
    return async_sessionmaker(bind=engine, expire_on_commit=False)


class User(Base):
    __tablename__ = "users"

    id = Column(CHAR(36), primary_key=True)
    last_access_time = Column(DateTime(timezone=True), server_default=func.now())

    packages = relationship("Package", back_populates="user")


class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    weight = Column(Float, nullable=False)
    content_value = Column(Float, nullable=False)
    delivery_cost = Column(Float)
    type_id = Column(Integer, ForeignKey("package_types.id"), nullable=False)
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, index=True, nullable=True)
    version = Column(BigInteger, nullable=False, default=0)

    user = relationship("User", back_populates="packages")
    type = relationship("PackageType", back_populates="packages")


class PackageType(Base):
    __tablename__ = "package_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)

    packages = relationship("Package", back_populates="type")
