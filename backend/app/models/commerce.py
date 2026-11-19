
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


# Table des commerçants
class Commercant(Base):
    __tablename__ = "commercants"

    id_commercant: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    nom_complet: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    telephone: Mapped[str] = mapped_column(String(20))
    mot_de_passe_hash: Mapped[str] = mapped_column(Text)

    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


# Table des commerces
class Commerce(Base):
    __tablename__ = "commerces"

    id_commerce: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    id_commercant: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("commercants.id_commercant"),
        nullable=False
    )

    nom_commercial: Mapped[str] = mapped_column(String(150))
    type_commerce: Mapped[str] = mapped_column(String(50))
    adresse: Mapped[str] = mapped_column(Text)
    ville: Mapped[str] = mapped_column(String(100))

    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
