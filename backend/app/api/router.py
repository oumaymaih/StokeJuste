
from fastapi import APIRouter

from app.features.gestion_produits.router import router as produits_router
from app.features.gestion_stock.router import router as stocks_router
from app.features.gestion_ventes.router import router as ventes_router


api_router = APIRouter()


@api_router.get("/health")
def health_check():
    return {"message": "Connexion au backend réussie !"}


# Gestion des produits
api_router.include_router(produits_router)

# Gestion des stocks
api_router.include_router(stocks_router)

# Gestion des ventes
api_router.include_router(ventes_router)
