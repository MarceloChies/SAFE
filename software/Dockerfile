FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install \
    --no-cache-dir \
    -r requirements.txt

COPY api/app ./app
COPY api/alembic.ini .
COPY api/migrations ./migrations

RUN mkdir -p /app/data

ENV DATABASE_URL=sqlite:////app/data/safe.sqlite3

CMD ["sh", "-c", "python -m alembic upgrade head && exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]