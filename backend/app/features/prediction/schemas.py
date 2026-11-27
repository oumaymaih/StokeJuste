from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator
)


# ==================================================
# 1. DONNEES RECUES DU FRONTEND
# ==================================================

class PredictionAutoRequest(BaseModel):

    model_config = ConfigDict(extra="forbid")

    # Identification du produit
    id_produit: str = Field(
        min_length=1,
        max_length=10
    )

    # Période à prédire
    annee: int = Field(ge=2000, le=2100)
    mois_num: int = Field(ge=1, le=12)
    semaine: int = Field(ge=1, le=5)

    # Informations commerciales
    promotion: int = Field(ge=0, le=1)

    prix: float = Field(
        gt=0,
        allow_inf_nan=False
    )

    nombre_lots: int = Field(ge=0)

    duree_vie_jours: int = Field(gt=0)

    # Stock disponible saisi par le commerçant
    # Utilisé uniquement pour la recommandation de commande

    stock_disponible: int = Field(
        ge=0,
        le=2147483647,
        strict=True,
        description="Quantité disponible en stock, en unités"
    )

    # Nettoyer l'identifiant du produit

    @field_validator("id_produit", mode="before")
    @classmethod
    def nettoyer_id_produit(cls, valeur):

        if isinstance(valeur, str):
            return valeur.strip().upper()

        return valeur

    # Convertir Oui / Non en 1 / 0

    @field_validator("promotion", mode="before")
    @classmethod
    def convertir_promotion(cls, valeur):

        if isinstance(valeur, str):

            valeur = valeur.strip().lower()

            if valeur == "oui":
                return 1

            if valeur == "non":
                return 0

        return valeur

    # Convertir le prix en nombre décimal

    @field_validator("prix", mode="before")
    @classmethod
    def convertir_prix(cls, valeur):

        if isinstance(valeur, str):

            valeur = (
                valeur.upper()
                .replace("MAD", "")
                .replace(",", ".")
                .strip()
            )

        return valeur


# ==================================================
# 2. DONNEES COMPLETES UTILISEES PAR LE BACKEND
# ==================================================

class PredictionRequest(PredictionAutoRequest):

    # Cette classe hérite des neuf informations
    # saisies par le commerçant.

    # Les quatre ventes précédentes sont récupérées
    # automatiquement depuis PostgreSQL.

    ventes_s1: int = Field(ge=0)
    ventes_s2: int = Field(ge=0)
    ventes_s3: int = Field(ge=0)
    ventes_s4: int = Field(ge=0)

    # Le stock disponible est hérité automatiquement
    # de la classe PredictionAutoRequest.
    #
    # Il ne sera pas transmis au modèle XGBoost.


# ==================================================
# 3. REPONSE ENVOYEE AU FRONTEND
# ==================================================

class PredictionResponse(BaseModel):

    # Identification de la prédiction

    id_prediction: int
    id_produit: str
    nom_produit: str

    # Résultat de la prédiction

    quantite_predite: float = Field(
        ge=0,
        allow_inf_nan=False
    )

    # Stock disponible saisi par le commerçant

    stock_disponible: int = Field(
        ge=0,
        le=2147483647,
        description="Quantité disponible en stock, en unités"
    )

    # Quantité recommandée à commander

    quantite_a_commander: int = Field(
        ge=0,
        description="Quantité recommandée à commander, en unités"
    )

    # Intervalle de prédiction

    borne_inferieure: float | None = None
    borne_superieure: float | None = None

    # Ventes historiques utilisées par le modèle

    ventes_s1: int = Field(ge=0)
    ventes_s2: int = Field(ge=0)
    ventes_s3: int = Field(ge=0)
    ventes_s4: int = Field(ge=0)

    # Indiquer si des données simulées ont été utilisées

    historique_simule: bool