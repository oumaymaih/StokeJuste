from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from sqlalchemy.orm import Session

from .database import get_db

from .models import (
    PredictionProduit,
    PredictionModele,
    PredictionHistorique
)

from .schemas import (
    PredictionAutoRequest,
    PredictionRequest,
    PredictionResponse
)

from .service import (
    recuperer_ventes_precedentes,
    preparer_donnees,
    predire_quantite,
    calculer_quantite_commande
)


router = APIRouter(
    prefix="/api/prediction",
    tags=["Prediction"]
)


# ==================================================
# 1. CONSULTER LES PRODUITS
# ==================================================

@router.get("/produits")
def consulter_produits(
    db: Session = Depends(get_db)
):

    produits = (
        db.query(PredictionProduit)
        .order_by(PredictionProduit.id_produit)
        .all()
    )

    return produits


# ==================================================
# 2. CONSULTER LES PERFORMANCES
# ==================================================

@router.get("/performances")
def consulter_performances(
    db: Session = Depends(get_db)
):

    modele = (
        db.query(PredictionModele)
        .filter_by(
            nom_modele="XGBoost optimisé",
            version="V1",
            statut="actif"
        )
        .first()
    )

    if modele is None:

        raise HTTPException(
            status_code=404,
            detail="Aucun modèle actif trouvé"
        )

    return modele


# ==================================================
# 3. EFFECTUER UNE PREDICTION AUTOMATIQUE
# ==================================================

@router.post(
    "/predire",
    response_model=PredictionResponse,
    status_code=201
)
def effectuer_prediction(
    donnees: PredictionAutoRequest,
    db: Session = Depends(get_db)
):

    # ETAPE 1 : Récupérer le produit

    produit = db.get(
        PredictionProduit,
        donnees.id_produit
    )

    if produit is None:

        raise HTTPException(
            status_code=404,
            detail="Produit introuvable"
        )

    # ETAPE 2 : Récupérer le modèle actif

    modele = (
        db.query(PredictionModele)
        .filter_by(
            nom_modele="XGBoost optimisé",
            version="V1",
            statut="actif"
        )
        .first()
    )

    if modele is None:

        raise HTTPException(
            status_code=503,
            detail="Modèle indisponible"
        )

    try:

        # ETAPE 3 : Récupérer automatiquement
        # les quatre ventes précédentes

        ventes, historique_simule = (
            recuperer_ventes_precedentes(
                db=db,
                id_produit=donnees.id_produit,
                annee=donnees.annee,
                mois_num=donnees.mois_num,
                semaine=donnees.semaine
            )
        )

        # ETAPE 4 : Construire les 13 informations
        # 9 informations saisies par le commerçant
        # et 4 ventes récupérées depuis PostgreSQL

        donnees_completes = PredictionRequest(
            **donnees.model_dump(),
            **ventes
        )

        # ETAPE 5 : Préparer les 14 features
        # attendues par le modèle XGBoost
        #
        # Le stock disponible n'est pas transmis
        # au modèle de prédiction.

        X = preparer_donnees(
            donnees_completes,
            produit.nom_produit
        )

        # ETAPE 6 : Préparer l'enregistrement
        #
        # Le stock disponible est déjà inclus dans
        # donnees_completes.model_dump().

        historique = PredictionHistorique(

            **donnees_completes.model_dump(),

            id_modele=modele.id_modele,

            moyenne_4_semaines=float(
                X["moyenne_4_semaines"].iloc[0]
            ),

            tendance=int(
                X["tendance"].iloc[0]
            ),

            quantite_predite=None,

            quantite_a_commander=None,

            borne_inferieure=None,
            borne_superieure=None
        )

        # ETAPE 7 : INSERT dans PostgreSQL

        db.add(historique)
        db.flush()

        # ETAPE 8 : Preprocessing et prédiction

        resultat = predire_quantite(X)

        # Calculer la quantité recommandée à commander
        #
        # Quantité à commander =
        # max(0, ceil(quantité prédite) - stock disponible)

        quantite_a_commander = calculer_quantite_commande(
            quantite_predite=resultat["quantite_predite"],
            stock_disponible=donnees.stock_disponible
        )

        # Vérifier la compatibilité avec le type
        # INTEGER de PostgreSQL

        if quantite_a_commander > 2147483647:

            raise ValueError(
                "La quantité à commander dépasse "
                "la valeur maximale autorisée."
            )

        # ETAPE 9 : UPDATE de la même ligne

        historique.quantite_predite = (
            resultat["quantite_predite"]
        )

        historique.quantite_a_commander = (
            quantite_a_commander
        )

        historique.borne_inferieure = (
            resultat["borne_inferieure"]
        )

        historique.borne_superieure = (
            resultat["borne_superieure"]
        )

        # ETAPE 10 : Préparer et valider la réponse

        db.flush()

        reponse = PredictionResponse(

            id_prediction=historique.id_prediction,

            id_produit=produit.id_produit,

            nom_produit=produit.nom_produit,

            quantite_predite=historique.quantite_predite,

            stock_disponible=historique.stock_disponible,

            quantite_a_commander=(
                historique.quantite_a_commander
            ),

            borne_inferieure=historique.borne_inferieure,

            borne_superieure=historique.borne_superieure,

            ventes_s1=historique.ventes_s1,
            ventes_s2=historique.ventes_s2,
            ventes_s3=historique.ventes_s3,
            ventes_s4=historique.ventes_s4,

            historique_simule=historique_simule
        )

        # Valider la transaction PostgreSQL

        db.commit()

    except ValueError as erreur:

        db.rollback()

        raise HTTPException(
            status_code=422,
            detail=str(erreur)
        )

    except FileNotFoundError:

        db.rollback()

        raise HTTPException(
            status_code=503,
            detail="Fichier du modèle introuvable"
        )

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Erreur pendant la prédiction "
                "ou son enregistrement"
            )
        )

    # ETAPE 11 : Retourner le résultat au frontend

    return reponse


