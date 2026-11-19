
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# Un produit demandé dans une vente
class ArticleVente(BaseModel):
    id_produit: uuid.UUID
    quantite: int = Field(gt=0)


# Données nécessaires pour enregistrer une vente
class VenteCreate(BaseModel):
    id_commerce: uuid.UUID
    articles: list[ArticleVente] = Field(min_length=1)


# Une ligne de vente enregistrée
class LigneVenteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_ligne: uuid.UUID
    id_vente: uuid.UUID
    id_produit: uuid.UUID
    id_lot: uuid.UUID
    quantite: int
    prix_unitaire: Decimal
    sous_total: Decimal


# Une vente et ses informations
class VenteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_vente: uuid.UUID
    id_commerce: uuid.UUID
    date_vente: datetime
    montant_total: Decimal
    statut: str
    lignes: list[LigneVenteResponse]
