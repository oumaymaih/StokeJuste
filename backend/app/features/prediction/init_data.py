import pandas as pd

from pathlib import Path
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

from .database import engine, SessionLocal, Base

from .models import (
    PredictionProduit,
    PredictionModele,
    PredictionHistorique,
    PredictionVenteReelle
)


# ==================================================
# CHEMIN DU REFERENTIEL DES PRODUITS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = BASE_DIR / "data" / "produits.csv"


# ==================================================
# 1. TESTER LA CONNEXION
# ==================================================

def tester_connexion():

    with engine.connect() as connexion:

        resultat = connexion.execute(
            text("SELECT current_database()")
        ).scalar()

        print("Connexion PostgreSQL réussie !")
        print("Base de données :", resultat)


# ==================================================
# 2. CREER LES QUATRE TABLES
# ==================================================

def creer_tables():

    # Créer uniquement les tables qui n'existent pas.
    #
    # Si une table existe déjà, create_all()
    # ne modifie pas sa structure.
    #
    # L'ajout des nouvelles colonnes stock_disponible
    # et quantite_a_commander dans une table existante
    # est effectué par migration_stock.py.

    Base.metadata.create_all(
        bind=engine,
        tables=[
            PredictionProduit.__table__,
            PredictionModele.__table__,
            PredictionHistorique.__table__,
            PredictionVenteReelle.__table__
        ],
        checkfirst=True
    )

    print("Les quatre tables sont disponibles !")


# ==================================================
# 3. ALIMENTER LES PRODUITS
# ==================================================

def alimenter_produits(db):

    produits = pd.read_csv(CSV_PATH)

    for produit in produits.to_dict(orient="records"):

        requete = insert(PredictionProduit).values(
            id_produit=produit["id_produit"],
            nom_produit=produit["nom_produit"],
            categorie=produit["categorie"]
        )

        # Ne pas insérer un produit déjà enregistré

        requete = requete.on_conflict_do_nothing(
            index_elements=["id_produit"]
        )

        db.execute(requete)

    print("Référentiel des produits traité.")


# ==================================================
# 4. ALIMENTER LES INFORMATIONS DU MODELE
# ==================================================

def alimenter_modeles(db):

    requete = insert(PredictionModele).values(
        nom_modele="XGBoost optimisé",
        version="V1",
        mae=12.25,
        rmse=16.36,
        r2=0.93,
        wape=7.01,
        periode_evaluation="Validation 2024",
        statut="actif"
    )

    # Ne pas insérer une version du modèle
    # déjà enregistrée dans PostgreSQL

    requete = requete.on_conflict_do_nothing(
        index_elements=["nom_modele", "version"]
    )

    db.execute(requete)

    print("Informations du modèle traitées.")


# ==================================================
# 5. INITIALISER LE MODULE
# ==================================================

def initialiser():

    print("=" * 60)
    print("INITIALISATION DU MODULE DE PREDICTION")
    print("=" * 60)

    # Vérifier la connexion à PostgreSQL

    tester_connexion()

    # Créer les tables manquantes

    creer_tables()

    # Ouvrir une session

    db = SessionLocal()

    try:

        # Alimenter le référentiel des produits

        alimenter_produits(db)

        # Alimenter les informations du modèle

        alimenter_modeles(db)

        # Valider les insertions

        db.commit()

        # Afficher le nombre de lignes par table

        print("\nCONTENU DES TABLES")

        tables = [
            PredictionProduit,
            PredictionModele,
            PredictionHistorique,
            PredictionVenteReelle
        ]

        for table in tables:

            print(
                table.__tablename__,
                ":",
                db.query(table).count(),
                "lignes"
            )

        print("\nInitialisation terminée avec succès !")

    except Exception:

        # Annuler les insertions non validées
        # en cas d'erreur

        db.rollback()
        raise

    finally:

        # Fermer la session PostgreSQL

        db.close()


# ==================================================
# 6. EXECUTION DU SCRIPT
# ==================================================

if __name__ == "__main__":

    initialiser()