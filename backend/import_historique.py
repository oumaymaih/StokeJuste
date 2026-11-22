
import csv
import uuid
from pathlib import Path
from datetime import date
from decimal import Decimal

from app.db.session import SessionLocal
from app.models.produit import Produit
from app.models.historique_vente import HistoriqueVente

COMMERCE_ID = uuid.UUID(
    "071bc3e6-2688-48e2-a1bd-e6cdf7192e1f"
)

CSV_PATH = Path(__file__).parent / "dataset_supermarket_maroc.csv"


def convertir_prix(valeur):
    return Decimal(
        valeur.replace("MAD", "")
        .replace(" ", "")
        .replace(",", ".")
        .strip()
    )


db = SessionLocal()

try:
    # 1. Récupérer les produits du commerce
    produits = db.query(Produit).filter_by(
        id_commerce=COMMERCE_ID
    ).all()

    produits_par_nom = {
        p.nom_produit.strip(): p.id_produit
        for p in produits
    }

    # 2. Récupérer les historiques existants
    historiques = (
        db.query(HistoriqueVente)
        .join(Produit)
        .filter(Produit.id_commerce == COMMERCE_ID)
        .all()
    )

    cles_existantes = {
        (h.id_produit, h.periode)
        for h in historiques
    }

    ajoutes = 0
    ignores = 0

    # 3. Lire et importer le CSV
    with open(
        CSV_PATH, encoding="utf-8-sig", newline=""
    ) as fichier:

        lecteur = csv.DictReader(fichier)

        for ligne in lecteur:
            nom = ligne["Produit"].strip()
            periode = ligne["Année / Mois / Semaine"].strip()

            if nom not in produits_par_nom:
                raise ValueError(
                    f"Produit introuvable : {nom}"
                )

            id_produit = produits_par_nom[nom]
            cle = (id_produit, periode)

            if cle in cles_existantes:
                ignores += 1
                continue

            historique = HistoriqueVente(
                id_produit=id_produit,
                periode=periode,
                ventes_s1=int(ligne["Ventes S-1"]),
                ventes_s2=int(ligne["Ventes S-2"]),
                ventes_s3=int(ligne["Ventes S-3"]),
                ventes_s4=int(ligne["Ventes S-4"]),
                promotion=ligne["Promotion"].strip().lower() == "oui",
                prix=convertir_prix(ligne["Prix"]),
                nombre_lots=int(ligne["Nombre de lots"]),
                date_production=date.fromisoformat(
                    ligne["Date de production"]
                ),
                date_peremption=date.fromisoformat(
                    ligne["Date de péremption"]
                ),
                quantite_predite=int(ligne["Quantité prédite"])
            )

            db.add(historique)
            cles_existantes.add(cle)
            ajoutes += 1

    # 4. Enregistrer dans PostgreSQL
    db.commit()

    print("Importation terminée !")
    print("Observations ajoutées :", ajoutes)
    print("Observations ignorées :", ignores)

except Exception as e:
    db.rollback()
    print("Erreur :", e)

finally:
    db.close()
