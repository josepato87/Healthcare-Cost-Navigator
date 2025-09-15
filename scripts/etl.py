import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import csv
import random
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, Provider, Procedure

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://navigator:navigator@localhost:5432/navigator")
CSV_PATH = os.path.join(os.path.dirname(__file__), '../resources/MUP_INP_RY24_P03_V10_DY22_PrvSvc.csv')
BATCH_SIZE = 1000

async def main():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    providers = {}
    procedures_batch = []
    total_procedures = 0
    with open(CSV_PATH, newline='', encoding='latin1') as csvfile:
        reader = csv.DictReader(csvfile)
        # print(f"CSV columns: {reader.fieldnames}")
        required_columns = [
            'Rndrng_Prvdr_CCN', 'Rndrng_Prvdr_Org_Name', 'Rndrng_Prvdr_City', 'Rndrng_Prvdr_St', 'Rndrng_Prvdr_Zip5',
            'DRG_Desc', 'Tot_Dschrgs', 'Avg_Submtd_Cvrd_Chrg', 'Avg_Tot_Pymt_Amt', 'Avg_Mdcr_Pymt_Amt'
        ]
        missing = [col for col in required_columns if col not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing columns in CSV: {missing}")
        async with async_session() as session:
            for i, row in enumerate(reader):
                pid = row['Rndrng_Prvdr_CCN']
                if pid not in providers:
                    providers[pid] = Provider(
                        provider_id=pid,
                        name=row['Rndrng_Prvdr_Org_Name'],
                        city=row['Rndrng_Prvdr_City'],
                        state=row['Rndrng_Prvdr_St'],
                        zip_code=row['Rndrng_Prvdr_Zip5'],
                        star_rating=random.uniform(1, 10)
                    )
                procedures_batch.append(Procedure(
                    ms_drg_definition=row['DRG_Desc'],
                    total_discharges=int(row['Tot_Dschrgs']),
                    average_covered_charges=float(row['Avg_Submtd_Cvrd_Chrg']),
                    average_total_payments=float(row['Avg_Tot_Pymt_Amt']),
                    average_medicare_payments=float(row['Avg_Mdcr_Pymt_Amt']),
                    provider=providers[pid]
                ))
                total_procedures += 1
                # Batch insert every BATCH_SIZE records
                if len(procedures_batch) >= BATCH_SIZE:
                    session.add_all(procedures_batch)
                    await session.flush()
                    procedures_batch.clear()
            # Insert any remaining procedures
            if procedures_batch:
                session.add_all(procedures_batch)
                await session.flush()
            # Insert all providers (if not already added)
            session.add_all(providers.values())
            await session.commit()
    print(f"Inserted {len(providers)} providers and {total_procedures} procedures into the database.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
