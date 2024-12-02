from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.database.core import SessionDep
from app.kafka_logger import log_action

from .models import TariffRead, TariffsIn, TariffUpdate
from .service import delete, get, get_all, update, upload

router = APIRouter()


@router.get("/", response_model=list[TariffRead])
async def get_tariffs(db_session: SessionDep) -> Any:
    """Return all tariffs in the database."""
    return await get_all(db_session=db_session)


@router.get("/{tariff_id}", response_model=TariffRead)
async def get_tariff(db_session: SessionDep, tariff_id: int) -> Any:
    """Retrieve information about a tariff by its ID."""
    tariff = await get(db_session=db_session, tariff_id=tariff_id)
    if not tariff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tariff with id `{tariff_id}` does not exist.",
        )

    return tariff


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_tariffs(db_session: SessionDep, tariffs: TariffsIn) -> dict[str, str]:
    "Create a new tariffs"
    return await upload(db_session=db_session, tariffs=tariffs)


@router.put("/{tariff_id}", response_model=TariffRead)
async def update_tariff(
    db_session: SessionDep, tariff_id: int, tarrif_in: TariffUpdate
) -> Any:
    """Update a tariff."""
    tariff = await get(db_session=db_session, tariff_id=tariff_id)
    if not tariff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tariff with id `{tariff_id}` does not exist.",
        )

    tariff = await update(db_session=db_session, tariff=tariff, tariff_in=tarrif_in)

    await log_action(action="update", tariff_id=tariff_id)

    return tariff


@router.delete("/{tariff_id}", response_model=None)
async def delete_tariff(db_session: SessionDep, tariff_id: int) -> None:
    """Delete a tariff."""
    tariff = await get(db_session=db_session, tariff_id=tariff_id)
    if not tariff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tariff with id `{tariff_id}` does not exist.",
        )
    await delete(db_session=db_session, tariff_id=tariff_id)

    await log_action(action="delete", tariff_id=tariff_id)
