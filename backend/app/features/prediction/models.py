from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Numeric,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func
)

from .database import Base


# ==================================================
# TABLE 1 : REFERENTIEL DES PRODUITS
# ==================================================

class PredictionProduit(Base):

    __tablename__ = "prediction_produits"

    id_produit = Column(String(10), primary_key=True)

    nom_produit = Column(
        String(150),
        unique=True,
        nullable=False
    )

    categorie = Column(String(100), nullable=False)


# ==================================================
# TABLE 2 : INFORMATIONS ET PERFORMANCES DU MODELE
# ==================================================

class PredictionModele(Base):

    __tablename__ = "prediction_modeles"

    __table_args__ = (
        UniqueConstraint("nom_modele", "version"),
    )

    id_modele = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    nom_modele = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False)

    mae = Column(Float, nullable=False)
    rmse = Column(Float, nullable=False)
    r2 = Column(Float, nullable=False)
    wape = Column(Float, nullable=False)

    periode_evaluation = Column(String(100))
    date_entrainement = Column(DateTime)

    statut = Column(String(20), default="actif")


# ==================================================
# TABLE 3 : HISTORIQUE DES PREDICTIONS
# ==================================================

class PredictionHistorique(Base):

    __tablename__ = "prediction_historique"

    # Identification de la prédiction

    id_prediction = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # Produit concerné

    id_produit = Column(
        String(10),
        ForeignKey("prediction_produits.id_produit"),
        nullable=False
    )

    # Modèle utilisé

    id_modele = Column(
        Integer,
        ForeignKey("prediction_modeles.id_modele"),
        nullable=False
    )

    # Ventes des quatre semaines précédentes

    ventes_s1 = Column(Integer, nullable=False)
    ventes_s2 = Column(Integer, nullable=False)
    ventes_s3 = Column(Integer, nullable=False)
    ventes_s4 = Column(Integer, nullable=False)

    # Informations commerciales

    promotion = Column(Integer, nullable=False)
    prix = Column(Numeric(10, 2), nullable=False)
    nombre_lots = Column(Integer, nullable=False)

    # Période de prédiction

    annee = Column(Integer, nullable=False)
    mois_num = Column(Integer, nullable=False)
    semaine = Column(Integer, nullable=False)

    # Variables complémentaires du modèle

    moyenne_4_semaines = Column(Float, nullable=False)
    tendance = Column(Integer, nullable=False)
    duree_vie_jours = Column(Integer, nullable=False)

    # Résultat de la prédiction XGBoost

    quantite_predite = Column(Float, nullable=True)

    # Stock disponible saisi par le commerçant
    # au moment de la prédiction

    stock_disponible = Column(Integer, nullable=True)

    # Quantité recommandée à commander
    # Calculée après la prédiction

    quantite_a_commander = Column(Integer, nullable=True)

    # Intervalle de prédiction

    borne_inferieure = Column(Float, nullable=True)
    borne_superieure = Column(Float, nullable=True)

    # Quantité réellement vendue

    quantite_reelle = Column(Integer, nullable=True)

    # Date de réalisation de la prédiction

    date_prediction = Column(
        DateTime,
        server_default=func.now()
    )


# ==================================================
# TABLE 4 : HISTORIQUE DES VENTES
# ==================================================

class PredictionVenteReelle(Base):

    __tablename__ = "prediction_ventes_reelles"

    __table_args__ = (
        UniqueConstraint(
            "id_produit",
            "annee",
            "mois_num",
            "semaine",
            name="uq_prediction_vente_periode"
        ),
    )

    id_vente = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    id_produit = Column(
        String(10),
        ForeignKey("prediction_produits.id_produit"),
        nullable=False
    )

    annee = Column(Integer, nullable=False)
    mois_num = Column(Integer, nullable=False)
    semaine = Column(Integer, nullable=False)

    ventes_s1 = Column(Integer, nullable=False)
    ventes_s2 = Column(Integer, nullable=False)
    ventes_s3 = Column(Integer, nullable=False)
    ventes_s4 = Column(Integer, nullable=False)

    promotion = Column(Integer, nullable=False)
    prix = Column(Float, nullable=False)
    nombre_lots = Column(Integer, nullable=False)

    duree_vie_jours = Column(Integer, nullable=False)
    moyenne_4_semaines = Column(Float, nullable=False)
    tendance = Column(Integer, nullable=False)

    quantite_vendue = Column(Integer, nullable=False)

    # Train / Validation / Test / Simulation / Production

    jeu_donnees = Column(String(20), nullable=False)