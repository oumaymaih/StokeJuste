
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.produit import Produit
from app.models.historique_vente import HistoriqueVente


router = APIRouter(
    prefix="/historique-ventes",
    tags=["Historique des ventes"]
)


@router.get("/")
def lister_historiques(
    id_commerce: uuid.UUID,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    limit = max(1, min(limit, 1530))

    resultats = (
        db.query(HistoriqueVente, Produit.nom_produit)
        .join(
            Produit,
            HistoriqueVente.id_produit == Produit.id_produit
        )
        .filter(Produit.id_commerce == id_commerce)
        .order_by(
            Produit.nom_produit,
            HistoriqueVente.periode
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "produit": nom,
            "periode": h.periode,
            "ventes_s1": h.ventes_s1,
            "ventes_s2": h.ventes_s2,
            "ventes_s3": h.ventes_s3,
            "ventes_s4": h.ventes_s4,
            "promotion": h.promotion,
            "prix": h.prix,
            "nombre_lots": h.nombre_lots,
            "date_production": h.date_production,
            "date_peremption": h.date_peremption,
            "quantite_predite": h.quantite_predite
        }
        for h, nom in resultats
    ]
