// =========================
// app.js — Modo Animación
// Depende de: dom.js, utils.js (deben cargarse antes en el HTML)
// Todas las referencias DOM viven en dom.js
// Sería conveniente separar el modo animación de aquí
// =========================

// ── ESTADO ───────────────────────────────────────────
let estadoPendiente = null;
let palabrasOrigActuales = [];

// ui-controller.js necesita saber si hay un resultado pendiente y poder limpiarlo,
// pero no debe tocar estadoPendiente directamente — estas funciones son la interfaz.
function hayResultadoPendiente() {
  return estadoPendiente !== null;
}
function limpiarPendiente() {
  estadoPendiente = null;
}

// ── FLUJO PRINCIPAL ───────────────────────────────────

async function mostrarYProcesar() {
  const texto = elInput.value.trim();
  if (!texto) return;

  elBtnEnviar.disabled = true;
  ocultarError(elErrorMsg);
  elOpcionesWrap.style.display = "none";
  elBtnRevelar.classList.remove("visible");
  elPanelRes.classList.remove("listo");
  elFichasDest.innerHTML = '<span class="ph">Esperando resultado...</span>';
  estadoPendiente = null;

  colapsarInput(elInputWrap);

  const palabrasOrig = texto.split(/\s+/);
  palabrasOrigActuales = palabrasOrig;

  await mostrarOriginales(palabrasOrig);
  mostrarEstado(elEstadoMsg, elEstadoTexto, "Analizando la oración...");

  try {
    const data = await consultarAPI(texto); // utils.js

    estadoPendiente = data;
    ocultarEstado(elEstadoMsg);
    elBtnRevelar.classList.add("visible");
    elPanelRes.classList.add("listo");
    elBtnEnviar.disabled = false;
    marcarEnvio(); // ui-controller.js
  } catch (error) {
    ocultarEstado(elEstadoMsg);
    mostrarError(
      elErrorMsg,
      "No se pudo conectar. ¿Está corriendo localhost:8000?",
    );
    elBtnEnviar.disabled = false;
    expandirInput(elInputWrap, elInput);
  }
}

async function revelarResultado() {
  if (!estadoPendiente) return;

  elBtnRevelar.classList.remove("visible");
  const data = estadoPendiente;
  estadoPendiente = null;

  const palabrasDest = data.texto_corregido.trim().split(/\s+/);
  await animarVuelo(palabrasOrigActuales, palabrasDest);

  const otras = (data.opciones || []).filter(
    (op) =>
      op.trim().toLowerCase() !== data.texto_corregido.trim().toLowerCase(),
  );

  if (otras.length > 0) {
    elOpcionesLista.innerHTML = "";
    otras.forEach((opcion) => {
      const boton = document.createElement("button");
      boton.className = "opcion-btn";
      boton.textContent = opcion;
      boton.onclick = () =>
        reanimar(palabrasOrigActuales, opcion.trim().split(/\s+/));
      elOpcionesLista.appendChild(boton);
    });
    elOpcionesWrap.style.display = "block";
  }

  elBtnEnviar.disabled = false;
}

// ── RENDERIZADO ───────────────────────────────────────

async function mostrarOriginales(palabras) {
  resetColores();
  elFichasOrig.innerHTML = "";

  palabras.forEach((palabra, i) => {
    const ficha = crearFicha(palabra, i, false);
    elFichasOrig.appendChild(ficha);
  });

  await wait(palabras.length * 70 + 100);
  await agitarFichas(elFichasOrig);
}

async function animarVuelo(palabrasOrig, palabrasDest) {
  elFichasDest.innerHTML = "";

  const fantasmas = palabrasDest.map((palabra, i) => {
    const ghost = document.createElement("div");
    ghost.className = "ficha-ghost";
    ghost.textContent = palabra;
    ghost.style.background = getColor(palabra, i);
    elFichasDest.appendChild(ghost);
    return ghost;
  });

  await wait(60);

  const fichasOriginales = Array.from(elFichasOrig.querySelectorAll(".ficha"));
  const usados = new Set();

  for (let i = 0; i < palabrasDest.length; i++) {
    const palabra = palabrasDest[i];
    const color = getColor(palabra, i);
    const ghost = fantasmas[i];

    let fichaOrig = null;
    for (let j = 0; j < fichasOriginales.length; j++) {
      if (
        !usados.has(j) &&
        fichasOriginales[j].dataset.palabra.toLowerCase() ===
          palabra.toLowerCase()
      ) {
        fichaOrig = fichasOriginales[j];
        usados.add(j);
        break;
      }
    }

    const rectDest = ghost.getBoundingClientRect();

    if (fichaOrig) {
      const rectOrig = fichaOrig.getBoundingClientRect();
      fichaOrig.style.opacity = "0.2";
      await volarFicha(palabra, color, rectOrig, rectDest);
    }

    ghost.classList.remove("ficha-ghost");
    ghost.classList.add("ficha", "anim-glow");
    ghost.style.opacity = "1";

    await wait(70);
  }
}

async function reanimar(orig, dest) {
  elFichasDest.innerHTML = '<span class="ph">Reordenando...</span>';
  elFichasOrig
    .querySelectorAll(".ficha")
    .forEach((f) => (f.style.opacity = "1"));
  await wait(160);
  await animarVuelo(orig, dest);
}

// ── EVENTOS ───────────────────────────────────────────
elInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") enviar(); // ui-controller.js — respeta el modo activo (ACCION_ENVIO)
});
