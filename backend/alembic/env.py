
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

from app.core.config import settings
from app.db.base import Base

# Importer les 7 modèles pour qu'Alembic les détecte
from app.models.commerce import Commercant, Commerce
from app.models.produit import Produit
from app.models.lot_stock import LotStock
from app.models.mouvement_stock import MouvementStock
from app.models.vente import Vente
from app.models.ligne_vente import LigneVente
from app.models.historique_vente import HistoriqueVente 

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Utiliser l'adresse PostgreSQL du fichier .env
config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL.replace("%", "%%")
)

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
