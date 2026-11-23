import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { LogoBox } from "./LoginPage";
import "./auth.css";

type Form = {
  nom: string;
  email: string;
  telephone: string;
  motDePasse: string;
  nomCommercial: string;
  typeCommerce: string;
  adresse: string;
  ville: string;
};

const TYPES = ["Restaurant", "Supermarché", "Épicerie", "Boulangerie", "Pharmacie", "Autre"];
const STEPS = ["Informations personnelles", "Informations de l'établissement", "Confirmation"];

export default function SignupPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState<Form>({
    nom: "", email: "", telephone: "", motDePasse: "",
    nomCommercial: "", typeCommerce: "Restaurant", adresse: "", ville: "",
  });

  const set = (k: keyof Form) => (e: { target: { value: string } }) =>
    setForm({ ...form, [k]: e.target.value });

  const validate = (): string => {
    if (step === 1) {
      if (!form.nom.trim()) return "Le nom complet est obligatoire.";
      if (!form.email.includes("@")) return "Adresse e-mail invalide.";
      if (!/^\d{9}$/.test(form.telephone.replace(/\s/g, "")))
        return "Téléphone invalide (9 chiffres après +212).";
      if (form.motDePasse.length < 8)
        return "Le mot de passe doit contenir au moins 8 caractères.";
    }
    if (step === 2) {
      if (!form.nomCommercial.trim()) return "Le nom commercial est obligatoire.";
      if (!form.adresse.trim()) return "L'adresse est obligatoire.";
      if (!form.ville.trim()) return "La ville est obligatoire.";
    }
    return "";
  };

  const next = () => {
    const msg = validate();
    if (msg) return setError(msg);
    setError("");
    setStep(step + 1);
  };

  const back = () => {
    setError("");
    if (step === 1) navigate("/connexion");
    else setStep(step - 1);
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    // TODO : appeler POST /api/auth/register quand le backend sera prêt
    console.log("Inscription", { ...form, telephone: "+212" + form.telephone });
    navigate("/connexion");
  };

  return (
    <div className="auth-page signup">
      <section className="auth-brand">
        <h1 className="auth-logo">
          <LogoBox />
          <div>
            Stock<span>Juste</span>
          </div>
        </h1>
        <p className="auth-slogan">Gérez mieux. Ne gaspillez plus.</p>
        <h2>
          Rejoignez notre plateforme et gérez votre commerce{" "}
          <span className="accent">plus efficacement</span>
        </h2>
        <ul>
          <li>Suivi en temps réel de vos stocks</li>
          <li>Alertes intelligentes (péremption et rupture)</li>
          <li>Prévisions de la demande avec l'IA</li>
        </ul>
      </section>

      <section className="auth-card wide">
        <h3 className="left">Créer un compte commerçant</h3>
        <p className="auth-sub left">Complétez vos informations pour démarrer</p>

        <div className="stepper">
          {STEPS.map((label, i) => {
            const n = i + 1;
            const cls = n === step ? "active" : n < step ? "done" : "";
            return (
              <div key={label} className={`step ${cls}`}>
                <div className="dot">{n < step ? "✓" : n}</div>
                {label}
              </div>
            );
          })}
        </div>

        <form onSubmit={handleSubmit} noValidate>
          {step === 1 && (
            <>
              <div className="grid2">
                <div className="field">
                  <label className="lbl">Nom complet *</label>
                  <input placeholder="Votre nom et prénom" value={form.nom} onChange={set("nom")} />
                </div>
                <div className="field">
                  <label className="lbl">Email professionnel *</label>
                  <input type="email" placeholder="exemple@votrecommerce.ma"
                    value={form.email} onChange={set("email")} />
                </div>
                <div className="field">
                  <label className="lbl">Téléphone *</label>
                  <div className="phone">
                    <span className="prefix">🇲🇦 +212</span>
                    <input placeholder="6 12 34 56 78" value={form.telephone}
                      onChange={set("telephone")} />
                  </div>
                </div>
                <div className="field">
                  <label className="lbl">Mot de passe *</label>
                  <input type={showPassword ? "text" : "password"} placeholder="Minimum 8 caractères"
                    value={form.motDePasse} onChange={set("motDePasse")} autoComplete="new-password" />
                  <button type="button" className="toggle" onClick={() => setShowPassword(!showPassword)}>
                    {showPassword ? "Masquer" : "Afficher"}
                  </button>
                </div>
              </div>
            </>
          )}

          {step === 2 && (
            <>
              <div className="section-title">🏪 Informations de votre établissement</div>
              <div className="grid2">
                <div className="field">
                  <label className="lbl">Nom commercial *</label>
                  <input placeholder="Mon Restaurant" value={form.nomCommercial}
                    onChange={set("nomCommercial")} />
                </div>
                <div className="field">
                  <label className="lbl">Type de commerce *</label>
                  <select value={form.typeCommerce} onChange={set("typeCommerce")}>
                    {TYPES.map((t) => <option key={t}>{t}</option>)}
                  </select>
                </div>
                <div className="field">
                  <label className="lbl">Adresse *</label>
                  <input placeholder="123 Rue Principale, Casablanca" value={form.adresse}
                    onChange={set("adresse")} />
                </div>
                <div className="field">
                  <label className="lbl">Ville *</label>
                  <input placeholder="Casablanca" value={form.ville} onChange={set("ville")} />
                </div>
              </div>
            </>
          )}

          {step === 3 && (
            <>
              <div className="section-title">Vérifiez vos informations</div>
              <dl className="summary">
                <dt>Nom complet</dt><dd>{form.nom}</dd>
                <dt>Email</dt><dd>{form.email}</dd>
                <dt>Téléphone</dt><dd>+212 {form.telephone}</dd>
                <dt>Établissement</dt><dd>{form.nomCommercial} ({form.typeCommerce})</dd>
                <dt>Adresse</dt><dd>{form.adresse}, {form.ville}</dd>
              </dl>
            </>
          )}

          {error && <p className="error">{error}</p>}

          <div className="actions">
            <button type="button" className="btn-outline" onClick={back}>
              {step === 1 ? "Annuler" : "Retour"}
            </button>
            {step < 3 ? (
              <button type="button" className="btn-primary" onClick={next}>Suivant →</button>
            ) : (
              <button type="submit" className="btn-primary">Créer mon compte</button>
            )}
          </div>
        </form>

        <p className="bottom">
          Vous avez déjà un compte ? <Link className="link" to="/connexion">Se connecter</Link>
        </p>
      </section>
    </div>
  );
}