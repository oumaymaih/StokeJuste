
import uuid
from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.commerce import Commerce
from app.models.produit import Produit
from app.models.lot_stock import LotStock
from app.models.mouvement_stock import MouvementStock
from app.models.vente import Vente
from app.models.ligne_vente import LigneVente

from app.features.gestion_ventes.schemas import VenteCreate
from sqlalchemy.orm import selectinload


# Enregistrer une vente avec la méthode FEFO
def creer_vente(db: Session, data: VenteCreate):

    try:
        # 1. Vérifier le commerce
        commerce = db.get(Commerce, data.id_commerce)

        if commerce is None:
            raise HTTPException(
                status_code=404,
                detail="Commerce introuvable"
            )

        # 2. Regrouper les quantités du même produit
        demandes = {}

        for article in data.articles:
            demandes[article.id_produit] = (
                demandes.get(article.id_produit, 0)
                + article.quantite
            )

        # 3. Créer la vente
        vente = Vente(
            id_commerce=data.id_commerce,
            montant_total=Decimal("0.00"),
            statut="VALIDEE"
        )

        db.add(vente)
        db.flush()

        total = Decimal("0.00")
        lignes_creees = []

        # Tri stable pour limiter les conflits concurrents
        for id_produit in sorted(demandes, key=str):

            quantite_demandee = demandes[id_produit]

            # 4. Vérifier le produit
            produit = db.get(Produit, id_produit)

            if (
                produit is None
                or not produit.est_actif
                or produit.id_commerce != data.id_commerce
            ):
                raise HTTPException(
                    status_code=404,
                    detail="Produit introuvable ou archivé"
                )

            # 5. Sélectionner les lots disponibles (FEFO)
            requete = (
                select(LotStock)
                .where(
                    LotStock.id_produit == id_produit,
                    LotStock.quantite_restante > 0
                )
                .order_by(
                    LotStock.date_peremption.asc().nulls_last(),
                    LotStock.date_reception.asc(),
                    LotStock.id_lot.asc()
                )
                .with_for_update()
            )

            # Exclure les lots périmés
            if produit.est_perissable:
                requete = requete.where(
                    LotStock.date_peremption >= date.today()
                )
            else:
                requete = requete.where(
                    (LotStock.date_peremption >= date.today())
                    | LotStock.date_peremption.is_(None)
                )

            lots = db.scalars(requete).all()

            disponible = sum(
                lot.quantite_restante for lot in lots
            )

            if disponible < quantite_demandee:
                raise HTTPException(
                    status_code=422,
                    detail=f"Stock insuffisant pour {produit.nom_produit}"
                )

            # 6. Prélever les quantités lot par lot
            restant_a_vendre = quantite_demandee

            for lot in lots:

                if restant_a_vendre == 0:
                    break

                quantite_prelevee = min(
                    restant_a_vendre,
                    lot.quantite_restante
                )

                lot.quantite_restante -= quantite_prelevee

                prix = Decimal(str(produit.prix_vente))
                sous_total = prix * quantite_prelevee

                # Enregistrer la ligne de vente
                ligne = LigneVente(
                    id_vente=vente.id_vente,
                    id_produit=id_produit,
                    id_lot=lot.id_lot,
                    quantite=quantite_prelevee,
                    prix_unitaire=prix,
                    sous_total=sous_total
                )

                db.add(ligne)

                # Enregistrer le mouvement de stock
                mouvement = MouvementStock(
                    id_lot=lot.id_lot,
                    type_mouvement="VENTE",
                    variation_quantite=-quantite_prelevee,
                    motif="Vente de produit"
                )

                db.add(mouvement)
                lignes_creees.append(ligne)

                total += sous_total
                restant_a_vendre -= quantite_prelevee

        # 7. Finaliser la vente
        vente.montant_total = total

        db.flush()

        # Préparer la réponse avec les lignes
        resultat = {
            "id_vente": vente.id_vente,
            "id_commerce": vente.id_commerce,
            "date_vente": vente.date_vente,
            "montant_total": vente.montant_total,
            "statut": vente.statut,
            "lignes": [
                {
                    "id_ligne": ligne.id_ligne,
                    "id_vente": ligne.id_vente,
                    "id_produit": ligne.id_produit,
                    "id_lot": ligne.id_lot,
                    "quantite": ligne.quantite,
                    "prix_unitaire": ligne.prix_unitaire,
                    "sous_total": ligne.sous_total
                }
                for ligne in lignes_creees
            ]
        }

        # 8. Enregistrer toutes les opérations ensemble
        db.commit()

        return resultat

    except Exception:
        db.rollback()
        raise


# 2. Consulter l'historique des ventes d'un commerce
def lister_ventes(db: Session, id_commerce: uuid.UUID):
    ventes = db.scalars(
        select(Vente)
        .options(selectinload(Vente.lignes))
        .where(Vente.id_commerce == id_commerce)
        .order_by(Vente.date_vente.desc())
    ).all()

    return ventes


# 3. Consulter les détails d'une vente
def consulter_vente(
    db: Session,
    id_vente: uuid.UUID,
    id_commerce: uuid.UUID
):
    vente = db.scalar(
        select(Vente)
        .options(selectinload(Vente.lignes))
        .where(
            Vente.id_vente == id_vente,
            Vente.id_commerce == id_commerce
        )
    )

    if vente is None:
        raise HTTPException(
            status_code=404,
            detail="Vente introuvable"
        )

    return vente
