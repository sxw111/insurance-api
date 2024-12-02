from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .models import Tariff, TariffsIn, TariffUpdate


async def get(*, db_session: AsyncSession, tariff_id: int):
    """Returns a tariff based on the given id."""
    result = await db_session.execute(select(Tariff).where(Tariff.id == tariff_id))

    return result.scalars().first()


async def get_all(*, db_session: AsyncSession):
    """Return all tariffs."""
    result = await db_session.execute(select(Tariff))

    return result.scalars().all()


async def get_actual_tariff(
    *, db_session: AsyncSession, cargo_type: str, date_in: date
):
    """
    Retrieves the most recent tariff for the
    specified cargo type and date from the database.
    """
    query = (
        select(Tariff)
        .filter(Tariff.cargo_type == cargo_type, Tariff.validity_date <= date_in)
        .order_by(Tariff.validity_date.desc())
    )

    result = await db_session.execute(query)

    return result.scalars().first()


async def upload(*, db_session: AsyncSession, tariffs: TariffsIn):
    "Uploads and save a list of tariffs."
    for validity_date, items in tariffs.root.items():
        for item in items:
            tariff = Tariff(
                validity_date=validity_date, cargo_type=item.cargo_type, rate=item.rate
            )
            db_session.add(tariff)

    await db_session.commit()
    return {"msg": "Tariffs uploaded successfully!"}


async def update(*, db_session: AsyncSession, tariff: Tariff, tariff_in: TariffUpdate):
    """Updates a tariff."""
    tariff_data = tariff.dict()
    update_data = tariff_in.model_dump(exclude_unset=True)
    for field in tariff_data:
        if field in update_data:
            setattr(tariff, field, update_data[field])

    await db_session.commit()
    await db_session.refresh(tariff)

    return tariff


async def delete(*, db_session: AsyncSession, tariff_id: int):
    """Deletes an existing tariff."""
    result = await db_session.execute(select(Tariff).where(Tariff.id == tariff_id))
    tariff = result.scalars().first()
    await db_session.delete(tariff)
    await db_session.commit()
