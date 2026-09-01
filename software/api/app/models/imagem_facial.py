from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ImagemFacial(Base):
    __tablename__ = "imagens_faciais"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    pessoa_id: Mapped[int] = mapped_column(
        ForeignKey(
            "pessoas.id",
            ondelete="CASCADE",
        ),
        index=True,
        nullable=False,
    )

    dados: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False,
    )

    tipo_mime: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    largura: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    altura: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    data_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    pessoa: Mapped["Pessoa"] = relationship(
        back_populates="imagens",
    )