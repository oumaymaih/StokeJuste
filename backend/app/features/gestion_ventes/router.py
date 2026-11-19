
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.gestion_ventes.schemas import (
    VenteCreate,
    VenteResponse
)
from app.features.gestion_ventes import service


router = APIRouter(
    prefix="/ventes",
    tags=["Gestion des ventes"]
)


# Enregistrer une nouvelle vente
@router.post(
    "/",
    response_model=VenteResponse,
    status_code=201
)
def ajouter_vente(
    data: VenteCreate,
    db: Session = Depends(get_db)
):
    return service.creer_vente(db, data)


# Consulter l'historique des ventes
@router.get("/", response_model=list[VenteResponse])
def historique_ventes(
    id_commerce: uuid.UUID,
    db: Session = Depends(get_db)
):
    return service.lister_ventes(db, id_commerce)


# Consulter les détails d'une vente
@router.get("/{id_vente}", response_model=VenteResponse)
def details_vente(
    id_vente: uuid.UUID,
    id_commerce: uuid.UUID,
    db: Session = Depends(get_db)
):
    return service.consulter_vente(
        db, id_vente, id_commerce
    )

