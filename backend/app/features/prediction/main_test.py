
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .router import router


app = FastAPI(
    title="StockJuste - Module Prediction",
    version="1.0"
)


app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],

    allow_credentials=False,

    allow_methods=["GET", "POST"],

    allow_headers=["*"]
)


app.include_router(router)


@app.get("/")
def accueil():

    return {
        "message": "Module de prediction StockJuste",
        "statut": "operationnel"
    }
