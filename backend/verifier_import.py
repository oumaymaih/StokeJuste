
import uuid
from sqlalchemy import func

from app.db.session import SessionLocal
from app.models.produit import Produit
from app.models.historique_vente import HistoriqueVente

COMMERCE_ID = uuid.UUID(
    "071bc3e6-2688-48e2-a1bd-e6cdf7192e1f"
)

db = SessionLocal()

try:
    nb_produits = db.query(Produit).filter(
        Produit.id_commerce == COMMERCE_ID
    ).count()

    nb_historiques = (
        db.query(HistoriqueVente)
        .join(Produit)
        .filter(Produit.id_commerce == COMMERCE_ID)
        .count()
    )

    print("Produits :", nb_produits)
    print("Observations historiques :", nb_historiques)

    print("\nHistorique par produit :")

    resultats = (
        db.query(
            Produit.nom_produit,
            func.count(HistoriqueVente.id_historique)
        )
        .join(
            HistoriqueVente,
            Produit.id_produit == HistoriqueVente.id_produit
        )
        .filter(Produit.id_commerce == COMMERCE_ID)
        .group_by(Produit.nom_produit)
        .order_by(Produit.nom_produit)
        .all()
    )

    for nom, nombre in resultats:
        print(f"{nom} : {nombre} observations")

finally:
    db.close()
