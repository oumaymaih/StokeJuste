import { useState } from "react";
import { Link, Route, Routes } from "react-router-dom";
import { getHealth } from "../services/api";

// Import du module de prediction
import PredictionPage from "../features/prediction/PredictionPage";

function HomePage() {
  const [message, setMessage] = useState("");

  async function testBackend() {
    try {
      const result = await getHealth();
      setMessage(result.message);
    } catch {
      setMessage("Le backend ne répond pas.");
    }
  }

  return (
    <main>
      <h1>StokeJuste</h1>
      <p>Gestion du stock et réduction du gaspillage.</p>

      <nav>
        <Link to="/produits">Produits</Link>{" "}
        <Link to="/alertes">Alertes</Link>{" "}
        <Link to="/prediction">Prédiction des ventes</Link>
      </nav>

      <button onClick={testBackend}>
        Tester la connexion au backend
      </button>

      <p>{message}</p>
    </main>
  );
}

function ProductsPage() {
  return <h1>Gestion des produits — à développer</h1>;
}

function AlertsPage() {
  return <h1>Gestion des alertes — à développer</h1>;
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/produits" element={<ProductsPage />} />
      <Route path="/alertes" element={<AlertsPage />} />

      {/* Route du module de prediction */}
      <Route path="/prediction" element={<PredictionPage />} />

    </Routes>
  );
}