import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.servicios.analizador import Analizador
from core.servicios.construir_chunks import ConstructorDeChunks
from core.servicios.evaluador_oraciones import EvaluadorNaturalidad
from core.servicios.generar_frases import GeneradorOraciones

# ============================================================
# CORPUS DE EVALUACIÓN — Anexo A (56 oraciones)
# Formato: (estructura, gold_standard, entrada_desordenada)
# ============================================================

CORPUS = [
    # SVO
    ("SVO", "El niño come una manzana", "manzana una niño el come"),
    ("SVO", "Valentina estudiaba la lección", "la Valentina estudiaba lección"),
    ("SVO", "yo saqué la basura", "la saqué basura yo"),
    ("SVO", "Emily lee un libro", "libro Emily un lee"),
    ("SVO", "la niña jugó en el parque", "parque la jugó el niña en"),
    ("SVO", "Nosotros jugaremos en el parque", "jugaremos el nosotros parque en"),
    ("SVO", "Julián compró una computadora", "una compró Julián computadora"),
    # SVO con ADJ en sujeto
    ("SVO_ADJ_suj", "El coche rojo ganó la carrera", "ganó rojo el carrera la coche"),
    (
        "SVO_ADJ_suj",
        "El gato negro persigue a un ratón",
        "ratón un a gato persigue negro el",
    ),
    (
        "SVO_ADJ_suj",
        "Las flores amarillas adornan el jardín",
        "amarillas jardín el las adornan flores",
    ),
    (
        "SVO_ADJ_suj",
        "El hombre cansado duerme en su casa",
        "casa cansado su hombre duerme el en",
    ),
    (
        "SVO_ADJ_suj",
        "Los estudiantes rebeldes dañaron la puerta",
        "puerta rebeldes la estudiantes dañaron los",
    ),
    (
        "SVO_ADJ_suj",
        "La lluvia incesante arruinó el paseo",
        "arruinó lluvia paseo la el incesante",
    ),
    (
        "SVO_ADJ_suj",
        "El vecino ruidoso vendió su equipo",
        "equipo ruidoso vendió su vecino el",
    ),
    # SVO con ADJ en objeto
    (
        "SVO_ADJ_obj",
        "El estudiante resuelve un problema complejo",
        "complejo resuelve problema un estudiante el",
    ),
    (
        "SVO_ADJ_obj",
        "La mujer baila una canción preciosa",
        "preciosa una mujer baila canción la",
    ),
    ("SVO_ADJ_obj", "Mi abuela hizo sopa caliente", "caliente sopa hizo abuela mi"),
    ("SVO_ADJ_obj", "El perro mordió la cama nueva", "nueva perro la cama el mordió"),
    (
        "SVO_ADJ_obj",
        "La chica dibuja una casa grande",
        "grande chica una casa la dibuja",
    ),
    (
        "SVO_ADJ_obj",
        "El Carpintero reparó la mesa dañada",
        "dañada reparó carpintero la mesa el",
    ),
    (
        "SVO_ADJ_obj",
        "la modista cose un vestido elegante",
        "elegante un modista vestido la cose",
    ),
    # Aux + participio
    (
        "AUX_PART",
        "La carta fue escrita por Luciano",
        "por Luciano escrita fue carta la",
    ),
    (
        "AUX_PART",
        "Las leyes fueron aprobadas por el congreso",
        "congreso el por aprobadas fueron leyes las",
    ),
    (
        "AUX_PART",
        "La motocicleta fue reparada por el mecánico",
        "mecánico el por reparada fue motocicleta la",
    ),
    (
        "AUX_PART",
        "los exploradores han encontrado el tesoro",
        "tesoro el encontrado han exploradores los",
    ),
    ("AUX_PART", "Daniel ha visto la película", "película la visto ha Daniel"),
    ("AUX_PART", "La puerta está cerrada con llave", "llave con cerrada fue puerta la"),
    ("AUX_PART", "Ella ha terminado la tarea", "tarea la terminado ha ella"),
    # Copulativo
    ("COPULATIVO", "La casa es de Carlos", "Carlos de casa la es"),
    ("COPULATIVO", "El café está caliente", "caliente café el está"),
    ("COPULATIVO", "Tus primos parecen cansados", "cansados primos parecen tus"),
    ("COPULATIVO", "El televisor es grande", "grande televisor el es"),
    ("COPULATIVO", "los zapatos estaban en la mesa", "mesa la en estaban zapatos los"),
    ("COPULATIVO", "El computador parecía nuevo", "nuevo computador parecía el"),
    ("COPULATIVO", "Yo era el capitán", "capitán el era yo"),
    # Gerundio
    (
        "GERUNDIO",
        "Nosotros estamos viendo televisión",
        "televisión viendo estamos nosotros",
    ),
    ("GERUNDIO", "Ella está escribiendo un libro", "libro un escribiendo está ella"),
    ("GERUNDIO", "Él va aprendiendo la lección", "lección la aprendiendo va él"),
    (
        "GERUNDIO",
        "El conductor maneja hablando por teléfono",
        "teléfono por hablando maneja conductor el",
    ),
    (
        "GERUNDIO",
        "Los niños están trepando el arbol",
        "árbol el trepando están niños los",
    ),
    (
        "GERUNDIO",
        "Los estudiantes están realizando la tarea",
        "tarea la realizando están estudiantes los",
    ),
    (
        "GERUNDIO",
        "El perro está persiguiendo la pelota",
        "pelota la persiguiendo está perro el",
    ),
    # Negativo
    ("NEGATIVO", "El joven no trajo su cuaderno", "cuaderno su trajo no joven el"),
    (
        "NEGATIVO",
        "El coronel no recibió el mensaje",
        "mensaje el recibió no coronel el",
    ),
    ("NEGATIVO", "La tienda no abre los domingos", "domingos los abre no tienda la"),
    (
        "NEGATIVO",
        "La policía no atrapó a los ladrones",
        "ladrones los a atrapó no policía la",
    ),
    ("NEGATIVO", "Ese perro no es mío", "perro mío no ese es"),
    ("NEGATIVO", "Yo no fui a la escuela", "escuela la a fui no yo"),
    ("NEGATIVO", "Él no come verduras", "verduras come no él"),
    # Modal
    (
        "MODAL",
        "La empresa quiere mejorar el servicio",
        "servicio el mejorar quiere empresa la",
    ),
    ("MODAL", "La gente necesita comprar comida", "comida comprar necesita gente la"),
    (
        "MODAL",
        "El grupo intenta resolver el problema",
        "problema el resolver intenta grupo el",
    ),
    (
        "MODAL",
        "Ellos pueden usar la fotocopiadora",
        "fotocopiadora la usar pueden ellos",
    ),
    (
        "MODAL",
        "El equipo intenta ganar el partido",
        "partido el ganar intenta equipo el",
    ),
    ("MODAL", "Mi amigo suele hablar de política", "política de hablar suele amigo mi"),
    ("MODAL", "Ustedes pueden visitar el museo", "museo el visitar pueden ustedes"),
]

