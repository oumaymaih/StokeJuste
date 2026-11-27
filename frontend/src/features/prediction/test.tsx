import { createRoot } from "react-dom/client";

import {
    BrowserRouter,
    Routes,
    Route,
    Link
} from "react-router-dom";

import PredictionPage from "./PredictionPage";


// ==================================================
// 1. RECUPERATION DE L'ELEMENT ROOT
// ==================================================

const root = document.getElementById("root");

if (!root) {
    throw new Error(
        "Élément root introuvable."
    );
}


// ==================================================
// 2. PAGE D'ACCUEIL TEMPORAIRE POUR LES TESTS
// ==================================================

function AccueilTest() {

    return (

        <div style={{ padding: "40px" }}>

            <h1>Accueil StockJuste</h1>

            <p>
                Le tableau de bord commun sera disponible
                après l'intégration des modules.
            </p>

            <Link to="/prediction">
                Accéder à la prédiction des ventes
            </Link>

        </div>

    );
}


// ==================================================
// 3. CONFIGURATION DES ROUTES DE TEST
// ==================================================

createRoot(root).render(

    <BrowserRouter>

        <Routes>

            {/* Page de test du module */}

            <Route
                path="/src/features/prediction/prediction-test.html"
                element={<PredictionPage />}
            />

            {/* Page de prediction */}

            <Route
                path="/prediction"
                element={<PredictionPage />}
            />

            {/* Page d'accueil temporaire */}

            <Route
                path="/tableau-de-bord"
                element={<AccueilTest />}
            />

        </Routes>

    </BrowserRouter>

);