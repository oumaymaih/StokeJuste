const API_URL = "http://127.0.0.1:8001/api/prediction";

// ==================================================
// 1. TYPES DES DONNEES
// ==================================================

export interface Produit {
    id_produit: string;
    nom_produit: string;
    categorie: string;
}

export interface Performances {
    id_modele: number;
    nom_modele: string;
    version: string;
    mae: number;
    rmse: number;
    r2: number;
    wape: number;
    periode_evaluation: string;
    statut: string;
}

// Les 9 informations envoyées au backend

export interface PredictionRequest {
    id_produit: string;
    annee: number;
    mois_num: number;
    semaine: number;
    prix: number;
    promotion: number;
    nombre_lots: number;
    duree_vie_jours: number;

    // Nouvelle information saisie par le commerçant
    stock_disponible: number;
}

// Résultat retourné par le backend

export interface PredictionResponse {
    id_prediction: number;
    id_produit: string;
    nom_produit: string;

    quantite_predite: number;

    // Informations de recommandation de commande
    stock_disponible: number;
    quantite_a_commander: number;

    borne_inferieure: number | null;
    borne_superieure: number | null;

    ventes_s1: number;
    ventes_s2: number;
    ventes_s3: number;
    ventes_s4: number;
}

// Historique des prédictions

export interface HistoriquePrediction {
    id_prediction: number;
    id_produit: string;
    nom_produit: string;

    annee: number;
    mois_num: number;
    semaine: number;

    quantite_predite: number;

    // Les anciennes prédictions peuvent contenir NULL
    stock_disponible: number | null;
    quantite_a_commander: number | null;

    quantite_reelle: number | null;

    borne_inferieure: number | null;
    borne_superieure: number | null;

    date_prediction: string;
}

export interface FiltresHistorique {
    id_produit?: string;
    annee?: string;
    mois_num?: string;
}

// ==================================================
// 2. FONCTION GENERIQUE POUR LES REQUETES HTTP
// ==================================================

async function requete<T>(
    endpoint: string,
    options?: RequestInit
): Promise<T> {

    let response: Response;

    try {
        response = await fetch(
            `${API_URL}${endpoint}`,
            options
        );
    } catch {
        throw new Error(
            "Impossible de contacter le backend. Vérifiez que FastAPI est lancé sur le port 8001."
        );
    }

    const data = await response.json().catch(() => null);

    if (!response.ok) {

        if (typeof data?.detail === "string") {
            throw new Error(data.detail);
        }

        if (Array.isArray(data?.detail)) {

            const message = data.detail
                .map((erreur: {
                    loc?: string[];
                    msg: string;
                }) => {
                    const champ = erreur.loc?.slice(1).join(".");
                    return `${champ || "Champ"} : ${erreur.msg}`;
                })
                .join(" | ");

            throw new Error(message);
        }

        throw new Error(
            `Erreur du serveur : HTTP ${response.status}`
        );
    }

    return data as T;
}

// ==================================================
// 3. API : CONSULTER LES PRODUITS
// ==================================================

export function getProduits(): Promise<Produit[]> {

    return requete<Produit[]>("/produits");
}

// ==================================================
// 4. API : CONSULTER LES PERFORMANCES
// ==================================================

export function getPerformances(): Promise<Performances> {

    return requete<Performances>("/performances");
}

// ==================================================
// 5. API : EFFECTUER UNE PREDICTION
// ==================================================

export function predireQuantite(
    donnees: PredictionRequest
): Promise<PredictionResponse> {

    return requete<PredictionResponse>(
        "/predire",
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(donnees)
        }
    );
}

// ==================================================
// 6. API : CONSULTER L'HISTORIQUE
// ==================================================

export function getHistorique(
    filtres: FiltresHistorique = {}
): Promise<HistoriquePrediction[]> {

    const params = new URLSearchParams();

    if (filtres.id_produit) {
        params.set("id_produit", filtres.id_produit);
    }

    if (filtres.annee) {
        params.set("annee", filtres.annee);
    }

    if (filtres.mois_num) {
        params.set("mois_num", filtres.mois_num);
    }

    const query = params.toString();

    return requete<HistoriquePrediction[]>(
        `/historique${query ? `?${query}` : ""}`
    );
}