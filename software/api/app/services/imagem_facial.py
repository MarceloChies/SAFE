import cv2
import numpy as np

TAMANHO_MAXIMO = 5 * 1024 * 1024

class ImagemFacialInvalida(ValueError):
    pass



def validar_imagem(dados: bytes) -> tuple[str, int, int]:
    if not dados:
        raise ImagemFacialInvalida("O arquivo esta vazio")

    if len(dados) > TAMANHO_MAXIMO:
        raise ImagemFacialInvalida(
            "A imagem deve ter no maximo 5 MB."
        )

    if dados.startswith(b"\xff\xd8\xff"):
        tipo_mime = "image/jpeg"
    elif dados.startswith(b"\x89PNG\r\n\x1a\n"):
        tipo_mime = "image/png"
    else:
        raise ImagemFacialInvalida(
            "Formato invalido. Envie uma imagem JPGEG ou PNG"
        )

    buffer = np.frombuffer(dados, dtype=np.uint8)

    try:
        imagem = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    except cv2.error as erro:
        raise ImagemFacialInvalida(
            "Nao foi possivel ler a imagem"
        ) from erro

    if imagem is None:
        raise ImagemFacialInvalida(
            "O arquivo nao contem uma imagem valida"
        )

    altura, largura = imagem.shape[:2]

    return tipo_mime, largura, altura

