import re
from datetime import date, datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

Nome = Annotated[str, Field(min_length=1, max_length=100)]
Email = Annotated[str, Field(max_length=255)]
Identificador = Annotated[str, Field(min_length=1, max_length=80)]

PADRAO_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalizar_email(valor: str | None) -> str | None:
    if valor is None:
        return None

    email = valor.strip().lower()

    if not PADRAO_EMAIL.fullmatch(email):
        raise ValueError("email inválido")

    return email


class PessoaBase(BaseModel):
    nome: Nome
    data_nascimento: date | None = None
    email: Email | None = None
    identificador: Identificador

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("email", mode="before")
    @classmethod
    def validar_email(cls, valor: str | None) -> str | None:
        return normalizar_email(valor)

    @field_validator("data_nascimento")
    @classmethod
    def validar_data_nascimento(cls, valor: date | None) -> date | None:
        if valor is not None and valor > date.today():
            raise ValueError(
                "data de nascimento não pode estar no futuro"
            )

        return valor


class PessoaCriacao(PessoaBase):
    pass


class PessoaAtualizacao(BaseModel):
    nome: Nome | None = None
    data_nascimento: date | None = None
    email: Email | None = None
    identificador: Identificador | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("nome", "identificador", mode="before")
    @classmethod
    def validar_campos_obrigatorios(cls, valor):
        if valor is None:
            raise ValueError("campo não pode ser nulo")

        return valor

    @field_validator("email", mode="before")
    @classmethod
    def validar_email(cls, valor: str | None) -> str | None:
        return normalizar_email(valor)

    @field_validator("data_nascimento")
    @classmethod
    def validar_data_nascimento(cls, valor: date | None) -> date | None:
        if valor is not None and valor > date.today():
            raise ValueError(
                "data de nascimento não pode estar no futuro"
            )

        return valor

    @model_validator(mode="after")
    def validar_atualizacao(self):
        if not self.model_fields_set:
            raise ValueError(
                "informe pelo menos um campo para atualizar"
            )

        return self


class PessoaResposta(PessoaBase):
    id: int
    data_registro: datetime

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )