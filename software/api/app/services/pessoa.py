from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.pessoa import Pessoa
from app.schemas.pessoa import (
    PessoaAtualizacao,
    PessoaCriacao,
)


class PessoaNaoEncontrada(Exception):
    pass


class PessoaDuplicada(Exception):
    pass


def listar_pessoas(
    database: Session,
    offset: int = 0,
    limite: int = 100,
) -> list[Pessoa]:
    consulta = (
        select(Pessoa)
        .order_by(Pessoa.id)
        .offset(offset)
        .limit(limite)
    )

    return list(database.scalars(consulta).all())


def buscar_pessoa(
    database: Session,
    pessoa_id: int,
) -> Pessoa:
    pessoa = database.get(Pessoa, pessoa_id)

    if pessoa is None:
        raise PessoaNaoEncontrada("pessoa não encontrada")

    return pessoa


def criar_pessoa(
    database: Session,
    dados: PessoaCriacao,
) -> Pessoa:
    pessoa = Pessoa(**dados.model_dump())

    database.add(pessoa)

    try:
        database.commit()
    except IntegrityError as erro:
        database.rollback()

        raise PessoaDuplicada(
            "email ou identificador já cadastrado"
        ) from erro

    database.refresh(pessoa)

    return pessoa


def atualizar_pessoa(
    database: Session,
    pessoa_id: int,
    dados: PessoaAtualizacao,
) -> Pessoa:
    pessoa = buscar_pessoa(database, pessoa_id)

    alteracoes = dados.model_dump(exclude_unset=True)

    for campo, valor in alteracoes.items():
        setattr(pessoa, campo, valor)

    try:
        database.commit()
    except IntegrityError as erro:
        database.rollback()

        raise PessoaDuplicada(
            "email ou identificador já cadastrado"
        ) from erro

    database.refresh(pessoa)

    return pessoa


def excluir_pessoa(
    database: Session,
    pessoa_id: int,
) -> None:
    pessoa = buscar_pessoa(database, pessoa_id)

    database.delete(pessoa)
    database.commit()