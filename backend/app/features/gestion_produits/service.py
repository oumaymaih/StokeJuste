
import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.commerce import Commerce
from app.models.produit import Produit
from app.features.gestion_produits.schemas import (
    ProduitCreate,
    ProduitUpdate,
)


# 1. Ajouter un produit
def creer_produit(db: Session, data: ProduitCreate):
    commerce = db.get(Commerce, data.id_commerce)

    if commerce is None:
        raise HTTPException(
            status_code=404,
            detail="Commerce introuvable"
        )

    produit = Produit(**data.model_dump())

    try:
        db.add(produit)
        db.commit()
        db.refresh(produit)
        return produit

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ce code produit existe déjà dans ce commerce"
        )


# 2. Consulter les produits d'un commerce
def lister_produits(db: Session, id_commerce: uuid.UUID):
    return db.scalars(
        select(Produit)
        .where(
            Produit.id_commerce == id_commerce,
            Produit.est_actif.is_(True)
        )
        .order_by(Produit.date_ajout.desc())
    ).all()


# 3. Modifier un produit
def modifier_produit(
    db: Session,
    id_produit: uuid.UUID,
    id_commerce: uuid.UUID,
    data: ProduitUpdate
):
    produit = db.scalar(
        select(Produit).where(
            Produit.id_produit == id_produit,
            Produit.id_commerce == id_commerce,
            Produit.est_actif.is_(True)
        )
    )

    if produit is None:
        raise HTTPException(
            status_code=404,
            detail="Produit introuvable"
        )

    modifications = data.model_dump(exclude_unset=True)

    for champ, valeur in modifications.items():
        setattr(produit, champ, valeur)

    db.commit()
    db.refresh(produit)
    return produit


# 4. Archiver un produit
def archiver_produit(
    db: Session,
    id_produit: uuid.UUID,
    id_commerce: uuid.UUID
):
    produit = db.scalar(
        select(Produit).where(
            Produit.id_produit == id_produit,
            Produit.id_commerce == id_commerce,
            Produit.est_actif.is_(True)
        )
    )

    if produit is None:
        raise HTTPException(
            status_code=404,
            detail="Produit introuvable"
        )

    produit.est_actif = False
    db.commit()

    return {"message": "Produit archivé avec succès"}
