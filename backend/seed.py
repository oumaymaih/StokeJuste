"""Données fictives StockJuste : python seed.py --apply (depuis backend/).

Ne crée pas de compte permettant une connexion : le mot de passe du commerçant
est volontairement désactivé. À remplacer via le flux d'inscription de l'app.
"""
import argparse
import uuid
from decimal import Decimal
from urllib.parse import urlsplit

from sqlalchemy import select
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.commerce import Commercant, Commerce
from app.models.produit import Produit
from app.models.lot_stock import LotStock
from app.models.mouvement_stock import MouvementStock
from app.models.vente import Vente
from app.models.ligne_vente import LigneVente

NAMESPACE = uuid.UUID('c63ac20c-9a29-465d-9099-826eaa18c745')


def demo_id(key):
    return uuid.uuid5(NAMESPACE, 'stockjuste-demo-v1:' + key)


def seed(db):
    commercant_id = demo_id('commercant')
    commerce_id = demo_id('commerce')
    if db.get(Commercant, commercant_id) is None:
        db.add(Commercant(
            id_commercant=commercant_id,
            nom_complet='Commerçant Démonstration',
            email='stockjuste-demo@example.invalid',
            telephone='0000000000',
            mot_de_passe_hash='!COMPTE_DEMO_CONNEXION_DESACTIVEE',
        ))
    if db.get(Commerce, commerce_id) is None:
        db.add(Commerce(
            id_commerce=commerce_id,
            id_commercant=commercant_id,
            nom_commercial='Épicerie Démo StockJuste',
            type_commerce='Epicerie',
            adresse='Adresse fictive, démonstration',
            ville='Fès',
        ))
    db.flush()

    donnees = [
        ('DEMO-LAIT', 'Lait 1 L', 'Produits laitiers', 'Marque démo', '8.00', 10, True, 50),
        ('DEMO-SUCRE', 'Sucre 1 kg', 'Epicerie', 'Marque démo', '7.00', 15, False, 100),
        ('DEMO-HUILE', 'Huile 5 L', 'Epicerie', 'Marque démo', '65.00', 5, False, 30),
    ]
    items = {}
    for code, nom, categorie, marque, prix, seuil, perissable, quantite in donnees:
        pid = demo_id('produit:' + code)
        lot_id = demo_id('lot:' + code)
        if db.get(Produit, pid) is None:
            db.add(Produit(
                id_produit=pid, id_commerce=commerce_id, code_produit=code,
                nom_produit=nom, categorie=categorie, marque=marque,
                prix_vente=Decimal(prix), seuil_minimal=seuil,
                est_perissable=perissable, est_actif=True,
            ))
        db.flush()
        if db.get(LotStock, lot_id) is None:
            db.add(LotStock(
                id_lot=lot_id, id_produit=pid,
                numero_lot='DEMO-LOT-' + code,
                quantite_recue=quantite,
                quantite_restante=quantite,
            ))
            db.flush()
            db.add(MouvementStock(
                id_mouvement=demo_id('entree:' + code),
                id_lot=lot_id, type_mouvement='ENTREE',
                variation_quantite=quantite,
                motif='Stock initial fictif (seed v1)',
            ))
        items[code] = (pid, lot_id, Decimal(prix))

    vente_id = demo_id('vente:1')
    if db.get(Vente, vente_id) is None:
        quantites = [('DEMO-LAIT', 2), ('DEMO-SUCRE', 1)]
        total = sum((items[code][2] * n for code, n in quantites), Decimal('0'))
        db.add(Vente(
            id_vente=vente_id, id_commerce=commerce_id,
            montant_total=total, statut='VALIDEE',
        ))
        db.flush()
        for code, n in quantites:
            pid, lot_id, prix = items[code]
            lot = db.get(LotStock, lot_id)
            if lot.quantite_restante < n:
                raise ValueError(f'Stock insuffisant pour {code}; aucun changement enregistre.')
            lot.quantite_restante -= n
            db.add(LigneVente(
                id_ligne=demo_id('ligne:1:' + code),
                id_vente=vente_id, id_produit=pid, id_lot=lot_id,
                quantite=n, prix_unitaire=prix, sous_total=prix * n,
            ))
            db.add(MouvementStock(
                id_mouvement=demo_id('sortie:1:' + code),
                id_lot=lot_id, type_mouvement='VENTE',
                variation_quantite=-n,
                motif='Vente de démonstration (seed v1)',
            ))


def main():
    parser = argparse.ArgumentParser(description='Initialisation fictive StockJuste')
    parser.add_argument('--apply', action='store_true', help='Écrire les données dans la base ciblée')
    args = parser.parse_args()
    # Ne jamais afficher l'URL entière : elle contient des identifiants secrets.
    from sqlalchemy.engine import make_url
    url = make_url(settings.DATABASE_URL)
    print(f'Base cible : {url.database} | Hôte : {url.host}')
    if not args.apply:
        print('Aucune écriture. Pour insérer les données : python seed.py --apply')
        return
    with SessionLocal.begin() as db:
        seed(db)
    print('Seed terminé : données de démonstration présentes, sans doublons.')
    print('Compte démo non utilisable pour se connecter (mot de passe désactivé).')


if __name__ == '__main__':
    main()
