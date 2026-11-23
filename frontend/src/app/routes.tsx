import { useState } from "react";
import { Link, Route, Routes } from "react-router-dom";
import { getHealth } from "../services/api";
import LoginPage from "../features/auth/LoginPage";
import SignupPage from "../features/auth/SignupPage";

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
        <Link to="/connexion">Connexion</Link>{" "}
        <Link to="/produits">Produits</Link>{" "}
        <Link to="/alertes">Alertes</Link>
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
      <Route path="/connexion" element={<LoginPage />} />
      <Route path="/inscription" element={<SignupPage />} />
      <Route path="/produits" element={<ProductsPage />} />
      <Route path="/alertes" element={<AlertsPage />} />
    </Routes>
  );
}