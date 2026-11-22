
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    String, Integer, Numeric, Boolean,
    Date, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class HistoriqueVente(Base):
    __tablename__ = "historique_ventes"

    __table_args__ = (
        UniqueConstraint(
            "id_produit",
            "periode",
            name="uq_historique_produit_periode"
        ),
    )

    id_historique: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    id_produit: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("produits.id_produit"),
        nullable=False
    )

    periode: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    ventes_s1: Mapped[int] = mapped_column(Integer)
    ventes_s2: Mapped[int] = mapped_column(Integer)
    ventes_s3: Mapped[int] = mapped_column(Integer)
    ventes_s4: Mapped[int] = mapped_column(Integer)

    promotion: Mapped[bool] = mapped_column(Boolean)

    prix: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    nombre_lots: Mapped[int] = mapped_column(Integer)

    date_production: Mapped[date | None] = mapped_column(Date)
    date_peremption: Mapped[date | None] = mapped_column(Date)

    quantite_predite: Mapped[int] = mapped_column(Integer)