# ============================================================
# FUNCIONES WRAPPER (igual que en test.py)
# ============================================================


def analizar_oracion(texto):
    analizador = Analizador()
    return analizador.analizar_oracion(texto)


def generar_chunks(tokens):
    constructor = ConstructorDeChunks()
    return constructor.generar_chunks(tokens)


def generar_frases(chunks):
    generador = GeneradorOraciones()
    return generador.generar_frases(chunks)


# ============================================================
# CLASIFICADOR DE ERROR
# ============================================================


def clasificar_error(tokens, chunks, candidatas, resultado_correcto):
    """
    Determina la capa del pipeline donde se originó el fallo.

    E1 — Error de etiquetado: spaCy asignó POS incorrecto y la palabra
         no estaba cubierta por CORRECCIONES_POS. Se detecta cuando el
         sistema no logra identificar el núcleo verbal por mala etiqueta.
    E2 — Error de chunking: el etiquetado fue correcto pero los chunks
         se construyeron mal (actantes invertidos, verbo incompleto, etc.)
    E3 — Error de selección GPT-2: la candidata correcta fue generada
         pero el evaluador eligió otra permutación.
    OK — Sin error.
    """
    if resultado_correcto:
        return "OK"

    # Sin verbo identificado: fallo temprano, probable error de etiquetado
    if not chunks.tiene_verbo():
        return "E1"

    # Con verbo pero sin frases nominales donde se esperan: fallo de chunking
    if not chunks.tiene_frases_nominales():
        return "E2"

    # GPT-2 intervino (más de una candidata) y el resultado fue incorrecto
    if len(candidatas) > 1:
        return "E3"

    # Una candidata, incorrecta: el fallo está en la generación (chunking)
    return "E2"


# ============================================================
# EVALUACIÓN PRINCIPAL
# ============================================================


