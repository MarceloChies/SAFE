import cv2

from pathlib import Path

def main():
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
    camera = cv2.VideoCapture(0)

    try:
        if not camera.isOpened():
            raise RuntimeError("nao foi possivel abrir a webcam")

        while True:
            sucesso, frame = camera.read()

            if not sucesso:
                print("Nao foi possivel capturar o frame")
                break

            imagem_cinza = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY,
            )

            rostos = detector.detectMultiScale(
                imagem_cinza,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
            )

            for x, y, largura, altura in rostos:
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + largura, y + altura),
                    (0, 255, 0),
                    2,
                )

            cv2.imshow("SAFE - Webcam", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()