import pandas as pd
from pathlib import Path

# 1. Définir les chemins
BASE_DIR = Path(__file__).resolve().parents[1]

SOURCE = BASE_DIR / "notebook" / "dataset_stockjuste_nettoye.csv"
DESTINATION = BASE_DIR / "data" / "produits.csv"

# 2. Charger le dataset nettoyé
df = pd.read_csv(SOURCE)

# 3. Extraire les produits uniques
produits = df[['produit']].drop_duplicates().copy()

# 4. Trier les produits
produits = produits.sort_values('produit').reset_index(drop=True)

# 5. Renommer la colonne
produits = produits.rename(columns={
    'produit': 'nom_produit'
})

# 6. Attribuer un identifiant unique
produits.insert(
    0,
    'id_produit',
    [f'P{i:03d}' for i in range(1, len(produits) + 1)]
)

# 7. Associer les catégories aux 10 produits
categories = {
    'Ain Saiss': 'Boissons',
    'Biscuits Merendina': 'Biscuits',
    'Ciel': 'Boissons',
    'Couscous Dari': 'Épicerie',
    'Fromage La Vache Qui Rit': 'Produits laitiers',
    'Huile de table Lesieur': 'Épicerie',
    'Lait UHT Centrale': 'Produits laitiers',
    'Sidi Ali': 'Boissons',
    'Thé vert Sultan': 'Épicerie',
    'Yaourt Jaouda': 'Produits laitiers'
}

produits['categorie'] = (
    produits['nom_produit']
    .map(categories)
    .fillna('À compléter')
)

# 8. Créer le dossier de destination
DESTINATION.parent.mkdir(parents=True, exist_ok=True)

# 9. Enregistrer ou remplacer le fichier CSV existant
produits.to_csv(
    DESTINATION,
    index=False,
    encoding='utf-8-sig'
)

# 10. Afficher les résultats
print("Fichier produits.csv généré avec succès !")
print("Nombre de produits :", len(produits))
print("Emplacement :", DESTINATION)

print("\nRéférentiel des produits :")
print(produits.to_string(index=False))