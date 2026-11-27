
import pandas as pd
import numpy as np

from pathlib import Path
from sqlalchemy.dialects.postgresql import insert

from ..database import engine, SessionLocal, Base

from ..models import (
    PredictionProduit,
    PredictionVenteReelle
)


# ==================================================
# CONFIGURATION
# ==================================================

SEED = 42

BASE_DIR = Path(__file__).resolve().parents[1]

CSV_PATH = (
    BASE_DIR
    / "notebook"
    / "dataset_stockjuste_nettoye.csv"
)

ANNEE_SIMULATION = 2026
MOIS_FIN = 11
SEMAINE_FIN = 3

COLONNES_VENTES = [
    "ventes_s1",
    "ventes_s2",
    "ventes_s3",
    "ventes_s4"
]

COLONNES_ENTIERES = [
    "annee",
    "mois_num",
    "semaine",
    *COLONNES_VENTES,
    "promotion",
    "nombre_lots",
    "duree_vie_jours",
    "quantite_vendue"
]

COLONNES_TABLE = [
    "id_produit",
    "annee",
    "mois_num",
    "semaine",
    *COLONNES_VENTES,
    "promotion",
    "prix",
    "nombre_lots",
    "duree_vie_jours",
    "moyenne_4_semaines",
    "tendance",
    "quantite_vendue",
    "jeu_donnees"
]


# ==================================================
# ETAPE 1 : IDENTIFIER LE JEU DE DONNEES
# ==================================================

def identifier_jeu(ligne):

    annee = ligne["annee"]
    mois = ligne["mois_num"]

    if annee == 2023:
        return "Train"

    if annee == 2024:

        if mois <= 6:
            return "Train"

        return "Validation"

    if annee == 2025:
        return "Test"

    raise ValueError(
        f"Période inattendue : {annee}/{mois}"
    )


# ==================================================
# ETAPE 2 : CHARGER LE DATASET NETTOYE
# ==================================================

def charger_dataset():

    if not CSV_PATH.exists():

        raise FileNotFoundError(
            f"Dataset introuvable : {CSV_PATH}"
        )

    df = pd.read_csv(CSV_PATH)

    colonnes_requises = [
        "produit",
        "prix",
        *COLONNES_ENTIERES
    ]

    manquantes = set(colonnes_requises) - set(df.columns)

    if manquantes:

        raise ValueError(
            f"Colonnes manquantes : {manquantes}"
        )

    df = df[colonnes_requises].copy()

    df["produit"] = df["produit"].str.strip()

    # Convertir les colonnes numériques

    for colonne in COLONNES_ENTIERES:

        valeurs = pd.to_numeric(
            df[colonne],
            errors="raise"
        )

        if not np.isfinite(valeurs).all():

            raise ValueError(
                f"Valeurs invalides : {colonne}"
            )

        if (valeurs % 1 != 0).any():

            raise ValueError(
                f"Valeurs non entières : {colonne}"
            )

        df[colonne] = valeurs.astype(int)

    df["prix"] = pd.to_numeric(
        df["prix"],
        errors="raise"
    )

    # Calculer les features dérivées

    df["moyenne_4_semaines"] = (
        df[COLONNES_VENTES].mean(axis=1)
    )

    df["tendance"] = (
        df["ventes_s1"] - df["ventes_s4"]
    )

    # Identifier Train / Validation / Test

    df["jeu_donnees"] = df.apply(
        identifier_jeu,
        axis=1
    )

    print("Dataset chargé :", len(df), "lignes")

    return df


# ==================================================
# ETAPE 3 : VERIFIER LA QUALITE
# ==================================================

def verifier_dataset(df):

    if df.isna().any().any():
        raise ValueError("Valeurs manquantes détectées.")

    if df["produit"].eq("").any():
        raise ValueError("Nom de produit vide.")

    if df.duplicated(
        ["produit", "annee", "mois_num", "semaine"]
    ).any():

        raise ValueError("Doublons détectés.")

    if not df["mois_num"].between(1, 12).all():
        raise ValueError("Mois invalides.")

    if not df["semaine"].between(1, 5).all():
        raise ValueError("Semaines invalides.")

    if not df["promotion"].isin([0, 1]).all():
        raise ValueError("Promotion invalide.")

    if not np.isfinite(df["prix"]).all():
        raise ValueError("Prix non finis.")

    if not (df["prix"] > 0).all():
        raise ValueError("Prix invalides.")

    if not (df["duree_vie_jours"] > 0).all():
        raise ValueError("Durées de vie invalides.")

    colonnes_quantites = [
        *COLONNES_VENTES,
        "nombre_lots",
        "quantite_vendue"
    ]

    if (df[colonnes_quantites] < 0).any().any():
        raise ValueError("Quantités négatives.")

    print("Contrôles qualité : OK")


# ==================================================
# ETAPE 4 : VERIFIER LA COHERENCE DES VENTES PASSEES
# ==================================================

