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
    drg: str = Query(..., description="DRG code or description (substring/fuzzy/fulltext match supported)"),
    zip: str = Query(..., description="ZIP code for search"),
    radius_km: int = Query(40, description="Search radius in km"),
    match_type: str = Query("substring", description="Match type: substring, fuzzy, or fulltext")
):
    SIMILARITY_THRESHOLD = 0.1
    async with async_session() as session:
        if match_type == "fuzzy":
            drg_filter = func.similarity(Procedure.ms_drg_definition, drg) > SIMILARITY_THRESHOLD
            order_by = [func.similarity(Procedure.ms_drg_definition, drg).desc(), Procedure.average_covered_charges]
        elif match_type == "fulltext":
            # Full-text search (optional, fallback to substring if not implemented)
            drg_filter = func.to_tsvector('english', Procedure.ms_drg_definition).match(drg)
            order_by = [Procedure.average_covered_charges]
        else:  # substring
            drg_filter = Procedure.ms_drg_definition.ilike(f"%{drg}%")
            order_by = [Procedure.average_covered_charges]
        stmt = (
            select(Provider, Procedure)
            .join(Procedure)
            .where(
                Provider.zip_code == zip,
                drg_filter
            )
            .order_by(*order_by)
        )
        result = await session.execute(stmt)
        rows = result.all()
        # Group only matching procedures by provider
        providers_dict = {}
        for provider, procedure in rows:
            if provider.provider_id not in providers_dict:
                providers_dict[provider.provider_id] = {
                    "provider_id": provider.provider_id,
                    "name": provider.name,
                    "city": provider.city,
                    "state": provider.state,
                    "zip_code": provider.zip_code,
                    "star_rating": round(provider.star_rating, 1),
                    "procedures": []
                }
            # Only append the procedure from the filtered SQL result
            providers_dict[provider.provider_id]["procedures"].append({
                "ms_drg_definition": procedure.ms_drg_definition,
                "total_discharges": procedure.total_discharges,
                "average_covered_charges": procedure.average_covered_charges,
                "average_total_payments": procedure.average_total_payments,
                "average_medicare_payments": procedure.average_medicare_payments
            })
        # Remove providers with no matching procedures (shouldn't happen, but for safety)
        return [p for p in providers_dict.values() if p["procedures"]]
