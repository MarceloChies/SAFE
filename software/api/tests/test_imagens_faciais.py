import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models.imagem_facial import ImagemFacial
from tests.conftest import SessionTeste
from tests.test_pessoas import cadastrar_pessoa


def gerar_imagem(extensao: str = ".png") -> bytes:
    imagem = np.zeros((24, 32, 3), dtype=np.uint8)
    sucesso, dados = cv2.imencode(extensao, imagem)
    assert sucesso
    return dados.tobytes()


def enviar_imagem(client: TestClient, pessoa_id: int, dados: bytes):
    return client.post(
        f"/pessoas/{pessoa_id}/imagens",
        files={"arquivo": ("foto.png", dados, "image/png")},
    )


@pytest.mark.parametrize(
    "extensao,tipo_mime",
    [(".jpg", "image/jpeg"), (".png", "image/png")],
)
def test_upload_salva_imagem_e_retorna_metadados(
    client: TestClient, extensao: str, tipo_mime: str,
):
    pessoa = cadastrar_pessoa(client)
    dados = gerar_imagem(extensao)

    # O formato deve ser identificado pelo conteudo, mesmo com MIME errado.
    resposta = client.post(
        f"/pessoas/{pessoa['id']}/imagens",
        files={"arquivo": ("foto.txt", dados, "text/plain")},
    )

    assert resposta.status_code == 201
    metadados = resposta.json()
    assert metadados["id"] > 0
    assert metadados["pessoa_id"] == pessoa["id"]
    assert metadados["tipo_mime"] == tipo_mime
    assert metadados["largura"] == 32
    assert metadados["altura"] == 24
    assert metadados["data_registro"] is not None
    assert "dados" not in metadados

    with SessionTeste() as database:
        imagem = database.get(ImagemFacial, metadados["id"])
        assert imagem is not None
        assert imagem.dados == dados
        assert imagem.pessoa_id == pessoa["id"]


@pytest.mark.parametrize(
    "dados",
    [
        b"",
        b"arquivo de texto",
        b"\xff\xd8\xffarquivo corrompido",
        b"\x89PNG\r\n\x1a\narquivo corrompido",
        b"x" * (5 * 1024 * 1024 + 1),
    ],
    ids=["vazio", "texto", "jpeg-corrompido", "png-corrompido", "acima-de-5mb"],
)
def test_upload_invalido_nao_salva_imagem(client: TestClient, dados: bytes):
    pessoa = cadastrar_pessoa(client)

    resposta = enviar_imagem(client, pessoa["id"], dados)

    assert resposta.status_code == 400
    assert resposta.json()["detail"]
    assert client.get(f"/pessoas/{pessoa['id']}/imagens").json() == []


def test_upload_para_pessoa_inexistente(client: TestClient):
    resposta = enviar_imagem(client, 999, gerar_imagem())

    assert resposta.status_code == 404
    with SessionTeste() as database:
        assert database.scalars(select(ImagemFacial)).all() == []


def test_upload_sem_arquivo(client: TestClient):
    pessoa = cadastrar_pessoa(client)

    resposta = client.post(f"/pessoas/{pessoa['id']}/imagens")

    assert resposta.status_code == 422


def test_listagem_retorna_apenas_imagens_da_pessoa(client: TestClient):
    pessoa = cadastrar_pessoa(client)
    outra_pessoa = cadastrar_pessoa(
        client, identificador="SAFE-002", email="joao@example.com",
    )
    imagens = []
    for extensao in (".png", ".jpg"):
        resposta = enviar_imagem(client, pessoa["id"], gerar_imagem(extensao))
        assert resposta.status_code == 201
        imagens.append(resposta.json())
    resposta_outra = enviar_imagem(client, outra_pessoa["id"], gerar_imagem())
    assert resposta_outra.status_code == 201

    resposta = client.get(f"/pessoas/{pessoa['id']}/imagens")

    assert resposta.status_code == 200
    assert resposta.json() == imagens


def test_listagem_sem_imagens(client: TestClient):
    pessoa = cadastrar_pessoa(client)

    resposta = client.get(f"/pessoas/{pessoa['id']}/imagens")

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_listagem_para_pessoa_inexistente(client: TestClient):
    resposta = client.get("/pessoas/999/imagens")

    assert resposta.status_code == 404
