
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class LotStock(Base):
    __tablename__ = "lots_stock"

    __table_args__ = (
        CheckConstraint(
            "quantite_recue >= 0",
            name="ck_lot_quantite_recue"
        ),
        CheckConstraint(
            "quantite_restante >= 0 AND quantite_restante <= quantite_recue",
            name="ck_lot_quantite_restante"
        ),
    )

    id_lot: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    id_produit: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("produits.id_produit"),
        nullable=False
    )

    numero_lot: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    quantite_recue: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    quantite_restante: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    date_production: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    date_reception: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    date_peremption: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )
