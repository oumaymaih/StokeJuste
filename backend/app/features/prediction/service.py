import joblib
import pandas as pd

from pathlib import Path
from functools import lru_cache
from math import isfinite, ceil

from sqlalchemy.orm import Session

from .schemas import PredictionRequest
from .models import PredictionVenteReelle


# ==================================================
# CHEMIN DU MODELE
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = (
    BASE_DIR
    / "notebook"
    / "models"
    / "stockjuste_xgboost.pkl"
)


# ==================================================
# LES 14 FEATURES ATTENDUES
# ==================================================

FEATURES = [
    "produit",
    "ventes_s1",
    "ventes_s2",
    "ventes_s3",
    "ventes_s4",
    "promotion",
    "prix",
    "nombre_lots",
    "annee",
    "mois_num",
    "semaine",
    "moyenne_4_semaines",
    "tendance",
    "duree_vie_jours"
]


# ==================================================
# 1. CHARGER LE PIPELINE
# ==================================================

@lru_cache(maxsize=1)
def charger_modele():

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            "Le fichier du modèle est introuvable."
        )

    pipeline = joblib.load(MODEL_PATH)

    if list(pipeline.feature_names_in_) != FEATURES:

        raise ValueError(
            "Les features du pipeline ne correspondent pas."
        )

    return pipeline


# ==================================================
# 2. DETERMINER LE NOMBRE DE SEMAINES DU MOIS
# ==================================================

def nombre_semaines(
    db: Session,
    annee: int,
    mois: int
):

    # Pour la simulation 2026, utiliser le même
    # découpage mensuel que le dataset 2025.

    annee_reference = (
        2025 if annee == 2026 else annee
    )

    resultat = db.query(
        PredictionVenteReelle.semaine
    ).filter(
        PredictionVenteReelle.annee
        == annee_reference,

        PredictionVenteReelle.mois_num
        == mois
    ).distinct().all()

    semaines = sorted(
        ligne[0] for ligne in resultat
    )

    if not semaines:

        raise ValueError(
            f"Calendrier indisponible : "
            f"{annee}/{mois:02d}"
        )

    if semaines != list(
        range(1, max(semaines) + 1)
    ):

        raise ValueError(
            f"Calendrier incomplet : "
            f"{annee}/{mois:02d}"
        )

    return max(semaines)


# ==================================================
# 3. DETERMINER LA PERIODE PRECEDENTE
# ==================================================

def periode_precedente(
    db: Session,
    annee: int,
    mois: int,
    semaine: int
):

    # Cas 1 : rester dans le même mois

    if semaine > 1:

        return annee, mois, semaine - 1

    # Cas 2 : revenir au mois précédent

    if mois == 1:

        annee -= 1
        mois = 12

    else:

        mois -= 1

    # Dernière semaine du mois précédent

    semaine = nombre_semaines(
        db,
        annee,
        mois
    )

    return annee, mois, semaine


# ==================================================
# 4. RECUPERER LES QUATRE VENTES PRECEDENTES
# ==================================================

def recuperer_ventes_precedentes(
    db: Session,
    id_produit: str,
    annee: int,
    mois_num: int,
    semaine: int
):

    # Vérifier que la semaine demandée existe

    maximum = nombre_semaines(
        db,
        annee,
        mois_num
    )

    if semaine > maximum:

        raise ValueError(
            f"La semaine S{semaine} n'existe pas "
            f"dans le calendrier de ce mois."
        )

    ventes = {}

    periodes_manquantes = []

    historique_simule = False

    periode = (
        annee,
        mois_num,
        semaine
    )

    # Rechercher les quatre périodes précédentes

    for i in range(1, 5):

        periode = periode_precedente(
            db,
            *periode
        )

        a, m, s = periode

        vente = db.query(
            PredictionVenteReelle
        ).filter_by(
            id_produit=id_produit,
            annee=a,
            mois_num=m,
            semaine=s
        ).first()

        if vente is None:

            periodes_manquantes.append(
                f"{a}/{m:02d}/S{s}"
            )

        else:

            ventes[f"ventes_s{i}"] = (
                vente.quantite_vendue
            )

            if vente.jeu_donnees == "Simulation":

                historique_simule = True

    # Ne pas remplacer les ventes manquantes par zéro

    if periodes_manquantes:

        raise ValueError(
            "Historique insuffisant. "
            "Ventes manquantes : "
            + ", ".join(periodes_manquantes)
        )

    return ventes, historique_simule


