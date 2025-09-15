# Healthcare Cost Navigator

## Overview
A FastAPI web service for searching hospitals offering MS-DRG procedures, viewing estimated prices & quality ratings, and interacting with an AI assistant for natural language queries.

## Features
- Search hospitals by DRG, ZIP, and radius
- View estimated prices and quality ratings
- AI assistant for natural language queries (cost, quality, etc.)

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
```
curl 'http://localhost:8000/providers?drg=CRANIOTOMY&zip=36301&radius_km=40'
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
    "star_rating": 1.4,
    "procedures": [
      {
        "ms_drg_definition": "CRANIOTOMY WITH MAJOR DEVICE IMPLANT OR ACUTE COMPLEX CNS PRINCIPAL DIAGNOSIS WITH MCC O",
        "total_discharges": 25,
        "average_covered_charges": 158541.64,
        "average_total_payments": 37331.0,
        "average_medicare_payments": 35332.96
      },
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
      }
    ]
  }
]
```

### AI Assistant
```
curl -X POST 'http://localhost:8000/ask' -H 'Content-Type: application/json' -d '{"question": "Which hospitals have the lowest cost for CRANIOTOMY in 36301?"}'
```

#### Sample Response
```json
{
  "answer": [
    {
      "name": "Southeast Health Medical Center",
      "city": "Dothan",
      "state": "1108 Ross Clark Circle",
      "zip_code": "36301",
      "average_covered_charges": 107085.33333
    },
    {
      "name": "Southeast Health Medical Center",
      "city": "Dothan",
      "state": "1108 Ross Clark Circle",
      "zip_code": "36301",
      "average_covered_charges": 156326.77778
    },
    {
      "name": "Southeast Health Medical Center",
      "city": "Dothan",
      "state": "1108 Ross Clark Circle",
      "zip_code": "36301",
      "average_covered_charges": 158541.64
    }
  ]
}
```


