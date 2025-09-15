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

There are three matching strategies for ms_drg_definition:
1. Fuzzy (typo-tolerant): Use similarity(ms_drg_definition, 'search_term') > 0.1 and order by similarity descending.
2. Fulltext (advanced): Use to_tsvector('english', ms_drg_definition) @@ plainto_tsquery('english', 'search_term').
3. Substring (case-insensitive): Use ILIKE '%search_term%'.

Choose the best strategy based on the user's question:
- For misspellings, typos, or ambiguous queries, use fuzzy.
- For complex, multi-word, or semantic queries, use fulltext.
- For exact DRG codes or clear keywords, use substring and separate the words to be used as separated like clauses with AND, for example "heart attack" would be ilike('%heart%') and ilike('%attack%').

Return only the SQL query, no explanation. 
If the question asks for a specific number of results, use LIMIT, but never more than 10. 
If not specified, LIMIT 5. 
If the question asks in plurals like: hospitals, providers, procedures; return multiple results with LIMIT 5.
If the question asks for the best or cheapest, and is explicit a single result, use LIMIT 1, otherwise LIMIT 5.

Return fields based on the question and always add the whole ms_drg_definition, average_total_payments, zip_code and star_rating.

Question: {question}
"""
    # logging.info(f"OpenAI prompt: {prompt}")
    response = await openai.AsyncOpenAI().chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    # logging.info(f"OpenAI raw response: {response}")
    sql = response.choices[0].message.content.strip()
    # Remove markdown code block markers if present
    if sql.startswith('```'):
        sql = sql.split('```')[1].strip() if '```' in sql else sql
    # Remove any leading/trailing code block language markers (e.g., 'sql')
    if sql.lower().startswith('sql'):
        sql = sql[3:].strip()
    # Remove only explanations, not the SQL query itself
    # If the response contains multiple queries, keep the first full query
    sql = sql.split(';')[0] + ';' if sql.count(';') == 1 else sql
    logging.info(f"Sanitized SQL: {sql}")
    logging.info("nl_to_sql finished")
    return sql