# ==================================================
# 4. CONSULTER ET FILTRER L'HISTORIQUE
# ==================================================

@router.get("/historique")
def consulter_historique(

    id_produit: str | None = None,

    annee: int | None = Query(
        default=None,
        ge=2000,
        le=2100
    ),

    mois_num: int | None = Query(
        default=None,
        ge=1,
        le=12
    ),

    db: Session = Depends(get_db)
):

    requete = (
        db.query(
            PredictionHistorique,
            PredictionProduit.nom_produit
        )
        .join(
            PredictionProduit,

            PredictionHistorique.id_produit
            == PredictionProduit.id_produit
        )
        .filter(
            PredictionHistorique.quantite_predite
            .is_not(None)
        )
    )

    # Filtrer par produit

    if id_produit is not None:

        requete = requete.filter(
            PredictionHistorique.id_produit
            == id_produit
        )

    # Filtrer par année

    if annee is not None:

        requete = requete.filter(
            PredictionHistorique.annee
            == annee
        )

    # Filtrer par mois

    if mois_num is not None:

        requete = requete.filter(
            PredictionHistorique.mois_num
            == mois_num
        )

    # Trier les prédictions

    resultats = requete.order_by(
        PredictionHistorique.annee.desc(),
        PredictionHistorique.mois_num.desc(),
        PredictionHistorique.semaine.desc(),
        PredictionHistorique.date_prediction.desc()
    ).all()

    # Construire la réponse

    return [

        {
            "id_prediction": h.id_prediction,
            "id_produit": h.id_produit,
            "nom_produit": nom,

            "annee": h.annee,
            "mois_num": h.mois_num,
            "semaine": h.semaine,

            "ventes_s1": h.ventes_s1,
            "ventes_s2": h.ventes_s2,
            "ventes_s3": h.ventes_s3,
            "ventes_s4": h.ventes_s4,

            "quantite_predite": h.quantite_predite,

            "stock_disponible": h.stock_disponible,

            "quantite_a_commander": h.quantite_a_commander,

            "quantite_reelle": h.quantite_reelle,

            "borne_inferieure": h.borne_inferieure,
            "borne_superieure": h.borne_superieure,

            "date_prediction": h.date_prediction
        }

        for h, nom in resultats
    ]