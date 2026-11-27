from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router

# Import du router du module de prediction
from app.features.prediction.router import router as prediction_router

app = FastAPI(title="StokeJuste API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router commun
app.include_router(api_router, prefix="/api")

# Router du module de prediction
app.include_router(prediction_router)