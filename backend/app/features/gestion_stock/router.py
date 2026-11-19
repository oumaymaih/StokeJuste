
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.gestion_stock.schemas import (
    LotCreate,
    LotResponse,
    MouvementResponse,
    AjustementStock,
    PerteStock
)
from app.features.gestion_stock import service


router = APIRouter(
    prefix="/stocks",
    tags=["Gestion des stocks"]
)


# 1. Réceptionner un nouveau lot
@router.post("/lots", response_model=LotResponse, status_code=201)
def ajouter_lot(
    data: LotCreate,
    db: Session = Depends(get_db)
):
    return service.receptionner_lot(db, data)


# 2. Consulter les lots d'un produit
@router.get("/lots", response_model=list[LotResponse])
def consulter_lots(
    id_produit: uuid.UUID,
    db: Session = Depends(get_db)
):
    return service.lister_lots(db, id_produit)


# 3. Consulter les mouvements d'un lot
@router.get(
    "/mouvements",
    response_model=list[MouvementResponse]
)
def consulter_mouvements(
    id_lot: uuid.UUID,
    db: Session = Depends(get_db)
):
    return service.lister_mouvements(db, id_lot)


# 4. Ajuster la quantité d'un lot
@router.patch(
    "/lots/{id_lot}/ajustement",
    response_model=LotResponse
)
def modifier_quantite_stock(
    id_lot: uuid.UUID,
    data: AjustementStock,
    db: Session = Depends(get_db)
):
    return service.ajuster_stock(db, id_lot, data)


# 5. Déclarer une perte
@router.post(
    "/lots/{id_lot}/pertes",
    response_model=LotResponse
)
def enregistrer_perte(
    id_lot: uuid.UUID,
    data: PerteStock,
    db: Session = Depends(get_db)
):
    return service.declarer_perte(db, id_lot, data)


