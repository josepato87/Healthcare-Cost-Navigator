import os
import openai
import re
import logging

openai.api_key = os.getenv("OPENAI_API_KEY")

IN_SCOPE_KEYWORDS = [
    "hospital", "cost", "price", "quality", "rating", "procedure", "drg", "medicare"
]

def is_in_scope(question: str) -> bool:
    q = question.lower()
    return any(kw in q for kw in IN_SCOPE_KEYWORDS)

async def nl_to_sql(question: str) -> str:
    logging.info("nl_to_sql called")
    prompt = f"""
You are a medical database assistant. Convert the following natural language question into a SQL query for a PostgreSQL database.

The database has these tables and columns:

Table: providers
- provider_id (PK)
- name
- city
- state
- zip_code
- star_rating

Table: procedures
- procedure_id (PK)
- ms_drg_definition
- total_discharges
- average_covered_charges
- average_total_payments
- average_medicare_payments
- provider_id (FK to providers.provider_id)

Use only these columns. 
When filtering by ms_drg_definition, use the LIKE operator instead of =, and wrap the value in percent signs (e.g., WHERE ms_drg_definition LIKE '%value%'). 
Return only the SQL query, no explanation.
Also remove the limit 1 from the final query unless the question explicitly asks for a single or the best result.

Question: {question}
"""
    logging.info(f"OpenAI prompt: {prompt}")
    response = await openai.AsyncOpenAI().chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    logging.info(f"OpenAI raw response: {response}")
    sql = response.choices[0].message.content.strip()
    # Remove only explanations, not the SQL query itself
    # If the response contains multiple queries, keep the first full query
    sql = sql.split(';')[0] + ';' if sql.count(';') == 1 else sql
    logging.info(f"Sanitized SQL: {sql}")
    logging.info("nl_to_sql finished")
    return sql
