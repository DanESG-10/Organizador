"""
Configuración centralizada del proyecto.
"""

from typing import Set

# import os


class Settings:
    """
    Configuración global de la aplicación.
    """

    # === MODELOS NLP ===
    SPACY_MODEL: str = "es_core_news_lg"
    GPT2_MODEL: str = "DeepESP/gpt2-spanish"

    # === PALABRAS ESPECIALES ===
    # Sustantivos que pueden funcionar como verbos
    SUSTANTIVOS_VERBALES: Set[str] = {
        "baila",
        "copia",
        "manda",
        "eres",
        "guarda",
        "cura",
        "compra",
        "canto",
        "uso",
        "copio",
        "pelea",
        "bebe",
        "mira",
        "ama",
        "odia",
        "baja",
        "caza",
        "pesca",
        "cosecha",
        "siembra",
        "barniza",
        "borda",
        "rema",
        "patina",
        "brinca",
        "trota",
        "escala",
        "resbala",
        "gira",
        "ata",
        "suelta",
        "agarra",
        "pega",
        "empuña",
        "lanza",
        "tira",
        "custodia",
        "combate",
        "debate",
        "corta",
        "rota",
        "afloja",
        "martilla",
        "atornilla",
        "pilota",
        "bucea",
        "surfea",
        "trepa",
        "empuja",
        "nada",
        "es",
        "ladra",
        "vino",
        "entrevista",
        "muerde",
        "para",
    }
    # terminaciones de infinitivo y gerundio
    terminaciones_no_personales = ("ar", "er", "ir", "ando", "iendo", "yendo")

    ARTICULOS_DEFINIDOS: Set[str] = {"el", "la", "los", "las"}

    # Preposiciones especiales
    PREPOSICIONES_ESPECIALES: Set[str] = {
        "a",
        "desde",
        "entre",
        "hacia",
        "según",
        "hasta",
        "contra",
        "sin",
    }

    # Terminaciones de participios
    TERMINACIONES_PARTICIPIO: list[str] = [
        "oto",
        "lto",
        "ado",
        "ido",
        "sto",
        "cho",
        "rto",
        "sta",
        "das",
        "dos",
        "ada",
        "do",
        "ito",
        "cha",
        "rita",
    ]

    # Correcciones de POS tags
    CORRECCIONES_POS: dict = {
        # Palabras que spaCy etiqueta mal
        "perro": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "carpintero": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "acertijo": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "mar": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "celular": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "tejado": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "universidad": {"pos": "NOUN", "gen": "Fem", "num": "Sing"},
        "ave": {"pos": "NOUN", "num": "Sing"},
        "bebé": {"pos": "NOUN", "num": "Sing"},
        "pájaro": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "clóset": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "techo": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "cuarto": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "horno": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "armario": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "agua": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "médico": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "paciente": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "anciano": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "delincuente": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "español": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "autobus": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "bus": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "vida": {"pos": "NOUN", "gen": "Fem", "num": "Sing"},
        # DET y VERB
        "mi": {"pos": "DET", "num": "Sing"},
        "este": {"pos": "DET", "gen": "Masc", "num": "Sing"},
        "ese": {"pos": "DET", "gen": "Masc", "num": "Sing"},
        "esa": {"pos": "DET", "gen": "Fem", "num": "Sing"},
        "puede": {"pos": "VERB", "num": "Sing"},
        "marchitan": {"pos": "VERB", "num": "Plur"},
        # Etiquetados porteriores a la prueba diagnóstico.
        # cat 1
        "rojo": {"pos": "ADJ", "gen": "Masc", "num": "Sing"},
        "vestido": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "negro": {"pos": "ADJ", "gen": "Masc", "num": "Sing"},
        # cat 2
        # "baila": {"pos": "VERB", "num": "Sing"},   puede ser un noun, se refiere al nombre de un pez
        "mecánico": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        "tus": {"pos": "DET", "num": "Plur"},
        "primos": {"pos": "NOUN", "gen": "Masc", "num": "Plur"},
        "joven": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
        # categoria 3
        "puerta": {"pos": "NOUN", "gen": "Fem", "num": "Sing"},
        "teléfono": {"pos": "NOUN", "gen": "Masc", "num": "Sing"},
    }
    # posibles actualizaciones, permitir: verbo+nexo+verbo_inf con starswitch
    """ === DICCIONARIOS DE PERÍFRASIS ===
    AUXILIARES_A = {"ir", "empezar", "comenzar", "volver", "ponerse", "venir", "aprender"}
    AUXILIARES_DE = {"acabar", "tratar", "dejar", "parar", "terminar", "cesar"}
    AUXILIARES_QUE = {"tener", "haber"}
    """

    # === CONFIGURACIÓN DE API ===
    APP_NAME: str = "NLP Sentence Analyzer"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # === CONFIGURACIÓN DE EVALUACIÓN ===
    # Si usar GPT-2 para evaluar naturalidad
    USE_GPT2_EVALUATION: bool = True
    # Número máximo de oraciones a generar
    MAX_SENTENCES: int = 10


# Instancia global de configuración
settings = Settings()
