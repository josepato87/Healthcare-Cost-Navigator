# Healthcare Cost Navigator

## Overview
A FastAPI web service for searching hospitals offering MS-DRG procedures, viewing estimated prices & quality ratings, and interacting with an AI assistant for natural language queries.

## Features
- Search hospitals by DRG, ZIP, and radius
- View estimated prices and quality ratings
- AI assistant for natural language queries (cost, rating, drg descriptions, etc.)

## Architecture Decisions
- Clean architecture: separation of API, services, and DB layers
- Async SQLAlchemy for scalable DB access
- Docker Compose for reproducible dev environment
- Mock star ratings for providers (can be replaced with real data)

## Tech Stack
- Python 3.11
- FastAPI
- async SQLAlchemy
- PostgreSQL
- OpenAI API
- Docker & Docker Compose

## Setup Instructions

### 1. Clone the repo
```
git clone <repo-url>
cd Healthcare-Cost-Navigator
```

### 2. Add your OpenAI API key
Edit `.env.template` and set your `OPENAI_API_KEY` and other credentials, then copy it to `.env`.

### 3. Build and start the stack
```
docker-compose up --build
```

### 4. Generate initial migration (if not present)
```
docker-compose run app alembic revision --autogenerate -m "Initial tables"
```

### 5. Run migrations to set up the database schema
```
docker-compose run app alembic upgrade head
```

### 6. Run ETL to seed the database
```
docker-compose run app python scripts/etl.py
```

## Alembic Troubleshooting
- Ensure your `.env` file contains a valid `DATABASE_URL` and is loaded by Docker Compose.
- If you get errors about missing models, check that `app/db/models.py` defines all tables and `Base = declarative_base()`.
- If you change your models, re-run the revision and upgrade commands to update the schema.

## API Usage

### Search Providers
You can refine your search using the `match_type` query parameter:
- `match_type=substring` (default): Case-insensitive substring matching (recommended for most queries).
- `match_type=fuzzy`: Typo-tolerant fuzzy matching using trigram similarity (requires `pg_trgm` extension).
- `match_type=fulltext`: Advanced phrase/semantic matching using PostgreSQL full-text search (if enabled).

Example:
```
curl 'http://localhost:8000/providers?drg=CRANIOTOMY&zip=36301&radius_km=40&match_type=substring'
curl 'http://localhost:8000/providers?drg=kraniotomy&zip=36301&match_type=fuzzy'
curl 'http://localhost:8000/providers?drg=major joint&zip=10001&match_type=fulltext'
```

The `match_type` parameter lets you choose the best strategy for your search, making the API versatile for both exact and natural language queries.

```
curl 'http://localhost:8000/providers?drg=CRANIOTOMY&zip=36301&radius_km=40&match_type=fulltext'
```

#### Sample Response
```json
[
  {
    "provider_id": "010001",
    "name": "Southeast Health Medical Center",
    "city": "Dothan",
    "state": "1108 Ross Clark Circle",
    "zip_code": "36301",
    "star_rating": 2.6,
    "procedures": [
      {
        "ms_drg_definition": "CRANIOTOMY WITH MAJOR DEVICE IMPLANT OR ACUTE COMPLEX CNS PRINCIPAL DIAGNOSIS WITHOUT MC",
        "total_discharges": 18,
        "average_covered_charges": 107085.33333,
        "average_total_payments": 25842.666667,
        "average_medicare_payments": 23857.944444
      },
      {
        "ms_drg_definition": "CRANIOTOMY AND ENDOVASCULAR INTRACRANIAL PROCEDURES WITH MCC",
        "total_discharges": 18,
        "average_covered_charges": 156326.77778,
        "average_total_payments": 32167.888889,
        "average_medicare_payments": 27662.944444
      },
      {
        "ms_drg_definition": "CRANIOTOMY WITH MAJOR DEVICE IMPLANT OR ACUTE COMPLEX CNS PRINCIPAL DIAGNOSIS WITH MCC O",
        "total_discharges": 25,
        "average_covered_charges": 158541.64,
        "average_total_payments": 37331,
        "average_medicare_payments": 35332.96
      }
    ]
  }
]
```

### AI Assistant
```
curl -X POST 'http://localhost:8000/ask' -H 'Content-Type: application/json' -d '{"question": "What are the cheapest options in hospitals for heart failure?"}'
```

#### Sample Response
```json
{
  "answer": [
    {
      "name": "Willis Knighton Medical Center, Inc",
      "city": "Shreveport",
      "state": "2600 Greenwood Road",
      "zip_code": "71103",
      "star_rating": 8.015208597663571,
      "ms_drg_definition": "HEART FAILURE AND SHOCK WITHOUT CC/MCC",
      "average_total_payments": 4317.2
    },
    {
      "name": "Monroe County Medical Center",
      "city": "Tompkinsville",
      "state": "529 Capp Harlan Road",
      "zip_code": "42167",
      "star_rating": 3.962343352520022,
      "ms_drg_definition": "HEART FAILURE AND SHOCK WITHOUT CC/MCC",
      "average_total_payments": 4367.9090909
    },
    {
      "name": "Central Vermont Medical Center",
      "city": "Barre",
      "state": "Box 547",
      "zip_code": "05641",
      "star_rating": 3.7994693684783827,
      "ms_drg_definition": "HEART FAILURE AND SHOCK WITH MCC",
      "average_total_payments": 4464.8602151
    },
    {
      "name": "Avoyelles Hospital",
      "city": "Marksville",
      "state": "4231 Highway 1192",
      "zip_code": "71351",
      "star_rating": 1.3653098354735926,
      "ms_drg_definition": "HEART FAILURE AND SHOCK WITHOUT CC/MCC",
      "average_total_payments": 4538.0714286
    },
    {
      "name": "Rutland Regional Medical Center",
      "city": "Rutland",
      "state": "160 Allen St",
      "zip_code": "05701",
      "star_rating": 9.604882114237704,
      "ms_drg_definition": "HEART FAILURE AND SHOCK WITH CC",
      "average_total_payments": 4662.6666667
    }
  ]
}
```

## Example Prompts for AI
1. Which hospitals have the lowest cost for CRANIOTOMY in 36301?
2. What are the cheapest options in hospitals for heart failure?
3. Show me hospitals offering DRG Renal Failure within 20km of 36301.
4. What is the average cost for major joint replacement in Denver?
5. List hospitals with 9+ star ratings for cardiac procedures near 10032.

## Testing
Run tests with:
```
docker-compose run app pytest
```

