
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    String, Text, Numeric, Integer, Boolean,
    ForeignKey, DateTime, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Produit(Base):
    __tablename__ = "produits"

    __table_args__ = (
        UniqueConstraint(
            "id_commerce",
            "code_produit",
            name="uq_produit_commerce_code"
        ),
    )

    id_produit: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    id_commerce: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("commerces.id_commerce"),
        nullable=False
    )

    code_produit: Mapped[str] = mapped_column(
        String(30), nullable=False
    )

    nom_produit: Mapped[str] = mapped_column(
        String(150), nullable=False
    )

    categorie: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    marque: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    image_url: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    prix_vente: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False
    )

    seuil_minimal: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )

    est_perissable: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    est_actif: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    date_ajout: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
