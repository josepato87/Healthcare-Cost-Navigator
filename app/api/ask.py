from fastapi import APIRouter, Request
from pydantic import BaseModel
from app.services.openai_service import nl_to_sql, is_in_scope
from app.db.models import Provider, Procedure
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy import text
import os
import logging

router = APIRouter(prefix="/ask", tags=["ask"])

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class AskRequest(BaseModel):
    question: str

@router.post("")
async def ask(request: AskRequest):
    try:
        logging.info(f"Received question: {request.question}")
        if not is_in_scope(request.question):
            return {"answer": "I can only help with hospital pricing and quality information. Please ask about medical procedures, costs, or hospital ratings."}
        sql_query = await nl_to_sql(request.question)
        logging.info(f"Generated SQL: {sql_query}")
        logging.info(f"SQL type: {type(sql_query)}")
        if not isinstance(sql_query, str):
            logging.error(f"nl_to_sql did not return a string. Got: {type(sql_query)} - {sql_query}")
            return {"error": f"nl_to_sql did not return a string. Got: {type(sql_query)} - {sql_query}"}
        if not sql_query.strip():
            logging.error(f"OpenAI returned an empty SQL string.")
            return {"error": "OpenAI returned an empty SQL string."}
        try:
            stmt = text(sql_query)
            logging.info(f"Executing SQL statement: {stmt}")
            async with async_session() as session:
                result = await session.execute(stmt)
                rows = result.fetchall()
                logging.info(f"SQL result rows: {rows}")
                answer = [dict(row._mapping) for row in rows]
                return {"answer": answer}
        except Exception as db_exc:
            logging.error(f"DB error: {db_exc}", exc_info=True)
            return {"error": "There was a problem processing your request. Please try again or contact support if the issue persists."}
    except Exception as exc:
        logging.error(f"OpenAI or other error: {exc}", exc_info=True)
        return {"error": f"Internal error: {exc}"}