# ==================================================
# 5. PREPARER LES 14 FEATURES
# ==================================================

def preparer_donnees(
    donnees: PredictionRequest,
    nom_produit: str
):

    # Calculer la moyenne des quatre dernières semaines

    moyenne = (
        donnees.ventes_s1
        + donnees.ventes_s2
        + donnees.ventes_s3
        + donnees.ventes_s4
    ) / 4

    # Calculer la tendance des ventes

    tendance = (
        donnees.ventes_s1
        - donnees.ventes_s4
    )

    # Construire uniquement les 14 features
    # attendues par le modèle XGBoost.
    #
    # Le stock disponible n'est pas une feature
    # du modèle de prédiction.

    features = {
        "produit": nom_produit,

        "ventes_s1": donnees.ventes_s1,
        "ventes_s2": donnees.ventes_s2,
        "ventes_s3": donnees.ventes_s3,
        "ventes_s4": donnees.ventes_s4,

        "promotion": donnees.promotion,
        "prix": donnees.prix,
        "nombre_lots": donnees.nombre_lots,

        "annee": donnees.annee,
        "mois_num": donnees.mois_num,
        "semaine": donnees.semaine,

        "moyenne_4_semaines": moyenne,
        "tendance": tendance,

        "duree_vie_jours": donnees.duree_vie_jours
    }

    return pd.DataFrame(
        [features],
        columns=FEATURES
    )


# ==================================================
# 6. APPLIQUER LE PREPROCESSING ET PREDIRE
# ==================================================

def predire_quantite(X: pd.DataFrame):

    pipeline = charger_modele()

    # Vérifier les produits reconnus

    produits_connus = (
        pipeline.named_steps["preprocessing"]
        .named_transformers_["cat"]
        .categories_[0]
    )

    if X["produit"].iloc[0] not in produits_connus:

        raise ValueError(
            "Produit non reconnu par le modèle."
        )

    # OneHotEncoder + XGBoost

    prediction = float(
        pipeline.predict(X)[0]
    )

    # Vérifier la validité de la prédiction

    if not isfinite(prediction):

        raise ValueError(
            "La prédiction obtenue est invalide."
        )

    # Empêcher une quantité prédite négative

    prediction = max(0.0, prediction)

    return {
        "quantite_predite": round(prediction, 2),
        "borne_inferieure": None,
        "borne_superieure": None
    }


# ==================================================
# 7. CALCULER LA QUANTITE A COMMANDER
# ==================================================

def calculer_quantite_commande(
    quantite_predite: float,
    stock_disponible: int
) -> int:

    """
    Calculer la quantité recommandée à commander
    à partir des ventes prévues et du stock disponible.

    Formule :
        Quantité à commander =
        max(0, ceil(quantité prédite) - stock disponible)
    """

    # Vérifier que la quantité prédite est valide

    if not isfinite(quantite_predite):

        raise ValueError(
            "La quantité prédite est invalide."
        )

    if quantite_predite < 0:

        raise ValueError(
            "La quantité prédite doit être positive ou nulle."
        )

    # Vérifier que le stock est un nombre entier

    if (
        not isinstance(stock_disponible, int)
        or isinstance(stock_disponible, bool)
    ):

        raise ValueError(
            "Le stock disponible doit être un nombre entier."
        )

    # Vérifier que le stock n'est pas négatif

    if stock_disponible < 0:

        raise ValueError(
            "Le stock disponible doit être positif ou nul."
        )

    # Arrondir la demande prévue à l'entier supérieur

    besoin_prevu = ceil(quantite_predite)

    # Calculer la quantité manquante
    # sans obtenir une valeur négative

    quantite_a_commander = max(
        0,
        besoin_prevu - stock_disponible
    )

    # Retourner la recommandation de commande

    return quantite_a_commander