def evaluar_corpus():
    """
    Corre las 56 oraciones del corpus, registra evidencia por capas
    y exporta los resultados a evaluacion_resultados.csv
    """
    evaluador = EvaluadorNaturalidad(mostrar_logs=False)
    resultados = []

    print("\n" + "=" * 60)
    print("EVALUACIÓN FORMAL DEL CORPUS — FASE 4")
    print("=" * 60)

    for i, (estructura, gold, entrada) in enumerate(CORPUS, 1):
        # --- Capa 1: etiquetado ---
        tokens = analizar_oracion(entrada)
        pos_tags = [(t.texto, t.pos) for t in tokens]

        # --- Capa 2: construcción de chunks ---
        chunks = generar_chunks(tokens)
        verbo = chunks.verbo_pre
        fn = [(fn.texto, fn.genero, fn.numero) for fn in chunks.fn]
        adj = chunks.adj

        # --- Capa 3: generación y selección ---
        candidatas = generar_frases(chunks)
        mejor = evaluador.elegir_mejor_frase(candidatas, chunks)

        salida = mejor.texto if mejor else "SIN SALIDA"
        n_candidatas = len(candidatas)

        # Puntajes GPT-2 solo cuando intervino
        if n_candidatas > 1:
            puntajes = [
                (c.texto, round(c.puntaje_naturalidad, 4))
                for c in candidatas
                if c.puntaje_naturalidad is not None
            ]
            margen = (
                round(
                    max(c.puntaje_naturalidad for c in candidatas)
                    - min(c.puntaje_naturalidad for c in candidatas),
                    4,
                )
                if puntajes
                else None
            )
        else:
            puntajes = []
            margen = None

        # --- Criterio de acierto: coincidencia exacta ---
        correcto = salida.strip().lower() == gold.strip().lower()

        # --- Clasificación de error ---
        tipo_error = clasificar_error(tokens, chunks, candidatas, correcto)

        # --- Registro de la fila ---
        fila = {
            "N": i,
            "Estructura": estructura,
            "Entrada": entrada,
            "Gold_standard": gold,
            "Salida_sistema": salida,
            "POS_tags": str(pos_tags),
            "Verbo_identificado": str(verbo),
            "FN_identificadas": str(fn),
            "ADJ_identificados": str(adj),
            "N_candidatas": n_candidatas,
            "Puntajes_GPT2": str(puntajes) if puntajes else "N/A",
            "Margen_GPT2": margen if margen is not None else "N/A",
            "Correcto": "SI" if correcto else "NO",
            "Tipo_error": tipo_error,
        }
        resultados.append(fila)

        # Impresión en consola (estilo test.py)
        estado = "OK" if correcto else f"FALLO [{tipo_error}]"
        print(f"\n[{i:02d}] {estructura} — {estado}")
        print(f"  Entrada:  {entrada}")
        print(f"  Salida:   {salida}")
        print(f"  Esperado: {gold}")
        if n_candidatas > 1:
            print(f"  GPT-2 eligió entre {n_candidatas} candidatas | margen: {margen}")
        print(f"  Verbo: {verbo} | FN: {fn}")

    # ============================================================
    # MÉTRICAS AGREGADAS
    # ============================================================

    print("\n" + "=" * 60)
    print("RESULTADOS POR ESTRUCTURA")
    print("=" * 60)

    estructuras = {}
    for r in resultados:
        est = r["Estructura"]
        if est not in estructuras:
            estructuras[est] = {"total": 0, "correctas": 0, "E1": 0, "E2": 0, "E3": 0}
        estructuras[est]["total"] += 1
        if r["Correcto"] == "SI":
            estructuras[est]["correctas"] += 1
        else:
            estructuras[est][r["Tipo_error"]] += 1

    total_global = len(resultados)
    correctas_global = sum(1 for r in resultados if r["Correcto"] == "SI")

    for est, datos in estructuras.items():
        emr = round(datos["correctas"] / datos["total"] * 100, 1)
        errores = datos["total"] - datos["correctas"]
        print(f"\n  {est}")
        print(f"    EMR: {datos['correctas']}/{datos['total']} ({emr}%)")
        if errores > 0:
            print(
                f"    Errores -> E1: {datos['E1']} | E2: {datos['E2']} | E3: {datos['E3']}"
            )

    emr_global = round(correctas_global / total_global * 100, 1)
    print(f"\n{'=' * 60}")
    print(f"EMR GLOBAL: {correctas_global}/{total_global} ({emr_global}%)")

    errores_total = total_global - correctas_global
    if errores_total > 0:
        e1 = sum(1 for r in resultados if r["Tipo_error"] == "E1")
        e2 = sum(1 for r in resultados if r["Tipo_error"] == "E2")
        e3 = sum(1 for r in resultados if r["Tipo_error"] == "E3")
        print(f"Distribucion de errores ({errores_total} total):")
        print(f"  E1 (etiquetado POS): {e1} ({round(e1 / errores_total * 100, 1)}%)")
        print(f"  E2 (chunking):       {e2} ({round(e2 / errores_total * 100, 1)}%)")
        print(f"  E3 (seleccion GPT2): {e3} ({round(e3 / errores_total * 100, 1)}%)")

    # Oraciones donde GPT-2 intervino
    con_gpt2 = [r for r in resultados if r["N_candidatas"] > 1]
    if con_gpt2:
        correctas_gpt2 = sum(1 for r in con_gpt2 if r["Correcto"] == "SI")
        print(f"\nGPT-2 intervino en {len(con_gpt2)} oraciones")
        print(
            f"  Tasa de seleccion correcta: {correctas_gpt2}/{len(con_gpt2)} "
            f"({round(correctas_gpt2 / len(con_gpt2) * 100, 1)}%)"
        )

    print("=" * 60)

    # ============================================================
    # EXPORTAR CSV
    # ============================================================

    output_path = Path(__file__).parent / "evaluacion_resultados_flax.csv"
    campos = [
        "N",
        "Estructura",
        "Entrada",
        "Gold_standard",
        "Salida_sistema",
        "POS_tags",
        "Verbo_identificado",
        "FN_identificadas",
        "ADJ_identificados",
        "N_candidatas",
        "Puntajes_GPT2",
        "Margen_GPT2",
        "Correcto",
        "Tipo_error",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(resultados)

    print(f"\nResultados exportados a: {output_path}")
    print(
        "Abre evaluacion_resultados_flax.csv para revisar el detalle oración por oración."
    )


if __name__ == "__main__":
    evaluar_corpus()
