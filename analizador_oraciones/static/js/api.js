// =========================
// api.js
// Responsabilidad: comunicación con el servidor.
// Si cambia la URL o el protocolo, solo se toca este archivo.
// =========================

const API_URL = "http://localhost:8000/corregir";
// para una app local — si tarda más, algo está mal y es mejor avisar.
const TIMEOUT_MS = 11000;

async function consultarAPI(texto) {
  // parámetro timeout nativo como en otras librerías.
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const respuesta = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto }),
      signal: controller.signal, // conecta el timeout al fetch
    });

    if (!respuesta.ok) {
      throw new Error(
        `Error del servidor: ${respuesta.status} ${respuesta.statusText}`,
      );
    }

    return await respuesta.json();
  } catch (error) {
    // AbortError significa que se superó el timeout — damos un mensaje claro.
    // Cualquier otro error (red caída, CORS, etc.) se reenvía tal cual.
    if (error.name === "AbortError") {
      throw new Error(
        "La solicitud tardó demasiado. ¿Está corriendo localhost:8000?",
      );
    }
    throw error; // deja que app.js o drag-mode.js lo muestren al usuario
  } finally {
    // finally se ejecuta siempre — tanto si hubo éxito como si hubo error.
    // Limpia el timer para que no quede ejecutándose en memoria aunque
    // la petición ya terminó antes del timeout.
    clearTimeout(timeoutId);
  }
}
