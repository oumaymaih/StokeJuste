
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.gestion_produits.schemas import (
    ProduitCreate,
    ProduitUpdate,
    ProduitResponse,
)
from app.features.gestion_produits import service


router = APIRouter(
    prefix="/produits",
    tags=["Gestion des produits"]
)


# 1. Ajouter un produit
@router.post("/", response_model=ProduitResponse, status_code=201)
def ajouter_produit(
    data: ProduitCreate,
    db: Session = Depends(get_db)
):
    return service.creer_produit(db, data)


# 2. Consulter les produits
@router.get("/", response_model=list[ProduitResponse])
def consulter_produits(
    id_commerce: uuid.UUID = Query(...),
    db: Session = Depends(get_db)
):
    return service.lister_produits(db, id_commerce)


# 3. Modifier un produit
@router.patch("/{id_produit}", response_model=ProduitResponse)
def mettre_a_jour_produit(
    id_produit: uuid.UUID,
    id_commerce: uuid.UUID = Query(...),
    data: ProduitUpdate = ...,
    db: Session = Depends(get_db)
):
    return service.modifier_produit(
        db, id_produit, id_commerce, data
    )


# 4. Archiver un produit
@router.delete("/{id_produit}")
def supprimer_produit(
    id_produit: uuid.UUID,
    id_commerce: uuid.UUID = Query(...),
    db: Session = Depends(get_db)
):
    return service.archiver_produit(
        db, id_produit, id_commerce
    )
