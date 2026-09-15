from datetime import datetime

from pydantic import BaseModel, ConfigDict

class ImagemFacialResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:int 
    pessoa_id: int
    tipo_mime: str
    largura: int
    altura: int
    data_registro: datetime