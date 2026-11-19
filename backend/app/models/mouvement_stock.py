
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class MouvementStock(Base):
    __tablename__ = "mouvements_stock"

    __table_args__ = (
        CheckConstraint(
            "type_mouvement IN ('ENTREE', 'VENTE', 'PERTE', 'AJUSTEMENT')",
            name="ck_type_mouvement"
        ),
    )

    id_mouvement: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    id_lot: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lots_stock.id_lot"),
        nullable=False
    )

    type_mouvement: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    variation_quantite: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    motif: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    date_mouvement: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
