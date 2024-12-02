from datetime import date
from decimal import Decimal

from pydantic import Field, RootModel
from sqlalchemy.orm import Mapped, mapped_column

from app.database.core import Base
from app.models import PydanticBase


class Tariff(Base):
    __tablename__ = "tariffs"

    id: Mapped[int] = mapped_column(primary_key=True)
    cargo_type: Mapped[str] = mapped_column(nullable=False)
    rate: Mapped[Decimal] = mapped_column(nullable=False)
    validity_date: Mapped[date] = mapped_column(nullable=False)


class TariffBase(PydanticBase):
    cargo_type: str
    rate: Decimal


class TariffRead(TariffBase):
    id: int
    validity_date: date


class TariffUpdate(TariffBase):
    validity_date: date


class TariffsIn(RootModel):
    root: dict[date, list[TariffBase]] = Field(  # type: ignore
        ...,
        example={
            "2020-11-12": [
                {"cargo_type": "Glass", "rate": 0.04},
                {"cargo_type": "Other", "rate": 0.01},
            ],
            "2020-07-01": [
                {"cargo_type": "Glass", "rate": 0.03},
                {"cargo_type": "Other", "rate": 0.015},
            ],
        },
    )
