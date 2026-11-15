from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/health")
def health_check():
    return {"message": "Connexion au backend réussie !"}