def verifier_coherence_historique(df):

    df_trie = df.sort_values(
        ["produit", "annee", "mois_num", "semaine"]
    )

    groupes = df_trie.groupby("produit")

    print("\nCOHERENCE DES VENTES PRECEDENTES")

    for i in range(1, 5):

        quantites_precedentes = (
            groupes["quantite_vendue"].shift(i)
        )

        masque = quantites_precedentes.notna()

        total = int(masque.sum())

        correspondances = int(
            (
                df_trie.loc[masque, f"ventes_s{i}"]
                == quantites_precedentes[masque]
            ).sum()
        )

        taux = (
            100 * correspondances / total
            if total else 0
        )

        print(
            f"ventes_s{i} : "
            f"{correspondances}/{total} "
            f"correspondances ({taux:.2f} %)"
        )

        if correspondances != total:

            print(
                "ATTENTION : vérifier la définition "
                "des ventes historiques du dataset."
            )


# ==================================================
# ETAPE 5 : GENERER LES DONNEES DE 2026
# ==================================================

def generer_donnees_2026(df):

    rng = np.random.default_rng(SEED)

    reference = df[
        df["annee"] == 2025
    ].copy()

    if reference.empty:

        raise ValueError(
            "Les données de référence 2025 sont absentes."
        )

    produits = sorted(df["produit"].unique())

    # Reprendre les périodes réellement présentes en 2025

    periodes = (
        reference[["mois_num", "semaine"]]
        .drop_duplicates()
        .sort_values(["mois_num", "semaine"])
    )

    # Garder les périodes jusqu'à novembre S3

    periodes = periodes[
        (periodes["mois_num"] < MOIS_FIN)
        |
        (
            (periodes["mois_num"] == MOIS_FIN)
            &
            (periodes["semaine"] <= SEMAINE_FIN)
        )
    ]

    if (MOIS_FIN, SEMAINE_FIN) not in list(
        periodes.itertuples(index=False, name=None)
    ):

        raise ValueError(
            "La période finale est absente "
            "du calendrier de référence."
        )

    # Historique chronologique par produit

    historiques = {}

    for produit in produits:

        donnees_produit = df[
            df["produit"] == produit
        ].sort_values(
            ["annee", "mois_num", "semaine"]
        )

        historiques[produit] = (
            donnees_produit["quantite_vendue"].tolist()
        )

        if len(historiques[produit]) < 4:

            raise ValueError(
                f"Historique insuffisant : {produit}"
            )

    # Index de recherche des données 2025

    reference = reference.set_index(
        ["produit", "mois_num", "semaine"]
    )

    nouvelles_lignes = []

    for mois, semaine in periodes.itertuples(
        index=False,
        name=None
    ):

        for produit in produits:

            cle = (produit, mois, semaine)

            if cle not in reference.index:

                raise ValueError(
                    f"Référence 2025 absente : {cle}"
                )

            ligne_ref = reference.loc[cle]

            historique = historiques[produit]

            # Quatre dernières ventes observées ou simulées

            ventes_s1 = int(historique[-1])
            ventes_s2 = int(historique[-2])
            ventes_s3 = int(historique[-3])
            ventes_s4 = int(historique[-4])

            # Variation aléatoire de -10 % à +10 %

            facteur = rng.uniform(0.90, 1.10)

            quantite = max(
                0,
                int(round(
                    ligne_ref["quantite_vendue"] * facteur
                ))
            )

            moyenne = (
                ventes_s1
                + ventes_s2
                + ventes_s3
                + ventes_s4
            ) / 4

            tendance = ventes_s1 - ventes_s4

            nouvelle_ligne = {
                "produit": produit,
                "annee": ANNEE_SIMULATION,
                "mois_num": int(mois),
                "semaine": int(semaine),

                "ventes_s1": ventes_s1,
                "ventes_s2": ventes_s2,
                "ventes_s3": ventes_s3,
                "ventes_s4": ventes_s4,

                "promotion": int(ligne_ref["promotion"]),
                "prix": float(ligne_ref["prix"]),

                "nombre_lots": int(
                    ligne_ref["nombre_lots"]
                ),

                "duree_vie_jours": int(
                    ligne_ref["duree_vie_jours"]
                ),

                "moyenne_4_semaines": moyenne,
                "tendance": tendance,

                "quantite_vendue": quantite,

                "jeu_donnees": "Simulation"
            }

            nouvelles_lignes.append(nouvelle_ligne)

            # Alimenter l'historique de la semaine suivante

            historique.append(quantite)

    df_simulation = pd.DataFrame(nouvelles_lignes)

    print(
        "\nDonnées simulées générées :",
        len(df_simulation)
    )

    return df_simulation


# ==================================================
# ETAPE 6 : FUSIONNER ET TRIER LES DONNEES
# ==================================================

