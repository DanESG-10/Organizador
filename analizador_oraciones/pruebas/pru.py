import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from core.servicios.analizador import Analizador
from core.servicios.construir_chunks import ConstructorDeChunks
from core.servicios.evaluador_oraciones import EvaluadorNaturalidad
from core.servicios.generar_frases import GeneradorOraciones

# ============================================================
# CORPUS DE EVALUACIÓN — Anexo A (56 oraciones)
# Formato: (estructura, gold_standard, entrada_desordenada)
# ============================================================

CORPUS = [
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
    ("AUX_PART", "La puerta fue cerrada con llave", "llave con cerrada fue puerta la"),
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
        "Los niños están trepando el árbol",
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


def analizar_oracion(texto):
    analizador = Analizador()
    return analizador.analizar_oracion(texto)


def generar_chunks(tokens):
    constructor = ConstructorDeChunks()
    return constructor.generar_chunks(tokens)


def generar_frases(chunks):
    generador = GeneradorOraciones()
    return generador.generar_frases(chunks)


def evaluar_corpus():
    evaluador = EvaluadorNaturalidad(mostrar_logs=False)
    resultados_finales = []
    correctas_global = 0

    print("\n" + "=" * 60)
    print("PROCESANDO EVALUACIÓN Y GENERANDO CSV")
    print("=" * 60)

    for i, (estructura, gold, entrada) in enumerate(CORPUS, 1):
        # Proceso del sistema
        tokens = analizar_oracion(entrada)
        chunks = generar_chunks(tokens)
        candidatas = generar_frases(chunks)
        mejor = evaluador.elegir_mejor_frase(candidatas, chunks)

        salida = mejor.texto if mejor else "SIN SALIDA"
        es_correcto = salida.strip().lower() == gold.strip().lower()

        if es_correcto:
            correctas_global += 1

        # 1. Lógica de Error: Solo marcar E3 si falló habiendo múltiples opciones
        tipo_error = "Error" if (not es_correcto and len(candidatas) > 1) else ""

        # 2. Verificar si usó el corrector de POS (de settings.py)
        uso_corrector = "No"
        palabras_entrada = entrada.split()
        # Accedemos a settings.CORRECCIONES_POS que definiste en settings.py
        for p in palabras_entrada:
            if p.lower() in settings.CORRECCIONES_POS:
                uso_corrector = "Sí"
                break

        # Guardar datos para el archivo
        resultados_finales.append(
            {
                "ID": i,
                "Salida del sistema": salida,
                "Correcto (0/1)": 1 if es_correcto else 0,
                "Tipo de error": tipo_error,
                "Usó corrección": uso_corrector,
            }
        )

        print(f"[{i:02d}] {'OK' if es_correcto else 'FALLO'} - {estructura}")

    # ============================================================
    # EXPORTAR A CSV (Compatible con Excel)
    # ============================================================
    output_path = Path(__file__).parent / "evaluacion_resultados_Flash.csv"

    with open(output_path, mode="w", encoding="utf-8-sig", newline="") as f:
        # Usamos utf-8-sig para que Excel reconozca los tildes automáticamente
        campos = [
            "ID",
            "Salida del sistema",
            "Correcto (0/1)",
            "Tipo de error",
            "Usó corrección",
        ]
        writer = csv.DictWriter(
            f, fieldnames=campos, delimiter=";"
        )  # Delimitador ';' es mejor para Excel en español

        writer.writeheader()
        writer.writerows(resultados_finales)

    print("\n" + "=" * 60)
    print(
        f"EMR GLOBAL: {correctas_global}/{len(CORPUS)} ({round(correctas_global / len(CORPUS) * 100, 1)}%)"
    )
    print(f"Archivo generado: {output_path.name}")
    print("=" * 60)


if __name__ == "__main__":
    evaluar_corpus()
