
import csv
from pathlib import Path
from decimal import Decimal

from app.db.session import SessionLocal
from app.models.produit import Produit
from app.models.commerce import Commerce

COMMERCE_ID = "071bc3e6-2688-48e2-a1bd-e6cdf7192e1f"
CSV_PATH = Path(__file__).parent / "dataset_supermarket_maroc.csv"


def convertir_prix(valeur):
    prix = valeur.replace("MAD", "").replace(" ", "")
    prix = prix.replace(",", ".")
    return Decimal(prix.strip())


# Lecture du dataset
with open(CSV_PATH, encoding="utf-8-sig", newline="") as fichier:
    lignes = list(csv.DictReader(fichier))

# Conserver la dernière observation de chaque produit
produits_uniques = {}

for ligne in lignes:
    nom = ligne["Produit"].strip()
    produits_uniques[nom] = ligne

db = SessionLocal()

try:
    commerce = db.get(Commerce, COMMERCE_ID)

    if commerce is None:
        raise ValueError("Commerce introuvable")

    ajoutes = 0
    ignores = 0

    for numero, (nom, ligne) in enumerate(
        sorted(produits_uniques.items()), start=1
    ):
        code = f"DEMO-{numero:03d}"

        # Éviter les doublons
        existe = db.query(Produit).filter_by(
            id_commerce=commerce.id_commerce,
            code_produit=code
        ).first()

        if existe:
            ignores += 1
            continue

        produit = Produit(
            id_commerce=commerce.id_commerce,
            code_produit=code,
            nom_produit=nom,
            categorie="Non classé",
            marque=None,
            image_url=None,
            prix_vente=convertir_prix(ligne["Prix"]),
            seuil_minimal=0,
            est_perissable=False,
            est_actif=True
        )

        db.add(produit)
        ajoutes += 1

    db.commit()

    print("Importation terminée !")
    print("Produits ajoutés :", ajoutes)
    print("Produits déjà présents :", ignores)

except Exception as e:
    db.rollback()
    print("Erreur :", e)

finally:
    db.close()
