import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link } from "react-router-dom";

import {
    getProduits,
    getPerformances,
    predireQuantite,
    getHistorique
} from "./predictionApi";

import type {
    Produit,
    Performances,
    PredictionRequest,
    PredictionResponse,
    HistoriquePrediction,
    FiltresHistorique
} from "./predictionApi";

import "./prediction.css";

// ==================================================
// 1. CONSTANTES ET FONCTIONS UTILITAIRES
// ==================================================

const MOIS = [
    "Janvier",
    "Février",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre"
];

const ANNEES = Array.from(
    { length: 11 },
    (_, i) => 2023 + i
);

const SEMAINES = [1, 2, 3, 4, 5];

const TAILLE_PAGE = 10;

function formatNombre(valeur: number) {
    return valeur.toLocaleString("fr-FR", {
        maximumFractionDigits: 2
    });
}

function messageErreur(erreur: unknown) {
    return erreur instanceof Error
        ? erreur.message
        : "Une erreur est survenue.";
}

// ==================================================
// 2. COMPOSANT PRINCIPAL
// ==================================================

export default function PredictionPage() {

    // --------------------------------------------------
    // Navigation
    // --------------------------------------------------

    const [onglet, setOnglet] = useState<
        "prediction" | "historique"
    >("prediction");

    // --------------------------------------------------
    // Données du backend
    // --------------------------------------------------

    const [produits, setProduits] =
        useState<Produit[]>([]);

    const [performances, setPerformances] =
        useState<Performances | null>(null);

    const [resultat, setResultat] =
        useState<PredictionResponse | null>(null);

    const [periodeResultat, setPeriodeResultat] =
        useState<PredictionRequest | null>(null);

    const [historique, setHistorique] =
        useState<HistoriquePrediction[]>([]);

    // --------------------------------------------------
    // États de chargement
    // --------------------------------------------------

    const [chargementInitial, setChargementInitial] =
        useState(true);

    const [chargement, setChargement] =
        useState(false);

    const [chargementHistorique, setChargementHistorique] =
        useState(false);

    // --------------------------------------------------
    // Gestion des erreurs
    // --------------------------------------------------

    const [erreur, setErreur] = useState("");

    const [erreurHistorique, setErreurHistorique] =
        useState("");

    const [erreurInitialisation, setErreurInitialisation] =
        useState("");

    const [erreurPerformances, setErreurPerformances] =
        useState("");

    // --------------------------------------------------
    // Recherche, tri et pagination
    // --------------------------------------------------

    const [recherche, setRecherche] =
        useState("");

    const [tri, setTri] =
        useState("date-desc");

    const [page, setPage] =
        useState(1);

    // --------------------------------------------------
    // Formulaire de prédiction
    // --------------------------------------------------

    const [formulaire, setFormulaire] =
        useState<PredictionRequest>({
            id_produit: "",
            annee: 2026,
            mois_num: 11,
            semaine: 4,
            prix: 35.59,
            nombre_lots: 10,
            duree_vie_jours: 90,
            promotion: 1,
            stock_disponible: NaN
        });

    // --------------------------------------------------
    // Filtres de l'historique
    // --------------------------------------------------

    const [filtres, setFiltres] =
        useState<FiltresHistorique>({
            id_produit: "",
            annee: "",
            mois_num: ""
        });

    // ==================================================
    // 3. CHARGEMENT INITIAL
    // ==================================================

    useEffect(() => {

        let actif = true;

        async function initialiser() {

            const [reponseProduits, reponsePerformances] =
                await Promise.allSettled([
                    getProduits(),
                    getPerformances()
                ]);

            if (!actif) {
                return;
            }

            if (reponseProduits.status === "fulfilled") {

                const listeProduits =
                    reponseProduits.value;

                setProduits(listeProduits);

                setFormulaire(precedent => ({
                    ...precedent,

                    id_produit:
                        precedent.id_produit ||
                        listeProduits[0]?.id_produit ||
                        ""
                }));

            } else {

                setErreurInitialisation(
                    messageErreur(reponseProduits.reason)
                );
            }

            if (reponsePerformances.status === "fulfilled") {

                setPerformances(
                    reponsePerformances.value
                );

            } else {

                setErreurPerformances(
                    messageErreur(reponsePerformances.reason)
                );
            }

            setChargementInitial(false);
        }

        void initialiser();

        return () => {
            actif = false;
        };

    }, []);

    // ==================================================
    // 4. MODIFICATION DU FORMULAIRE
    // ==================================================

    function modifierChamp<K extends keyof PredictionRequest>(
        champ: K,
        valeur: PredictionRequest[K]
    ) {

        setFormulaire(precedent => ({
            ...precedent,
            [champ]: valeur
        }));
    }

    // ==================================================
    // 5. EFFECTUER UNE PREDICTION
    // ==================================================

    async function effectuerPrediction(
        event: FormEvent<HTMLFormElement>
    ) {

        event.preventDefault();

        if (chargement) {
            return;
        }

        setErreur("");
        setResultat(null);
        setPeriodeResultat(null);

        // Vérification du produit

        if (!formulaire.id_produit) {

            setErreur("Veuillez sélectionner un produit.");

            return;
        }

        // Vérification du prix

        if (
            !Number.isFinite(formulaire.prix) ||
            formulaire.prix <= 0
        ) {

            setErreur("Le prix doit être supérieur à zéro.");

            return;
        }

        // Vérification du nombre de lots

        if (
            !Number.isInteger(formulaire.nombre_lots) ||
            formulaire.nombre_lots < 0
        ) {

            setErreur(
                "Le nombre de lots doit être un entier positif ou nul."
            );

            return;
        }

        // Vérification de la durée de vie

        if (
            !Number.isInteger(formulaire.duree_vie_jours) ||
            formulaire.duree_vie_jours <= 0
        ) {

            setErreur(
                "La durée de vie doit être un entier supérieur à zéro."
            );

            return;
        }

        // Vérification du stock disponible

        if (
            !Number.isInteger(formulaire.stock_disponible) ||
            formulaire.stock_disponible < 0 ||
            formulaire.stock_disponible > 2147483647
        ) {

            setErreur(
                "Veuillez saisir un stock disponible entier compris entre 0 et 2147483647."
            );

            return;
        }

        setChargement(true);

        const donnees = { ...formulaire };

        try {

            const reponse =
                await predireQuantite(donnees);

            setResultat(reponse);

            setPeriodeResultat(donnees);

        } catch (e) {

            setErreur(messageErreur(e));

        } finally {

            setChargement(false);
        }
    }

    // ==================================================
    // 6. CHARGEMENT DE L'HISTORIQUE
    // ==================================================

    async function chargerHistorique(
        criteres: FiltresHistorique
    ) {

        setErreurHistorique("");
        setChargementHistorique(true);

        try {

            const donnees =
                await getHistorique(criteres);

            setHistorique(donnees);

            setPage(1);

        } catch (e) {

            setHistorique([]);

            setErreurHistorique(
                messageErreur(e)
            );

        } finally {

            setChargementHistorique(false);
        }
    }

    // ==================================================
    // 7. NAVIGATION ENTRE LES PAGES
    // ==================================================

    function ouvrirPrediction() {

        setOnglet("prediction");

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    }

    function ouvrirHistorique() {

        setOnglet("historique");

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

        if (!chargementHistorique) {
            void chargerHistorique(filtres);
        }
    }

    // ==================================================
    // 8. REINITIALISATION DES FILTRES
    // ==================================================

    function reinitialiserFiltres() {

        const nouveauxFiltres = {
            id_produit: "",
            annee: "",
            mois_num: ""
        };

        setFiltres(nouveauxFiltres);

        setRecherche("");

        setTri("date-desc");

        setPage(1);

        void chargerHistorique(nouveauxFiltres);
    }

    // ==================================================
    // 9. DONNEES DU GRAPHIQUE
    // ==================================================

    const valeursGraphique = resultat
        ? [
            {
                nom: "S-4",
                valeur: resultat.ventes_s4
            },
            {
                nom: "S-3",
                valeur: resultat.ventes_s3
            },
            {
                nom: "S-2",
                valeur: resultat.ventes_s2
            },
            {
                nom: "S-1",
                valeur: resultat.ventes_s1
            },
            {
                nom: "Prévision",
                valeur: resultat.quantite_predite
            }
        ]
        : [];

    const maximumGraphique = Math.max(
        1,
        ...valeursGraphique.map(item => item.valeur)
    );

    // ==================================================
    // 10. RECHERCHE ET TRI DE L'HISTORIQUE
    // ==================================================

    const lignesFiltrees = historique

        .filter(h =>
            h.nom_produit
                .toLocaleLowerCase("fr")
                .includes(
                    recherche
                        .trim()
                        .toLocaleLowerCase("fr")
                )
        )

        .sort((a, b) => {

            if (tri === "quantite-desc") {

                return (
                    b.quantite_predite -
                    a.quantite_predite
                );
            }

            if (tri === "quantite-asc") {

                return (
                    a.quantite_predite -
                    b.quantite_predite
                );
            }

            const dateA =
                new Date(a.date_prediction).getTime();

            const dateB =
                new Date(b.date_prediction).getTime();

            if (tri === "date-asc") {

                return dateA - dateB;
            }

            return dateB - dateA;
        });

    // ==================================================
    // 11. PAGINATION
    // ==================================================

    const totalPages = Math.max(
        1,
        Math.ceil(
            lignesFiltrees.length / TAILLE_PAGE
        )
    );

    const pageActive = Math.min(
        page,
        totalPages
    );

    const debutPage =
        (pageActive - 1) * TAILLE_PAGE;

    const finPage = Math.min(
        debutPage + TAILLE_PAGE,
        lignesFiltrees.length
    );

    const lignesPage = lignesFiltrees.slice(
        debutPage,
        finPage
    );

    const nombreProduits = new Set(
        lignesFiltrees.map(h => h.id_produit)
    ).size;

    // ==================================================
    // 12. EXPORTATION CSV
    // ==================================================

    function exporterCSV() {

        function cellule(valeur: unknown) {

            let texte = String(valeur ?? "");

            // Protection contre les formules Excel

            if (/^[=+@\-\t\r]/.test(texte)) {

                texte = "'" + texte;
            }

            return '"' +
                texte.replace(/"/g, '""') +
                '"';
        }

        const entetes = [
            "ID",
            "Produit",
            "Année",
            "Mois",
            "Semaine",
            "Quantité prédite",
            "Stock disponible",
            "Quantité à commander",
            "Quantité réelle",
            "Date de prédiction"
        ];

        const donnees = lignesFiltrees.map(h => [
            h.id_prediction,
            h.nom_produit,
            h.annee,
            MOIS[h.mois_num - 1],
            `S${h.semaine}`,
            String(h.quantite_predite).replace(".", ","),
            h.stock_disponible,
            h.quantite_a_commander,
            h.quantite_reelle,
            new Date(h.date_prediction)
                .toLocaleString("fr-FR")
        ]);

        const contenu = [
            entetes,
            ...donnees
        ]
            .map(ligne =>
                ligne.map(cellule).join(";")
            )
            .join("\r\n");

        const fichier = new Blob(
            ["\uFEFF", contenu],
            {
                type: "text/csv;charset=utf-8"
            }
        );

        const url =
            URL.createObjectURL(fichier);

        const lien =
            document.createElement("a");

        lien.href = url;

        lien.download =
            "stockjuste-historique.csv";

        document.body.appendChild(lien);

        lien.click();

        lien.remove();

        window.setTimeout(() => {
            URL.revokeObjectURL(url);
        }, 1000);
    }

    // ==================================================
    // 13. INTERFACE GRAPHIQUE
    // ==================================================

    return (

        <main className="sj-prediction">

            <div className="sj-container">

                {/* ======================================
                    BARRE DE NAVIGATION
                ====================================== */}

                <nav
                    className="sj-tabs"
                    aria-label="Navigation du module"
                >

                    <span className="sj-brand">
                        StockJuste
                        <span className="sj-brand-dot">.</span>
                    </span>

                    <div className="sj-nav-links">

                        {/* RETOUR A L'ACCUEIL */}

                        <Link
                            to="/tableau-de-bord"
                            className="sj-home-link"
                        >
                            Retour à l'accueil
                        </Link>

                        {/* ONGLET PREDICTION */}

                        <button
                            type="button"
                            className={
                                onglet === "prediction"
                                    ? "sj-tab active"
                                    : "sj-tab"
                            }
                            aria-current={
                                onglet === "prediction"
                                    ? "page"
                                    : undefined
                            }
                            onClick={ouvrirPrediction}
                        >
                            Prédiction
                        </button>

                        {/* ONGLET HISTORIQUE */}

                        <button
                            type="button"
                            className={
                                onglet === "historique"
                                    ? "sj-tab active"
                                    : "sj-tab"
                            }
                            aria-current={
                                onglet === "historique"
                                    ? "page"
                                    : undefined
                            }
                            onClick={ouvrirHistorique}
                        >
                            Historique
                        </button>

                    </div>

                </nav>

                {/* ======================================
                    EN-TETE DYNAMIQUE
                ====================================== */}

                <header className="sj-header">

                    <span className="sj-eyebrow">
                        GESTION INTELLIGENTE DES STOCKS
                    </span>

                    <h1>
                        {onglet === "prediction"
                            ? "Prédiction des ventes"
                            : "Historique des prédictions"}
                    </h1>

                    <p>
                        {onglet === "prediction"
                            ? "Anticipez la demande et optimisez la gestion de vos stocks."
                            : "Consultez, filtrez et exportez vos prévisions de ventes."}
                    </p>

                </header>

                {/* ERREUR D'INITIALISATION */}

                {erreurInitialisation && (

                    <div
                        className="sj-error"
                        role="alert"
                    >

                        <strong>
                            Erreur de connexion
                        </strong>

                        <p>
                            {erreurInitialisation}
                        </p>

                    </div>

                )}

                {/* ======================================
                    PAGE DE PREDICTION
                ====================================== */}

                {onglet === "prediction" && (

                    <>

                        {/* PERFORMANCES DU MODELE */}

                        {erreurPerformances && (

                            <div
                                className="sj-error"
                                role="alert"
                            >
                                Performances indisponibles :
                                {" "}
                                {erreurPerformances}
                            </div>

                        )}

                        <section
                            className="sj-metrics"
                            aria-label="Performances du modèle"
                        >

                            {/* MAE */}

                            <article className="sj-metric">

                                <span>MAE</span>

                                <strong>
                                    {performances
                                        ? formatNombre(
                                            performances.mae
                                        )
                                        : "N/D"}
                                </strong>

                                <small>
                                    Erreur absolue moyenne
                                </small>

                            </article>

                            {/* RMSE */}

                            <article className="sj-metric">

                                <span>RMSE</span>

                                <strong>
                                    {performances
                                        ? formatNombre(
                                            performances.rmse
                                        )
                                        : "N/D"}
                                </strong>

                                <small>
                                    Racine de l'erreur
                                    quadratique moyenne
                                </small>

                            </article>

                            {/* R2 */}

                            <article className="sj-metric">

                                <span>R²</span>

                                <strong>
                                    {performances
                                        ? formatNombre(
                                            performances.r2
                                        )
                                        : "N/D"}
                                </strong>

                                <small>
                                    Coefficient de détermination
                                </small>

                            </article>

                            {/* WAPE */}

                            <article className="sj-metric">

                                <span>WAPE</span>

                                <strong>
                                    {performances
                                        ? `${formatNombre(
                                            performances.wape
                                        )} %`
                                        : "N/D"}
                                </strong>

                                <small>
                                    Erreur absolue pondérée
                                    en pourcentage
                                </small>

                            </article>

                        </section>

                        {/* FORMULAIRE ET RESULTAT */}

                        <div className="sj-main-grid">

                            {/* ==============================
                                FORMULAIRE DE PREDICTION
                            ============================== */}

                            <section className="sj-panel">

                                <h2>
                                    Nouvelle prédiction
                                </h2>

                                <p className="sj-description">
                                    Renseignez les informations
                                    du produit, le stock disponible
                                    et la période souhaitée.
                                </p>

                                <form
                                    onSubmit={effectuerPrediction}
                                >

                                    <div className="sj-form-grid">

                                        {/* PRODUIT */}

                                        <label className="sj-field sj-full">

                                            <span>Produit</span>

                                            <select
                                                required
                                                disabled={chargementInitial}
                                                value={formulaire.id_produit}
                                                onChange={e =>
                                                    modifierChamp(
                                                        "id_produit",
                                                        e.target.value
                                                    )
                                                }
                                            >

                                                <option value="">

                                                    {chargementInitial
                                                        ? "Chargement des produits..."
                                                        : "Sélectionner un produit"}

                                                </option>

                                                {produits.map(produit => (

                                                    <option
                                                        key={produit.id_produit}
                                                        value={produit.id_produit}
                                                    >
                                                        {produit.nom_produit}
                                                    </option>

                                                ))}

                                            </select>

                                        </label>

                                        {/* ANNEE */}

                                        <label className="sj-field">

                                            <span>Année</span>

                                            <select
                                                value={formulaire.annee}
                                                onChange={e =>
                                                    modifierChamp(
                                                        "annee",
                                                        Number(e.target.value)
                                                    )
                                                }
                                            >

                                                {ANNEES.map(annee => (

                                                    <option
                                                        key={annee}
                                                        value={annee}
                                                    >
                                                        {annee}
                                                    </option>

                                                ))}

                                            </select>

                                        </label>

                                        {/* MOIS */}

                                        <label className="sj-field">

                                            <span>Mois</span>

                                            <select
                                                value={formulaire.mois_num}
                                                onChange={e =>
                                                    modifierChamp(
                                                        "mois_num",
                                                        Number(e.target.value)
                                                    )
                                                }
                                            >

                                                {MOIS.map((mois, index) => (

                                                    <option
                                                        key={mois}
                                                        value={index + 1}
                                                    >
                                                        {mois}
                                                    </option>

                                                ))}

                                            </select>

                                        </label>

                                        {/* SEMAINE */}

                                        <label className="sj-field">

                                            <span>Semaine</span>

                                            <select
                                                value={formulaire.semaine}
                                                onChange={e =>
                                                    modifierChamp(
                                                        "semaine",
                                                        Number(e.target.value)
                                                    )
                                                }
                                            >

                                                {SEMAINES.map(semaine => (

                                                    <option
                                                        key={semaine}
                                                        value={semaine}
                                                    >
                                                        S{semaine}
                                                    </option>

                                                ))}

                                            </select>

                                        </label>

                                        {/* PRIX */}

                                        <label className="sj-field">

                                            <span>Prix (MAD)</span>

                                            <input
                                                type="number"
                                                required
                                                min="0.01"
                                                step="0.01"
                                                value={
                                                    Number.isNaN(formulaire.prix)
                                                        ? ""
                                                        : formulaire.prix
                                                }
                                                onChange={e =>
                                                    modifierChamp(
                                                        "prix",
                                                        e.target.valueAsNumber
                                                    )
                                                }
                                            />

                                        </label>

                                        {/* NOMBRE DE LOTS */}

                                        <label className="sj-field">

                                            <span>Nombre de lots</span>

                                            <input
                                                type="number"
                                                required
                                                min="0"
                                                step="1"
                                                value={
                                                    Number.isNaN(formulaire.nombre_lots)
                                                        ? ""
                                                        : formulaire.nombre_lots
                                                }
                                                onChange={e =>
                                                    modifierChamp(
                                                        "nombre_lots",
                                                        e.target.valueAsNumber
                                                    )
                                                }
                                            />

                                        </label>

                                        {/* DUREE DE VIE */}

                                        <label className="sj-field">

                                            <span>
                                                Durée de vie (jours)
                                            </span>

                                            <input
                                                type="number"
                                                required
                                                min="1"
                                                step="1"
                                                value={
                                                    Number.isNaN(formulaire.duree_vie_jours)
                                                        ? ""
                                                        : formulaire.duree_vie_jours
                                                }
                                                onChange={e =>
                                                    modifierChamp(
                                                        "duree_vie_jours",
                                                        e.target.valueAsNumber
                                                    )
                                                }
                                            />

                                        </label>

                                        {/* PROMOTION */}

                                        <label className="sj-field sj-full">

                                            <span>Promotion</span>

                                            <select
                                                value={formulaire.promotion}
                                                onChange={e =>
                                                    modifierChamp(
                                                        "promotion",
                                                        Number(e.target.value)
                                                    )
                                                }
                                            >

                                                <option value={0}>
                                                    Non
                                                </option>

                                                <option value={1}>
                                                    Oui
                                                </option>

                                            </select>

                                        </label>

                                        {/* STOCK DISPONIBLE */}

                                        <label className="sj-field sj-full">

                                            <span>
                                                Stock disponible (unités)
                                            </span>

                                            <input
                                                type="number"
                                                required
                                                min="0"
                                                max="2147483647"
                                                step="1"
                                                placeholder="Saisir le stock disponible"
                                                value={
                                                    Number.isNaN(
                                                        formulaire.stock_disponible
                                                    )
                                                        ? ""
                                                        : formulaire.stock_disponible
                                                }
                                                onChange={e =>
                                                    modifierChamp(
                                                        "stock_disponible",
                                                        e.target.valueAsNumber
                                                    )
                                                }
                                            />

                                            <small className="sj-field-help">
                                                Quantité actuellement disponible
                                                pour le produit sélectionné.
                                            </small>

                                        </label>

                                    </div>

                                    {/* INFORMATION */}

                                    <div className="sj-info">

                                        <strong>
                                            Récupération automatique
                                            des ventes
                                        </strong>

                                        <p>
                                            Les ventes des quatre
                                            semaines précédentes sont
                                            récupérées automatiquement
                                            depuis la base de données.
                                        </p>

                                    </div>

                                    {/* INFORMATION SUR LA COMMANDE */}

                                    <div className="sj-info">

                                        <strong>
                                            Recommandation de commande
                                        </strong>

                                        <p>
                                            La quantité à commander est
                                            calculée automatiquement à partir
                                            de la quantité prédite et du stock
                                            disponible renseigné.
                                        </p>

                                    </div>

                                    {/* BOUTON DE PREDICTION */}

                                    <button
                                        type="submit"
                                        className="sj-primary"
                                        disabled={
                                            chargement ||
                                            chargementInitial ||
                                            !formulaire.id_produit
                                        }
                                    >

                                        {chargement
                                            ? "Prédiction en cours..."
                                            : "Prédire la quantité"}

                                    </button>

                                    {/* MESSAGE D'ERREUR */}

                                    {erreur && (

                                        <div
                                            className="sj-error"
                                            role="alert"
                                        >

                                            <strong>
                                                Prédiction impossible
                                            </strong>

                                            <p>{erreur}</p>

                                        </div>

                                    )}

                                </form>

                            </section>

                            {/* ==============================
                                RESULTAT DE LA PREDICTION
                            ============================== */}

                            <section
                                className="sj-panel"
                                aria-live="polite"
                            >

                                <h2>
                                    Résultat de la prédiction
                                </h2>

                                <p className="sj-description">
                                    Estimation de la demande et
                                    recommandation de commande
                                    pour la période sélectionnée.
                                </p>

                                {/* AVANT LA PREDICTION */}

                                {!resultat && (

                                    <div className="sj-empty">

                                        <h3>

                                            {chargement
                                                ? "Analyse en cours..."
                                                : erreur
                                                    ? "Résultat indisponible"
                                                    : "En attente de prédiction"}

                                        </h3>

                                        <p>

                                            {chargement
                                                ? "Le modèle analyse les informations du produit."
                                                : erreur
                                                    ? "Vérifiez les informations du formulaire puis réessayez."
                                                    : "Renseignez le formulaire pour obtenir une estimation des ventes et une recommandation de commande."}

                                        </p>

                                    </div>

                                )}

                                {/* APRES LA PREDICTION */}

                                {resultat && (

                                    <>

                                        {/* QUANTITE PREDITE */}

                                        <div className="sj-result">

                                            <span>
                                                Quantité prédite
                                            </span>

                                            <strong>

                                                {formatNombre(
                                                    resultat.quantite_predite
                                                )}

                                            </strong>

                                            <small>unités</small>

                                            <h3>
                                                {resultat.nom_produit}
                                            </h3>

                                            {periodeResultat && (

                                                <p>

                                                    {MOIS[
                                                        periodeResultat.mois_num - 1
                                                    ]}

                                                    {" "}

                                                    {periodeResultat.annee}

                                                    {" - S"}

                                                    {periodeResultat.semaine}

                                                </p>

                                            )}

                                        </div>

                                        {/* ==============================
                                            RECOMMANDATION DE COMMANDE
                                        ============================== */}

                                        <h3 className="sj-subtitle">
                                            Recommandation de commande
                                        </h3>

                                        <div className="sj-order-grid">

                                            {/* STOCK DISPONIBLE */}

                                            <article className="sj-stock-card">

                                                <span>
                                                    Stock disponible
                                                </span>

                                                <strong>
                                                    {formatNombre(
                                                        resultat.stock_disponible
                                                    )}
                                                </strong>

                                                <small>
                                                    unités
                                                </small>

                                            </article>

                                            {/* QUANTITE A COMMANDER */}

                                            <article className="sj-order-card">

                                                <span>
                                                    Quantité à commander
                                                </span>

                                                <strong>
                                                    {formatNombre(
                                                        resultat.quantite_a_commander
                                                    )}
                                                </strong>

                                                <small>
                                                    unités
                                                </small>

                                            </article>

                                        </div>

                                        {/* INTERPRETATION DE LA RECOMMANDATION */}

                                        <div className="sj-order-message">

                                            <strong>

                                                {resultat.quantite_a_commander > 0
                                                    ? "Commande recommandée"
                                                    : "Stock suffisant"}

                                            </strong>

                                            <p>

                                                {resultat.quantite_a_commander > 0
                                                    ? `Il est recommandé de commander ${formatNombre(
                                                        resultat.quantite_a_commander
                                                    )} unités supplémentaires pour couvrir la demande prévue.`
                                                    : "Le stock disponible permet de couvrir la demande prévue. Aucune commande supplémentaire n'est recommandée."}

                                            </p>

                                        </div>

                                        {/* EXPLICATION DU CALCUL */}

                                        <div className="sj-info">

                                            <strong>
                                                Calcul de la quantité à commander
                                            </strong>

                                            <p>

                                                Quantité prédite arrondie
                                                à l'entier supérieur,
                                                moins le stock disponible,
                                                avec un minimum de zéro.

                                            </p>

                                            <p>

                                                {`max(0, ${formatNombre(
                                                    Math.ceil(
                                                        resultat.quantite_predite
                                                    )
                                                )} - ${formatNombre(
                                                    resultat.stock_disponible
                                                )}) = ${formatNombre(
                                                    resultat.quantite_a_commander
                                                )} unités`}

                                            </p>

                                        </div>

                                        {/* VENTES PRECEDENTES */}

                                        <h3 className="sj-subtitle">
                                            Ventes des quatre
                                            semaines précédentes
                                        </h3>

                                        <div className="sj-sales-grid">

                                            {[
                                                resultat.ventes_s1,
                                                resultat.ventes_s2,
                                                resultat.ventes_s3,
                                                resultat.ventes_s4

                                            ].map((vente, index) => (

                                                <article
                                                    className="sj-sale"
                                                    key={index}
                                                >

                                                    <span>
                                                        S-{index + 1}
                                                    </span>

                                                    <strong>
                                                        {formatNombre(vente)}
                                                    </strong>

                                                    <small>unités</small>

                                                </article>

                                            ))}

                                        </div>

                                        {/* GRAPHIQUE DES VENTES */}

                                        <h3 className="sj-subtitle">
                                            Évolution des ventes
                                        </h3>

                                        <div
                                            className="sj-chart"
                                            role="img"
                                            aria-label={
                                                valeursGraphique
                                                    .map(item =>
                                                        `${item.nom} : ${formatNombre(item.valeur)} unités`
                                                    )
                                                    .join(", ")
                                            }
                                        >

                                            {valeursGraphique.map(
                                                (item, index) => (

                                                    <div
                                                        className="sj-chart-column"
                                                        key={item.nom}
                                                    >

                                                        <span>

                                                            {formatNombre(
                                                                item.valeur
                                                            )}

                                                        </span>

                                                        <div
                                                            className={
                                                                index === 4
                                                                    ? "sj-bar predicted"
                                                                    : "sj-bar"
                                                            }
                                                            style={{
                                                                height:
                                                                    `${Math.max(
                                                                        0,
                                                                        item.valeur /
                                                                        maximumGraphique *
                                                                        150
                                                                    )}px`
                                                            }}
                                                        />

                                                        <small>
                                                            {item.nom}
                                                        </small>

                                                    </div>

                                                )
                                            )}

                                        </div>

                                        {/* INTERVALLE SI DISPONIBLE */}

                                        {resultat.borne_inferieure != null &&
                                         resultat.borne_superieure != null && (

                                            <div className="sj-info">

                                                <strong>
                                                    Intervalle estimé
                                                </strong>

                                                <p>

                                                    De

                                                    {" "}

                                                    {formatNombre(
                                                        resultat.borne_inferieure
                                                    )}

                                                    {" à "}

                                                    {formatNombre(
                                                        resultat.borne_superieure
                                                    )}

                                                    {" unités"}

                                                </p>

                                            </div>

                                        )}

                                        {/* MESSAGE DE CONFIRMATION */}

                                        <div
                                            className="sj-success"
                                            role="status"
                                        >

                                            Prédiction et recommandation
                                            enregistrées avec succès.

                                        </div>

                                        <button
                                            type="button"
                                            className="sj-secondary"
                                            onClick={ouvrirHistorique}
                                        >

                                            Consulter l'historique

                                        </button>

                                    </>

                                )}

                            </section>

                        </div>

                    </>

                )}

                {/* ======================================
                    PAGE HISTORIQUE
                ====================================== */}

                {onglet === "historique" && (

                    <section className="sj-panel">

                        <h2>
                            Prévisions enregistrées
                        </h2>

                        <p className="sj-description">

                            Retrouvez l'ensemble des prédictions
                            et des recommandations de commande
                            enregistrées dans la base de données.

                        </p>

                        {/* RESUME DE L'HISTORIQUE */}

                        <div className="sj-history-summary">

                            <article>

                                <span>
                                    Prédictions trouvées
                                </span>

                                <strong>

                                    {chargementHistorique
                                        ? "..."
                                        : lignesFiltrees.length}

                                </strong>

                            </article>

                            <article>

                                <span>
                                    Produits concernés
                                </span>

                                <strong>

                                    {chargementHistorique
                                        ? "..."
                                        : nombreProduits}

                                </strong>

                            </article>

                        </div>

                        {/* ==============================
                            FILTRES
                        ============================== */}

                        <form
                            className="sj-filters"
                            onSubmit={e => {

                                e.preventDefault();

                                void chargerHistorique(filtres);

                            }}
                        >

                            {/* FILTRE PRODUIT */}

                            <label className="sj-field">

                                <span>Produit</span>

                                <select
                                    value={filtres.id_produit}
                                    onChange={e =>
                                        setFiltres(precedent => ({
                                            ...precedent,
                                            id_produit: e.target.value
                                        }))
                                    }
                                >

                                    <option value="">
                                        Tous les produits
                                    </option>

                                    {produits.map(produit => (

                                        <option
                                            key={produit.id_produit}
                                            value={produit.id_produit}
                                        >
                                            {produit.nom_produit}
                                        </option>

                                    ))}

                                </select>

                            </label>

                            {/* FILTRE ANNEE */}

                            <label className="sj-field">

                                <span>Année</span>

                                <select
                                    value={filtres.annee}
                                    onChange={e =>
                                        setFiltres(precedent => ({
                                            ...precedent,
                                            annee: e.target.value
                                        }))
                                    }
                                >

                                    <option value="">
                                        Toutes les années
                                    </option>

                                    {ANNEES.map(annee => (

                                        <option
                                            key={annee}
                                            value={annee}
                                        >
                                            {annee}
                                        </option>

                                    ))}

                                </select>

                            </label>

                            {/* FILTRE MOIS */}

                            <label className="sj-field">

                                <span>Mois</span>

                                <select
                                    value={filtres.mois_num}
                                    onChange={e =>
                                        setFiltres(precedent => ({
                                            ...precedent,
                                            mois_num: e.target.value
                                        }))
                                    }
                                >

                                    <option value="">
                                        Tous les mois
                                    </option>

                                    {MOIS.map((mois, index) => (

                                        <option
                                            key={mois}
                                            value={index + 1}
                                        >
                                            {mois}
                                        </option>

                                    ))}

                                </select>

                            </label>

                            {/* APPLIQUER LES FILTRES */}

                            <button
                                type="submit"
                                className="sj-primary"
                                disabled={chargementHistorique}
                            >

                                {chargementHistorique
                                    ? "Chargement..."
                                    : "Filtrer"}

                            </button>

                            {/* REINITIALISER */}

                            <button
                                type="button"
                                className="sj-secondary"
                                onClick={reinitialiserFiltres}
                                disabled={chargementHistorique}
                            >

                                Réinitialiser

                            </button>

                        </form>

                        {/* ==============================
                            RECHERCHE, TRI ET EXPORT
                        ============================== */}

                        <div className="sj-toolbar">

                            {/* RECHERCHE */}

                            <label className="sj-field">

                                <span>
                                    Rechercher un produit
                                </span>

                                <input
                                    type="search"
                                    placeholder="Nom du produit..."
                                    value={recherche}
                                    onChange={e => {

                                        setRecherche(
                                            e.target.value
                                        );

                                        setPage(1);

                                    }}
                                />

                            </label>

                            {/* TRI */}

                            <label className="sj-field">

                                <span>Trier par</span>

                                <select
                                    value={tri}
                                    onChange={e => {

                                        setTri(e.target.value);

                                        setPage(1);

                                    }}
                                >

                                    <option value="date-desc">
                                        Date : plus récente
                                    </option>

                                    <option value="date-asc">
                                        Date : plus ancienne
                                    </option>

                                    <option value="quantite-desc">
                                        Quantité : décroissante
                                    </option>

                                    <option value="quantite-asc">
                                        Quantité : croissante
                                    </option>

                                </select>

                            </label>

                            {/* EXPORT CSV */}

                            <button
                                type="button"
                                className="sj-secondary"
                                onClick={exporterCSV}
                                disabled={
                                    chargementHistorique ||
                                    lignesFiltrees.length === 0
                                }
                            >

                                Exporter CSV

                            </button>

                        </div>

                        {/* ERREUR HISTORIQUE */}

                        {erreurHistorique && (

                            <div
                                className="sj-error"
                                role="alert"
                            >

                                {erreurHistorique}

                            </div>

                        )}

                        {/* ==============================
                            TABLEAU DE L'HISTORIQUE
                        ============================== */}

                        <div className="sj-table-wrapper">

                            <table className="sj-table">

                                <thead>

                                    <tr>

                                        <th>ID</th>

                                        <th>Produit</th>

                                        <th>Année</th>

                                        <th>Mois</th>

                                        <th>Semaine</th>

                                        <th>Quantité prédite</th>

                                        <th>Stock disponible</th>

                                        <th>Quantité à commander</th>

                                        <th>Quantité réelle</th>

                                        <th>Date de prédiction</th>

                                    </tr>

                                </thead>

                                <tbody>

                                    {/* CHARGEMENT */}

                                    {chargementHistorique ? (

                                        <tr>

                                            <td colSpan={10}>

                                                Chargement des
                                                prédictions...

                                            </td>

                                        </tr>

                                    ) : erreurHistorique ? (

                                        <tr>

                                            <td colSpan={10}>

                                                Impossible de charger
                                                les prédictions.

                                            </td>

                                        </tr>

                                    ) : lignesFiltrees.length === 0 ? (

                                        <tr>

                                            <td colSpan={10}>

                                                Aucune prédiction
                                                trouvée.

                                            </td>

                                        </tr>

                                    ) : (

                                        lignesPage.map(h => (

                                            <tr key={h.id_prediction}>

                                                {/* IDENTIFIANT */}

                                                <td>
                                                    {h.id_prediction}
                                                </td>

                                                {/* PRODUIT */}

                                                <td>
                                                    {h.nom_produit}
                                                </td>

                                                {/* ANNEE */}

                                                <td>
                                                    {h.annee}
                                                </td>

                                                {/* MOIS */}

                                                <td>
                                                    {MOIS[h.mois_num - 1]}
                                                </td>

                                                {/* SEMAINE */}

                                                <td>
                                                    S{h.semaine}
                                                </td>

                                                {/* QUANTITE PREDITE */}

                                                <td className="sj-quantity">

                                                    {formatNombre(
                                                        h.quantite_predite
                                                    )}

                                                </td>

                                                {/* STOCK DISPONIBLE */}

                                                <td className="sj-stock-cell">

                                                    {h.stock_disponible != null

                                                        ? formatNombre(
                                                            h.stock_disponible
                                                        )

                                                        : "Non disponible"}

                                                </td>

                                                {/* QUANTITE A COMMANDER */}

                                                <td className="sj-order-cell">

                                                    {h.quantite_a_commander != null

                                                        ? formatNombre(
                                                            h.quantite_a_commander
                                                        )

                                                        : "Non disponible"}

                                                </td>

                                                {/* QUANTITE REELLE */}

                                                <td>

                                                    {h.quantite_reelle != null

                                                        ? formatNombre(
                                                            h.quantite_reelle
                                                        )

                                                        : "Non disponible"}

                                                </td>

                                                {/* DATE DE PREDICTION */}

                                                <td>

                                                    {new Date(
                                                        h.date_prediction
                                                    ).toLocaleString("fr-FR")}

                                                </td>

                                            </tr>

                                        ))

                                    )}

                                </tbody>

                            </table>

                        </div>

                        {/* ==============================
                            PAGINATION
                        ============================== */}

                        <div className="sj-pagination">

                            <span className="sj-count">

                                {chargementHistorique

                                    ? "Chargement..."

                                    : lignesFiltrees.length > 0

                                        ? `Affichage de ${debutPage + 1} à ${finPage} sur ${lignesFiltrees.length} prédictions`

                                        : "0 prédiction"}

                            </span>

                            <div className="sj-page-controls">

                                <button
                                    type="button"
                                    className="sj-secondary"
                                    disabled={
                                        pageActive <= 1 ||
                                        chargementHistorique
                                    }
                                    onClick={() =>
                                        setPage(pageActive - 1)
                                    }
                                >

                                    Précédent

                                </button>

                                <strong>

                                    Page {pageActive} sur {totalPages}

                                </strong>

                                <button
                                    type="button"
                                    className="sj-secondary"
                                    disabled={
                                        pageActive >= totalPages ||
                                        chargementHistorique
                                    }
                                    onClick={() =>
                                        setPage(pageActive + 1)
                                    }
                                >

                                    Suivant

                                </button>

                            </div>

                        </div>

                    </section>

                )}

                {/* ======================================
                    PIED DE PAGE
                ====================================== */}

                <footer className="sj-footer">

                    StockJuste - Intelligence artificielle
                    et gestion intelligente des stocks

                </footer>

            </div>

        </main>

    );
}