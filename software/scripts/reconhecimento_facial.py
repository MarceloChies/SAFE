from pathlib import Path

import cv2
import numpy as np
import requests


API_URL = "http://127.0.0.1:8000"
TAMANHO_ROSTO = (200, 200)


def criar_detector():
    caminho = (
        Path(__file__).resolve().parent.parent
        / "api"
        / "app"
        / "assets"
        / "haarcascade_frontalface_default.xml"
    )

    detector = cv2.CascadeClassifier(str(caminho))

    if detector.empty():
        raise RuntimeError("Não foi possível carregar o detector.")

    return detector


def carregar_referencias(detector):
    pessoas = requests.get(
        f"{API_URL}/pessoas",
        timeout=10,
    )
    pessoas.raise_for_status()

    rostos_treinamento = []
    identificadores = []
    nomes = {}

    for pessoa in pessoas.json():
        pessoa_id = pessoa["id"]
        nomes[pessoa_id] = pessoa["nome"]

        resposta = requests.get(
            f"{API_URL}/pessoas/{pessoa_id}/imagens",
            timeout=10,
        )
        resposta.raise_for_status()

        for metadados in resposta.json():
            imagem_id = metadados["id"]

            arquivo = requests.get(
                (
                    f"{API_URL}/pessoas/{pessoa_id}"
                    f"/imagens/{imagem_id}/arquivo"
                ),
                timeout=10,
            )
            arquivo.raise_for_status()

            buffer = np.frombuffer(
                arquivo.content,
                dtype=np.uint8,
            )
            imagem = cv2.imdecode(
                buffer,
                cv2.IMREAD_GRAYSCALE,
            )

            if imagem is None:
                continue

            rostos = detector.detectMultiScale(
                imagem,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
            )

            if len(rostos) != 1:
                continue

            x, y, largura, altura = rostos[0]
            rosto = imagem[
                y:y + altura,
                x:x + largura,
            ]
            rosto = cv2.resize(rosto, TAMANHO_ROSTO)

            rostos_treinamento.append(rosto)
            identificadores.append(pessoa_id)

    if not rostos_treinamento:
        raise RuntimeError(
            "Nenhuma imagem facial válida foi encontrada."
        )

    reconhecedor = cv2.face.LBPHFaceRecognizer_create(
        radius=1,
        neighbors=8,
        grid_x=8,
        grid_y=8,
        threshold=70,
    )

    reconhecedor.train(
        rostos_treinamento,
        np.array(identificadores, dtype=np.int32),
    )

    print(
        f"Treinamento concluído com "
        f"{len(rostos_treinamento)} imagem(ns)."
    )

    return reconhecedor, nomes