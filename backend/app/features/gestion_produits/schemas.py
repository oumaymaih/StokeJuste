
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


# Données communes pour un produit
class ProduitBase(BaseModel):
    nom_produit: str = Field(min_length=1, max_length=150)
    categorie: str = Field(min_length=1, max_length=100)
    marque: str | None = None
    image_url: str | None = None
    prix_vente: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    seuil_minimal: int = Field(default=0, ge=0)
    est_perissable: bool = False


# Données pour ajouter un produit
class ProduitCreate(ProduitBase):
    id_commerce: uuid.UUID
    code_produit: str = Field(min_length=1, max_length=30)


# Données pour modifier un produit
class ProduitUpdate(BaseModel):
    nom_produit: str | None = None
    categorie: str | None = None
    marque: str | None = None
    image_url: str | None = None
    prix_vente: Decimal | None = Field(default=None, ge=0)
    seuil_minimal: int | None = Field(default=None, ge=0)
    est_perissable: bool | None = None


# Données renvoyées par l'API
class ProduitResponse(ProduitBase):
    model_config = ConfigDict(from_attributes=True)

    id_produit: uuid.UUID
    id_commerce: uuid.UUID
    code_produit: str
    est_actif: bool
    date_ajout: datetime
