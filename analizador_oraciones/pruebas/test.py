import sys  # Busca los módulos dentro de la carpeta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.servicios.analizador import Analizador
from core.servicios.construir_chunks import ConstructorDeChunks
from core.servicios.evaluador_oraciones import EvaluadorNaturalidad
from core.servicios.generar_frases import GeneradorOraciones


def pruebas_rapidas():
    """Pruebas rápidas con GPT-2 para casos ambiguos (estilo original)"""
    casos = [
        "ganó rojo el carrera la coche",
        "elegante un modista vestido la cose",
        "perro no ese es mío",
    ]
    """, ""ganó rojo el carrera la coche",
        "ratón el a gato persigue negro un",
        "equipo ruidoso vendió su vecino el",
        "preciosa una mujer baila canción la",
        "grande chica una casa la dibuja",
        "elegante un modista vestido la cose",
        "mecánico el por reparada fue motocicleta la",
        "llave con cerrada fue puerta la",
        "partido el ganar intenta equipo el",
        "estudiantes los estudian la en biblioteca",
        "preciosa una mujer baila canción la",
        "perro no ese es mío",
        "cansados primos parecen tus",
        "teléfono por hablando maneja conductor el",
        "cuaderno su trajo no joven el","""

    print("\n" + "=" * 60)
    print("PRUEBAS RÁPIDAS CON GPT-2")
    print("=" * 60)

    # Instancias (Evaluador SIN logs para ser más limpio)
    evaluador = EvaluadorNaturalidad(mostrar_logs=True)  # Sin logs

    for texto in casos:
        tokens = analizar_oracion(texto)
        chunks = generar_chunks(tokens)
        opciones = generar_frases(chunks)
        print(f"  fn: {[(fn.texto, fn.genero, fn.numero) for fn in chunks.fn]}")
        print(f"  adj: {chunks.adj}")
        print(f"  verbo_pre: {chunks.verbo_pre}")
        print(f"  verbo_num: {chunks.verbo_num}")
        print(f"  verbo_gen: {chunks.verbo_gen}")
        print(f"  imper: {chunks.pron_imp}")
        print(f"ambiguedades: {chunks.combinaciones_ambiguas}")
        print(tokens)

        # Usar evaluador (él maneja si carga GPT-2 o no)
        mejor = evaluador.elegir_mejor_frase(opciones, chunks)

        print(f"\n'{texto}'")
        if mejor:
            if len(opciones) == 1:
                print(f"  → {mejor.texto}")
            else:
                # Caso ambiguo: mostrar la elegida por GPT-2
                print(
                    f"  → {mejor.texto} (GPT-2 eligió entre {len(opciones)} opciones)"
                )
        else:
            print("  → No se pudo reorganizar")

    print("\n" + "=" * 60)


# Funciones wrapper para mantener tu estilo
def analizar_oracion(texto):
    """Wrapper para mantener tu estilo original"""
    analizador = Analizador()
    return analizador.analizar_oracion(texto)


def generar_chunks(tokens):
    """Wrapper para mantener tu estilo original"""
    constructor = ConstructorDeChunks()
    return constructor.generar_chunks(tokens)


def generar_frases(chunks):
    """Wrapper para mantener tu estilo original"""
    generador = GeneradorOraciones()
    return generador.generar_frases(chunks)


# Ejecutar solo pruebas rápidas:
if __name__ == "__main__":
    pruebas_rapidas()
