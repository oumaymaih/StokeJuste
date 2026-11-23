import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import "./auth.css";

export function LogoBox() {
  return (
    <svg viewBox="0 0 48 48" fill="none">
      <path d="M24 4 42 14v20L24 44 6 34V14z" fill="#f97316" />
      <path d="M24 4 42 14 24 24 6 14z" fill="#fb923c" />
      <path d="M24 24v20" stroke="#fff" strokeWidth="2" />
    </svg>
  );
}

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(false);
  const [lang, setLang] = useState<"FR" | "AR">("FR");
  const [error, setError] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setError("");
    if (!email.includes("@")) return setError("Adresse e-mail invalide.");
    if (password.length < 8)
      return setError("Le mot de passe doit contenir au moins 8 caractères.");

    // TODO : appeler POST /api/auth/login quand le backend sera prêt
    console.log("Connexion", { email, remember });
  };

  return (
    <div className="auth-page">
      <section className="auth-brand">
        <h1 className="auth-logo">
          <LogoBox />
          <div>
            Stock<span>Juste</span>
          </div>
        </h1>
        <p className="auth-slogan">Gérez mieux. Ne gaspillez plus.</p>
        <h2>
          Votre partenaire pour une gestion de stock{" "}
          <span className="accent">intelligente et durable</span>
        </h2>
        <ul>
          <li>Suivi en temps réel de vos stocks</li>
          <li>Alertes intelligentes (péremption et rupture)</li>
          <li>Prévisions de la demande avec l'IA</li>
        </ul>
      </section>

      <section className="auth-card">
        <div className="lang">
          <button className={lang === "FR" ? "on" : ""} onClick={() => setLang("FR")}>FR</button>
          <button className={lang === "AR" ? "on" : ""} onClick={() => setLang("AR")}>العربية</button>
        </div>

        <div className="auth-tabs">
          <Link className="tab active" to="/connexion">Connexion</Link>
          <Link className="tab" to="/inscription">Créer un compte</Link>
        </div>

        <h3>Bienvenue sur StockJuste</h3>
        <p className="auth-sub">Connectez-vous pour accéder à votre espace</p>

        <form onSubmit={handleSubmit} noValidate>
          <label className="field icon">
            <svg className="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="5" width="18" height="14" rx="2" /><path d="m3 7 9 6 9-6" />
            </svg>
            <input type="email" placeholder="Adresse e-mail" value={email}
              onChange={(e) => setEmail(e.target.value)} autoComplete="email" />
          </label>

          <label className="field icon">
            <svg className="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="4" y="11" width="16" height="10" rx="2" /><path d="M8 11V7a4 4 0 0 1 8 0v4" />
            </svg>
            <input type={showPassword ? "text" : "password"} placeholder="Mot de passe"
              value={password} onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password" />
            <button type="button" className="toggle" onClick={() => setShowPassword(!showPassword)}>
              {showPassword ? "Masquer" : "Afficher"}
            </button>
          </label>

          <div className="row">
            <label className="check">
              <input type="checkbox" checked={remember}
                onChange={(e) => setRemember(e.target.checked)} />
              Se souvenir de moi
            </label>
            <Link to="/mot-de-passe-oublie">Mot de passe oublié ?</Link>
          </div>

          {error && <p className="error">{error}</p>}

          <button type="submit" className="btn-primary">Se connecter</button>
        </form>

        <div className="sep">Ou</div>

        <button type="button" className="btn-social">
          <svg viewBox="0 0 48 48">
            <path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9.1 3.6l6.8-6.8C35.8 2.4 30.3 0 24 0 14.6 0 6.5 5.4 2.6 13.2l7.9 6.1C12.4 13.6 17.7 9.5 24 9.5z" />
            <path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.7c-.6 3-2.3 5.5-4.8 7.2l7.6 5.9c4.4-4.1 7-10.1 7-17.6z" />
            <path fill="#FBBC05" d="M10.5 28.7a14.500 14.500 0 0 1 0-9.4l-7.9-6.1a24 24 0 0 0 0 21.6z" />
            <path fill="#34A853" d="M24 48c6.5 0 11.9-2.100 15.900-5.800l-7.600-5.900c-2.100 1.400-4.900 2.300-8.300 2.300-6.300 0-11.600-4.100-13.500-9.800l-7.900 6.100C6.500 42.600 14.600 48 24 48z" />
          </svg>
          Continuer avec Google
        </button>
        <button type="button" className="btn-social">
          <svg viewBox="0 0 24 24">
            <rect x="1" y="1" width="10" height="10" fill="#f25022" />
            <rect x="13" y="1" width="10" height="10" fill="#7fba00" />
            <rect x="1" y="13" width="10" height="10" fill="#00a4ef" />
            <rect x="13" y="13" width="10" height="10" fill="#ffb900" />
          </svg>
          Continuer avec Microsoft
        </button>

        <p className="bottom">
          Vous n'avez pas de compte ? <Link className="link" to="/inscription">Créer un compte</Link>
        </p>
      </section>
    </div>
  );
}