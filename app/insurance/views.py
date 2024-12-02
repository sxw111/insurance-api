from datetime import date
from decimal import Decimal

from fastapi import APIRouter, HTTPException, status

from app.database.core import SessionDep
from app.tariff.service import get_actual_tariff

from .utils import calculate_insurance

router = APIRouter()


@router.post("/calculate")
async def calculate(
    db_session: SessionDep, cargo_type: str, declared_value: Decimal, date_in: date
) -> dict[str, Decimal]:
    "Calculates the cost of insurance at the current rate."
    tariff = await get_actual_tariff(
        db_session=db_session, cargo_type=cargo_type, date_in=date_in
    )

    if not tariff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tariff not found"
        )

    insurance_cost = calculate_insurance(
        declared_value=declared_value, tariff_rate=tariff.rate
    )

    return {"insurance_cost": insurance_cost}