def fusionner_donnees(df, df_simulation):

    df_final = pd.concat(
        [df, df_simulation],
        ignore_index=True
    )

    df_final = df_final.sort_values(
        [
            "annee",
            "mois_num",
            "semaine",
            "produit"
        ],
        ascending=True
    ).reset_index(drop=True)

    verifier_dataset(df_final)

    print("\nREPARTITION FINALE")

    print(
        df_final["jeu_donnees"]
        .value_counts()
        .reindex(
            [
                "Train",
                "Validation",
                "Test",
                "Simulation"
            ]
        )
    )

    print("Total :", len(df_final))

    return df_final


# ==================================================
# ETAPE 7 : CREER UNIQUEMENT LA NOUVELLE TABLE
# ==================================================

def creer_table():

    Base.metadata.create_all(
        bind=engine,
        tables=[
            PredictionVenteReelle.__table__
        ],
        checkfirst=True
    )

    print(
        "Table prediction_ventes_reelles disponible."
    )


# ==================================================
# ETAPE 8 : ALIMENTER POSTGRESQL
# ==================================================

def alimenter_table(df):

    db = SessionLocal()

    try:

        df = df.copy()

        # Récupérer les identifiants des produits

        produits = db.query(
            PredictionProduit
        ).all()

        mapping = {
            p.nom_produit.strip(): p.id_produit
            for p in produits
        }

        df["id_produit"] = (
            df["produit"].map(mapping)
        )

        # Vérifier les produits inconnus

        if df["id_produit"].isna().any():

            inconnus = df.loc[
                df["id_produit"].isna(),
                "produit"
            ].unique()

            raise ValueError(
                f"Produits inconnus : {inconnus}"
            )

        # Ordre chronologique croissant

        df = df.sort_values(
            [
                "annee",
                "mois_num",
                "semaine",
                "id_produit"
            ],
            ascending=True
        ).reset_index(drop=True)

        donnees = df[
            COLONNES_TABLE
        ].to_dict(orient="records")

        nb_inserees = 0
        nb_ignorees = 0

        # Insertion par lots pour limiter les requêtes

        taille_lot = 200

        for debut in range(
            0,
            len(donnees),
            taille_lot
        ):

            lot = donnees[
                debut:debut + taille_lot
            ]

            requete = insert(
                PredictionVenteReelle
            ).values(lot)

            requete = requete.on_conflict_do_nothing(
                index_elements=[
                    "id_produit",
                    "annee",
                    "mois_num",
                    "semaine"
                ]
            )

            resultat = db.execute(requete)

            nb_inserees += resultat.rowcount

            nb_ignorees += (
                len(lot) - resultat.rowcount
            )

        db.commit()

        print("\nCHARGEMENT TERMINE")

        print("Lignes insérées :", nb_inserees)
        print("Lignes ignorées :", nb_ignorees)

        print(
            "Total PostgreSQL :",
            db.query(PredictionVenteReelle).count()
        )

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


# ==================================================
# ETAPE 9 : VERIFIER LE CHARGEMENT
# ==================================================

def verifier_chargement():

    db = SessionLocal()

    try:

        print("\nCONTENU DE POSTGRESQL")

        for jeu in [
            "Train",
            "Validation",
            "Test",
            "Simulation"
        ]:

            nombre = db.query(
                PredictionVenteReelle
            ).filter_by(
                jeu_donnees=jeu
            ).count()

            print(jeu, ":", nombre)

        # Dernières observations

        dernieres = db.query(
            PredictionVenteReelle
        ).order_by(
            PredictionVenteReelle.annee.desc(),
            PredictionVenteReelle.mois_num.desc(),
            PredictionVenteReelle.semaine.desc(),
            PredictionVenteReelle.id_produit.asc()
        ).limit(10).all()

        print("\nDERNIERES OBSERVATIONS")

        for vente in dernieres:

            print(
                f"{vente.annee}/"
                f"{vente.mois_num:02d}/"
                f"S{vente.semaine} | "
                f"{vente.id_produit} | "
                f"{vente.quantite_vendue} unités | "
                f"{vente.jeu_donnees}"
            )

    finally:

        db.close()


# ==================================================
# ETAPE 10 : EXECUTION
# ==================================================

if __name__ == "__main__":

    print("=" * 65)
    print("CHARGEMENT DES VENTES HISTORIQUES")
    print("=" * 65)

    # Charger les données 2023 - 2025

    df = charger_dataset()

    verifier_dataset(df)

    verifier_coherence_historique(df)

    # Générer les données de 2026

    df_simulation = generer_donnees_2026(df)

    # Fusionner les deux datasets

    df_final = fusionner_donnees(
        df,
        df_simulation
    )

    # Créer la table

    creer_table()

    # Insérer dans PostgreSQL

    alimenter_table(df_final)

    # Vérifier le résultat

    verifier_chargement()

    print("\nChargement terminé avec succès !")
