from fastapi import APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, selectinload
from sqlalchemy import select, func
from app.db.models import Provider, Procedure
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/providers", tags=["providers"])

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

@router.get("")
async def get_providers(
    drg: str = Query(..., description="DRG code or description"),
    zip: str = Query(..., description="ZIP code for search"),
    radius_km: int = Query(40, description="Search radius in km")
):
    async with async_session() as session:
        stmt = select(Provider).options(selectinload(Provider.procedures)).join(Procedure).where(
            Procedure.ms_drg_definition.ilike(f"%{drg}%"),
            Provider.zip_code == zip
        ).order_by(Procedure.average_covered_charges)
        result = await session.execute(stmt)
        providers = result.scalars().unique().all()
        return [
            {
                "provider_id": p.provider_id,
                "name": p.name,
                "city": p.city,
                "state": p.state,
                "zip_code": p.zip_code,
                "star_rating": round(p.star_rating, 1),
                "procedures": [
                    {
                        "ms_drg_definition": proc.ms_drg_definition,
                        "total_discharges": proc.total_discharges,
                        "average_covered_charges": proc.average_covered_charges,
                        "average_total_payments": proc.average_total_payments,
                        "average_medicare_payments": proc.average_medicare_payments
                    }
                    for proc in p.procedures if drg in proc.ms_drg_definition
                ]
            }
            for p in providers
        ]
