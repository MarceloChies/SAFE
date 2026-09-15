from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import imagem_facial as _imagem_facial_model
from app.models import pessoa as _pessoa_model


engine_teste = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine_teste, "connect")
def habilitar_chaves_estrangeiras(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionTeste = sessionmaker(
    bind=engine_teste,
    autoflush=False,
    expire_on_commit=False,
)


def substituir_get_db() -> Generator[Session, None, None]:
    with SessionTeste() as database:
        yield database


@pytest.fixture(autouse=True)
def preparar_banco():
    Base.metadata.create_all(engine_teste)
    yield
    Base.metadata.drop_all(engine_teste)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = substituir_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
