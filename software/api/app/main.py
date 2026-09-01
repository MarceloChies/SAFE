from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status:" "healthy"}


@app.get("/health/database")
def database_health(
    database: Session = Depends(get_db),
):
    try:
        database.execute(text("SELECT 1"))

        database_path = database.execute(
            text("PRAGMA database_list")
        ).all()

        return {
            "status": "connected",
            "database": str(database_path),
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        )