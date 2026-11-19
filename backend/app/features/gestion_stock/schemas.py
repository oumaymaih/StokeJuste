
import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field, ConfigDict, model_validator


# Données nécessaires pour réceptionner un lot
class LotCreate(BaseModel):
    id_produit: uuid.UUID
    numero_lot: str | None = Field(default=None, max_length=50)
    quantite_recue: int = Field(gt=0)
    date_production: date | None = None
    date_peremption: date | None = None

    @model_validator(mode="after")
    def verifier_dates(self):
        if (
            self.date_production is not None
            and self.date_peremption is not None
            and self.date_peremption < self.date_production
        ):
            raise ValueError(
                "La date de péremption doit être après "
                "la date de production"
            )
        return self


# Données renvoyées après la réception
class LotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_lot: uuid.UUID
    id_produit: uuid.UUID
    numero_lot: str
    quantite_recue: int
    quantite_restante: int
    date_production: date | None
    date_reception: datetime
    date_peremption: date | None


# Données d'un mouvement de stock
class MouvementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_mouvement: uuid.UUID
    id_lot: uuid.UUID
    type_mouvement: str
    variation_quantite: int
    motif: str | None
    date_mouvement: datetime


class AjustementStock(BaseModel):
    nouvelle_quantite: int = Field(ge=0)
    motif: str = Field(min_length=1, max_length=255)

class PerteStock(BaseModel):
    quantite_perdue: int = Field(gt=0)
    motif: str = Field(min_length=1, max_length=255)