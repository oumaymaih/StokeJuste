import os

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# ==================================================
# 1. CHARGER LE FICHIER .ENV
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(
    BASE_DIR / ".env",
    override=True
)


# ==================================================
# 2. RECUPERER L'URL DE CONNEXION
# ==================================================

DATABASE_URL = os.getenv(
    "PREDICTION_DATABASE_URL",
    ""
).strip()

if not DATABASE_URL:

    raise ValueError(
        "PREDICTION_DATABASE_URL est manquante."
    )


# ==================================================
# 3. CONNEXION A POSTGRESQL SUR RAILWAY
# ==================================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)


# ==================================================
# 4. CREATION DES SESSIONS
# ==================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==================================================
# 5. BASE INDEPENDANTE DU MODULE PREDICTION
# ==================================================

# Cette base contient les quatre tables :
#
# - prediction_produits
# - prediction_modeles
# - prediction_historique
# - prediction_ventes_reelles

Base = declarative_base()


# ==================================================
# 6. GESTION DES SESSIONS AVEC FASTAPI
# ==================================================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()