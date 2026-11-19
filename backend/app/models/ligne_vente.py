
import uuid
from decimal import Decimal

from sqlalchemy import (
    Integer, Numeric, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class LigneVente(Base):
    __tablename__ = "lignes_vente"

    __table_args__ = (
        CheckConstraint(
            "quantite > 0",
            name="ck_ligne_quantite"
        ),
        CheckConstraint(
            "prix_unitaire >= 0 AND sous_total >= 0",
            name="ck_ligne_montants"
        ),
    )

    id_ligne: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    id_vente: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ventes.id_vente"),
        nullable=False
    )

    id_produit: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("produits.id_produit"),
        nullable=False
    )

    id_lot: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lots_stock.id_lot"),
        nullable=False
    )

    quantite: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    prix_unitaire: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    sous_total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    
    vente: Mapped["Vente"] = relationship(
        "Vente",
        back_populates="lignes"
    )
