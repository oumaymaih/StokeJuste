
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    String, Numeric, DateTime, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Vente(Base):
    __tablename__ = "ventes"

    __table_args__ = (
        CheckConstraint(
            "statut IN ('VALIDEE', 'ANNULEE')",
            name="ck_vente_statut"
        ),
        CheckConstraint(
            "montant_total >= 0",
            name="ck_vente_montant"
        ),
    )

    id_vente: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    id_commerce: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("commerces.id_commerce"),
        nullable=False
    )

    date_vente: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    montant_total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    statut: Mapped[str] = mapped_column(
        String(20),
        default="VALIDEE",
        nullable=False
    )

    lignes: Mapped[list["LigneVente"]] = relationship(
        "LigneVente",
        back_populates="vente"
    )

