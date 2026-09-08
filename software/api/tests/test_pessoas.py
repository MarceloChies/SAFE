from fastapi.testclient import TestClient


def dados_pessoa(
    identificador: str = "SAFE-001",
    email: str = "maria@example.com",
) -> dict:
    return {
        "nome": "Maria Silva",
        "data_nascimento": "2000-05-20",
        "email": email,
        "identificador": identificador,
    }


def cadastrar_pessoa(
    client: TestClient,
    identificador: str = "SAFE-001",
    email: str = "maria@example.com",
) -> dict:
    resposta = client.post(
        "/pessoas",
        json=dados_pessoa(identificador, email),
    )
    assert resposta.status_code == 201
    return resposta.json()


def test_criar_pessoa(client: TestClient):
    resposta = client.post(
        "/pessoas",
        json=dados_pessoa(email="MARIA@EXAMPLE.COM"),
    )

    assert resposta.status_code == 201
    pessoa = resposta.json()
    assert pessoa["id"] > 0
    assert pessoa["nome"] == "Maria Silva"
    assert pessoa["email"] == "maria@example.com"
    assert pessoa["identificador"] == "SAFE-001"
    assert pessoa["data_registro"] is not None


def test_listar_pessoas_com_paginacao(client: TestClient):
    cadastrar_pessoa(client)
    cadastrar_pessoa(
        client,
        identificador="SAFE-002",
        email="joao@example.com",
    )

    resposta = client.get(
        "/pessoas",
        params={"offset": 1, "limite": 1},
    )

    assert resposta.status_code == 200
    pessoas = resposta.json()
    assert len(pessoas) == 1
    assert pessoas[0]["identificador"] == "SAFE-002"


def test_consultar_pessoa(client: TestClient):
    pessoa = cadastrar_pessoa(client)

    resposta = client.get(f"/pessoas/{pessoa['id']}")

    assert resposta.status_code == 200
    assert resposta.json()["id"] == pessoa["id"]


def test_atualizar_pessoa(client: TestClient):
    pessoa = cadastrar_pessoa(client)

    resposta = client.patch(
        f"/pessoas/{pessoa['id']}",
        json={"nome": "Maria Souza", "email": None},
    )

    assert resposta.status_code == 200
    pessoa_atualizada = resposta.json()
    assert pessoa_atualizada["nome"] == "Maria Souza"
    assert pessoa_atualizada["email"] is None


def test_excluir_pessoa(client: TestClient):
    pessoa = cadastrar_pessoa(client)

    resposta = client.delete(f"/pessoas/{pessoa['id']}")

    assert resposta.status_code == 204
    assert resposta.content == b""
    assert client.get(f"/pessoas/{pessoa['id']}").status_code == 404


def test_retornar_404_para_pessoa_inexistente(client: TestClient):
    assert client.get("/pessoas/999").status_code == 404
    assert client.patch(
        "/pessoas/999",
        json={"nome": "Novo nome"},
    ).status_code == 404
    assert client.delete("/pessoas/999").status_code == 404


def test_impedir_email_e_identificador_duplicados(client: TestClient):
    cadastrar_pessoa(client)

    resposta_email = client.post(
        "/pessoas",
        json=dados_pessoa(
            identificador="SAFE-002",
            email="maria@example.com",
        ),
    )
    resposta_identificador = client.post(
        "/pessoas",
        json=dados_pessoa(
            identificador="SAFE-001",
            email="outra@example.com",
        ),
    )

    assert resposta_email.status_code == 409
    assert resposta_identificador.status_code == 409


def test_validar_dados_de_entrada(client: TestClient):
    resposta_email = client.post(
        "/pessoas",
        json=dados_pessoa(email="email-invalido"),
    )
    resposta_data = client.post(
        "/pessoas",
        json={
            **dados_pessoa(),
            "data_nascimento": "2999-01-01",
        },
    )
    resposta_patch_vazio = client.patch(
        "/pessoas/1",
        json={},
    )

    assert resposta_email.status_code == 422
    assert resposta_data.status_code == 422
    assert resposta_patch_vazio.status_code == 422
