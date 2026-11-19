
from datetime import date
import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.produit import Produit
from app.models.lot_stock import LotStock
from app.models.mouvement_stock import MouvementStock
from app.features.gestion_stock.schemas import LotCreate


# 1. Réceptionner un nouveau lot
def receptionner_lot(db: Session, data: LotCreate):

    # Vérifier que le produit existe et est actif
    produit = db.get(Produit, data.id_produit)

    if produit is None or not produit.est_actif:
        raise HTTPException(
            status_code=404,
            detail="Produit introuvable ou archivé"
        )

    # Vérifier la date de péremption
    if produit.est_perissable and data.date_peremption is None:
        raise HTTPException(
            status_code=422,
            detail="Date de péremption obligatoire"
        )

    if data.date_peremption and data.date_peremption < date.today():
        raise HTTPException(
            status_code=422,
            detail="Impossible de réceptionner un lot périmé"
        )

    # Générer un numéro de lot si absent
    numero_lot = data.numero_lot or f"LOT-{uuid.uuid4().hex[:8].upper()}"

    # Créer le lot
    lot = LotStock(
        id_produit=data.id_produit,
        numero_lot=numero_lot,
        quantite_recue=data.quantite_recue,
        quantite_restante=data.quantite_recue,
        date_production=data.date_production,
        date_peremption=data.date_peremption
    )

    try:
        db.add(lot)
        db.flush()

        # Créer automatiquement le mouvement d'entrée
        mouvement = MouvementStock(
            id_lot=lot.id_lot,
            type_mouvement="ENTREE",
            variation_quantite=data.quantite_recue,
            motif="Réception de stock"
        )

        db.add(mouvement)

        # Enregistrer les deux opérations ensemble
        db.commit()
        db.refresh(lot)

        return lot

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Erreur lors de la réception du lot"
        )


# 2. Consulter les lots d'un produit
def lister_lots(db: Session, id_produit: uuid.UUID):

    return db.scalars(
        select(LotStock)
        .where(LotStock.id_produit == id_produit)
        .order_by(
            LotStock.date_peremption.asc().nulls_last(),
            LotStock.date_reception.asc()
        )
    ).all()


# 3. Consulter l'historique des mouvements d'un lot
def lister_mouvements(db: Session, id_lot: uuid.UUID):

    return db.scalars(
        select(MouvementStock)
        .where(MouvementStock.id_lot == id_lot)
        .order_by(MouvementStock.date_mouvement.desc())
    ).all()


# 4. Ajuster la quantité d'un lot
def ajuster_stock(
    db: Session,
    id_lot: uuid.UUID,
    data
):
    try:
        # Verrouiller le lot pendant la modification
        lot = db.scalar(
            select(LotStock)
            .where(LotStock.id_lot == id_lot)
            .with_for_update()
        )

        if lot is None:
            raise HTTPException(
                status_code=404,
                detail="Lot introuvable"
            )

        if data.nouvelle_quantite > lot.quantite_recue:
            raise HTTPException(
                status_code=422,
                detail="La quantité ne peut pas dépasser la quantité reçue"
            )

        variation = data.nouvelle_quantite - lot.quantite_restante

        if variation == 0:
            return lot

        # Mettre à jour le stock
        lot.quantite_restante = data.nouvelle_quantite

        # Enregistrer le mouvement
        mouvement = MouvementStock(
            id_lot=id_lot,
            type_mouvement="AJUSTEMENT",
            variation_quantite=variation,
            motif=data.motif
        )

        db.add(mouvement)
        db.commit()
        db.refresh(lot)

        return lot

    except Exception:
        db.rollback()
        raise


# 5. Déclarer une perte de stock
def declarer_perte(
    db: Session,
    id_lot: uuid.UUID,
    data
):
    try:
        # Verrouiller le lot pendant l'opération
        lot = db.scalar(
            select(LotStock)
            .where(LotStock.id_lot == id_lot)
            .with_for_update()
        )

        if lot is None:
            raise HTTPException(
                status_code=404,
                detail="Lot introuvable"
            )

        # Vérifier la quantité disponible
        if data.quantite_perdue > lot.quantite_restante:
            raise HTTPException(
                status_code=422,
                detail="Quantité perdue supérieure au stock disponible"
            )

        # Diminuer la quantité restante
        lot.quantite_restante -= data.quantite_perdue

        # Enregistrer automatiquement le mouvement
        mouvement = MouvementStock(
            id_lot=id_lot,
            type_mouvement="PERTE",
            variation_quantite=-data.quantite_perdue,
            motif=data.motif
        )

        db.add(mouvement)
        db.commit()
        db.refresh(lot)

        return lot

    except Exception:
        db.rollback()
        raise
