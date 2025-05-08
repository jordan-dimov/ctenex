import asyncio
from datetime import datetime
from decimal import Decimal

from ctenex.core.db.async_session import (
    DatabaseManager,
    create_custom_engine,
    get_async_session,
)
from ctenex.domain.contracts import ContractCode
from ctenex.domain.entities import Contract, Country
from ctenex.settings.application import get_app_settings


async def init_db():
    db_settings = get_app_settings().db
    engine = create_custom_engine(str(db_settings.uri))

    await DatabaseManager.drop_db(engine=engine)
    await DatabaseManager.setup_db(engine=engine)

    async with get_async_session() as session:
        session.add(
            Country(
                country_id="GB",
                name="United Kingdom",
            )
        )
        await session.commit()

    async with get_async_session() as session:
        session.add(
            Contract(
                contract_id=ContractCode.UK_BL_MAR_25,
                tick_size=Decimal("0.01"),
                contract_size=Decimal("1"),
                location="GB",
                commodity="power",
                delivery_period="hourly",
                start_date=datetime(2025, 1, 1),
                end_date=datetime(2025, 1, 1),
            )
        )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(init_db())
