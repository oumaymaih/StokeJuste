const API_URL =
  import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export async function getHealth(): Promise<{ message: string }> {
  const response = await fetch(`${API_URL}/api/health`);

  if (!response.ok) {
    throw new Error("Erreur lors de la connexion au backend.");
  }

  return response.json();
}