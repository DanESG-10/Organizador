from typing import List, Optional, Tuple

from config.settings import settings

from core.modelos.chunks import Chunks
from core.modelos.token_datos import Token
from core.servicios.validar_concor import ValidarConcordancia


class ConstructorDeChunks:
    def __init__(self):
        self.validador = ValidarConcordancia()

    def generar_chunks(self, tokens: List[Token]) -> Chunks:
        """
        se usan las funciones necesaria para llenar
        el contenedor de chunks
        """
        chunks = Chunks()
        self.indices_usados = set()

        # ORDEN DE PROCESAMIENTO
        self._agregar_verbo(chunks, tokens)
        self._agregar_preposiciones(chunks, tokens)

        # Guardar total_dets ANTES de marcar ningún índice
        _, self.total_dets = self._extraer_determinantes(tokens)

        # Detectar y manejar ambigüedad
        hay_amb, det_info, nouns, adjs = self._detectar_ambiguedad(tokens)

        if hay_amb:
            self._procesar_ambiguedad(chunks, det_info, nouns, adjs)
        else:
            self._agregar_frases_nominales(chunks, tokens)
            self._agregar_det_huerfano(chunks, tokens)
            self._agregar_nouns_sin_articulos(chunks, tokens)

        # Agregar elementos restantes
        self._agregar_pronombres_impersonales(chunks, tokens)
        self._agregar_nombres_propios(chunks, tokens)
        self._agregar_adjetivos(chunks, tokens)
        self._agregar_adverbios(chunks, tokens)

        return chunks

    # EMPEZAMOS CON EL VERBO

    def _agregar_verbo(self, chunks: Chunks, tokens: List[Token]) -> None:
        """
        Orden de búsqueda:
        1. AUX + participio ("ha comido")
        2. VERB simple ("corre")
        3. Sustantivos verbales ("baila", "copia")
        """
        # 1. Buscar AUX + participio
        aux_idx = self._buscar_auxiliar(chunks, tokens)
        if aux_idx is not None:
            self._buscar_participio(chunks, tokens)
            self._buscar_gerundio_o_infinitivo(chunks, tokens)
            return

        if self._buscar_verbo_simple(chunks, tokens):
            # Si encontró el simple, intentamos agregarle un gerundio acompañante
            # sin salir de la función todavía.
            self._buscar_gerundio_o_infinitivo(chunks, tokens)
            return

        # 3. Si no hubo VERB simple, intentar agregar SOLO el gerundio
        if self._buscar_gerundio_o_infinitivo(chunks, tokens):
            return

        # 4. Caso extremo: Si sigue sin haber verbo, buscar sustantivo verbal
        if not chunks.tiene_verbo():
            self._buscar_sustantivo_verbal(chunks, tokens)

    def _buscar_auxiliar(self, chunks: Chunks, tokens: List[Token]) -> Optional[int]:
        """
        Busca verbo auxiliar (AUX). -- Índice del AUX encontrado, o None
        """
        for i, token in enumerate(tokens):
            if token.pos == "AUX" and i not in self.indices_usados:
                chunks.agregar_verbo(token.texto)
                chunks.verbo_num = token.num if token.num else ""
                self.indices_usados.add(i)
                return i
        return None

    def _buscar_participio(self, chunks: Chunks, tokens: List[Token]) -> None:
        """
        Busca participio después de AUX. Primero busca como NOUN, luego como ADJ.
        """
        # Buscar participio como VERB, luego NOUN y luego ADJ
        for i, token in enumerate(tokens):
            if i in self.indices_usados:
                continue
            if self._es_participio(token.texto) and token.pos == "VERB":
                chunks.agregar_verbo(token.texto)
                chunks.verbo_gen = token.gen if token.gen else ""
                self.indices_usados.add(i)
                return
        # Buscar NOUN
        for i, token in enumerate(tokens):
            if i in self.indices_usados:
                continue
            if self._es_participio(token.texto) and token.pos == "NOUN":
                chunks.agregar_verbo(token.texto)
                chunks.verbo_gen = token.gen if token.gen else ""
                self.indices_usados.add(i)
                return
        # Buscar participio como ADJ
        for i, token in enumerate(tokens):
            if i in self.indices_usados:
                continue
            if self._es_participio(token.texto) and token.pos == "ADJ":
                chunks.agregar_verbo(token.texto)
                chunks.verbo_gen = token.gen if token.gen else ""
                self.indices_usados.add(i)
                return

    def _buscar_verbo_simple(self, chunks: Chunks, tokens: List[Token]) -> bool:
        """
        Busca verbo principal (VERB). True si encontró verbo, False si no
        """
        for i, token in enumerate(tokens):
            if token.pos == "VERB" and i not in self.indices_usados:
                texto_min = token.texto.lower()

                # Si termina en gerundio o infinitivo, lo saltamos
                if texto_min.endswith(settings.terminaciones_no_personales):
                    continue

                # Si pasa el filtro, es nuestro verbo conjugado
                chunks.agregar_verbo(token.texto)
                chunks.verbo_num = token.num if token.num else ""
                self.indices_usados.add(i)
                return True

        return False

    def _buscar_sustantivo_verbal(self, chunks: Chunks, tokens: List[Token]) -> None:
        """
        Busca sustantivos que pueden funcionar como verbos.
        Ssi no hay verbo hasta ahora.
        """
        # Solo buscar si no hay verbo
        if chunks.tiene_verbo():
            return

        for i, token in enumerate(tokens):
            if i in self.indices_usados:
                continue

            if token.texto.lower() in settings.SUSTANTIVOS_VERBALES:
                chunks.agregar_verbo(token.texto)
                chunks.verbo_num = "Sing"
                self.indices_usados.add(i)
                return

    def _es_participio(self, palabra: str) -> bool:
        """Verifica si una palabra tiene terminación de participio."""

        return any(palabra.endswith(t) for t in settings.TERMINACIONES_PARTICIPIO)

    def _buscar_gerundio_o_infinitivo(
        self, chunks: Chunks, tokens: List[Token]
    ) -> bool:
        """
        Busca un verbo gerundio o infinitivo. Devuelve True si encontró uno.
        """
        terminaciones_gerundio = ("ando", "iendo", "yendo")
        terminaciones_infinitivo = ("ar", "er", "ir")

        for i, token in enumerate(tokens):
            if i in self.indices_usados:
                continue

            texto_min = token.texto.lower()
            es_gerundio = texto_min.endswith(terminaciones_gerundio)
            es_infinitivo = texto_min.endswith(terminaciones_infinitivo)

            if (es_gerundio or es_infinitivo) and token.pos in ["VERB", "AUX"]:
                chunks.agregar_verbo(token.texto)
                self.indices_usados.add(i)
                return True  # Éxito
        return False

    # PREPOSICIONES
    def _agregar_preposiciones(self, chunks: Chunks, tokens: List[Token]) -> None:
        """
        Agrega preposiciones al chunk verbal.
        """
        for i, token in enumerate(tokens):
            if i in self.indices_usados:
                continue

            es_prepo = token.pos == "ADP" or (
                token.pos == "NOUN"
                and token.texto.lower() in settings.PREPOSICIONES_ESPECIALES
            )

            if es_prepo:
                chunks.agregar_verbo(token.texto)
                self.indices_usados.add(i)
                break

    ## AMBIGUEDAD
    def _detectar_ambiguedad(
        self, tokens: List[Token]
    ) -> Tuple[bool, Optional[Tuple], List[Tuple], List[Tuple]]:
        """
        Detecta si hay ambigüedad sintáctica.
        Ambigüedad: UN DET + DOS+ NOUNs compatibles
        Ejemplo: "el perro come pescado"

        Returns:
            Tupla de 4 elementos:
            - hay_ambiguedad (bool)
            - det_info (Tuple[int, Token] o None)
            - nouns_compatibles (List[Tuple[int, Token]])
            - adjs_compatibles (List[Tuple[int, Token]])
        """
        dets_ordenados, total_dets = self._extraer_determinantes(tokens)

        # Debe haber exactamente 1 DET
        if total_dets != 1:
            return False, None, [], []

        i_det, det = dets_ordenados[0]

        # Buscar NOUNs compatibles con este DET
        nouns_compatibles = []
        for i, token in enumerate(tokens):
            if token.pos == "NOUN" and i not in self.indices_usados:
                if self.validador.validar_concordancia([det], token):
                    nouns_compatibles.append((i, token))

        # Debe haber 2 o más NOUNs
        if len(nouns_compatibles) <= 1:
            return False, None, [], []

        # Buscar ADJs compatibles con alguno de los NOUNs
        adjs_compatibles = []
        for i, token in enumerate(tokens):
            if token.pos == "ADJ" and i not in self.indices_usados:
                for _, noun in nouns_compatibles:
                    if self.validador.validar_concordancia([noun], token):
                        adjs_compatibles.append((i, token))
                        break

        return True, (i_det, det), nouns_compatibles, adjs_compatibles

    def _procesar_ambiguedad(
        self,
        chunks: Chunks,
        det_info: Tuple[int, Token],
        nouns_compatibles: List[Tuple[int, Token]],
        adjs_compatibles: List[Tuple[int, Token]],
    ) -> None:
        """
        Procesa casos ambiguos generando combinaciones posibles.
        Refactoriza: procesar_datos_ambiguos() de orden.py (líneas 238-296)
        Genera 2 o 4 combinaciones según si hay ADJ.
        """
        i_det, det = det_info
        det_token = det.texto

        # Tomar los primeros 2 NOUNs
        (i_noun1, noun1), (i_noun2, noun2) = nouns_compatibles[0], nouns_compatibles[1]
        sus1, sus2 = noun1.texto, noun2.texto

        combinaciones = []

        if not adjs_compatibles:
            # 2 COMBINACIONES SIN ADJ
            combinaciones = [
                {"sujeto": f"{det_token} {sus1}", "objeto": sus2},
                {"sujeto": f"{det_token} {sus2}", "objeto": sus1},
            ]
        else:
            # 4 COMBINACIONES CON ADJ
            i_adj, adj = adjs_compatibles[0]
            adj_token = adj.texto

            combinaciones = [
                {"sujeto": f"{det_token} {sus1} {adj_token}", "objeto": sus2},
                {"sujeto": f"{det_token} {sus2} {adj_token}", "objeto": sus1},
                {"sujeto": f"{det_token} {sus1}", "objeto": f"{sus2} {adj_token}"},
                {"sujeto": f"{det_token} {sus2}", "objeto": f"{sus1} {adj_token}"},
            ]

            # Marcar ADJ como usado
            self.indices_usados.add(i_adj)

        # Guardar combinaciones
        chunks.combinaciones_ambiguas = combinaciones

        # Marcar índices como usados
        self.indices_usados.update([i_det, i_noun1, i_noun2])

    # FRASES NOMINALES

    def _agregar_frases_nominales(self, chunks: Chunks, tokens: List[Token]) -> None:
        """
        Construye frases nominales DET + NOUN.
        Por cada DET busca el primer NOUN que concuerde.
        Prioridad: NOUNs con morfología completa primero, None/None al final.
        El validador decide si concuerdan según lo que tenga cada token.
        Si un NOUN termina en -s pero tiene num=Sing y no hay otro NOUN
        plural disponible, se permite que concuerde con DET plural.
        """
        dets_ordenados, _ = self._extraer_determinantes(tokens)

        for i_det, det in dets_ordenados:
            if i_det in self.indices_usados:
                continue

            # Prioridad: gen+num primero, luego parciales, luego None/None
            nouns_con_todo = [
                (i, t)
                for i, t in enumerate(tokens)
                if t.pos == "NOUN"
                and i not in self.indices_usados
                and t.tiene_gen()
                and t.tiene_num()
            ]
            nouns_parciales = [
                (i, t)
                for i, t in enumerate(tokens)
                if t.pos == "NOUN"
                and i not in self.indices_usados
                and (t.tiene_gen() or t.tiene_num())
                and not (t.tiene_gen() and t.tiene_num())
            ]
            nouns_sin_nada = [
                (i, t)
                for i, t in enumerate(tokens)
                if t.pos == "NOUN"
                and i not in self.indices_usados
                and not t.tiene_gen()
                and not t.tiene_num()
            ]
            nouns_ordenados = nouns_con_todo + nouns_parciales + nouns_sin_nada

            for i_noun, noun in nouns_ordenados:
                # Revisar si aplica permitir_plural
                permitir_plural = self._noun_puede_ser_plural(noun, tokens, i_noun)

                if not self.validador.validar_concordancia(
                    [det], noun, permitir_plural
                ):
                    continue

                # Concordancia válida → construir FN y guardar
                chunks.agregar_frase_nominal(
                    texto=f"{det.texto} {noun.texto}",
                    genero=noun.gen if noun.tiene_gen() else det.gen,
                    numero=noun.num if noun.tiene_num() else det.num,
                )
                self.indices_usados.add(i_det)
                self.indices_usados.add(i_noun)
                break

    def _noun_puede_ser_plural(
        self, noun: Token, tokens: List[Token], i_noun: int
    ) -> bool:
        """
        Determina si un NOUN que termina en -s pero tiene num=Sing
        puede tratarse como plural.
        Solo aplica si no hay otro NOUN disponible con num=Plur
        o que termine en -s que compita por el mismo DET.
        """
        # Solo aplica si termina en -s y tiene num=Sing
        if not noun.texto.lower().endswith("s"):
            return False
        if noun.num != "Sing":
            return False

        # Revisar si hay otro NOUN que sea claramente plural
        for i, token in enumerate(tokens):
            if token.pos != "NOUN" or i in self.indices_usados or i == i_noun:
                continue
            if token.num == "Plur" or token.texto.lower().endswith("s"):
                return False  # Hay competencia, no forzar plural

        return True

    def _agregar_det_huerfano(self, chunks: Chunks, tokens: List[Token]) -> None:
        """
        Si quedó algún DET sin emparejar, busca un ADJ compatible.
        Cubre casos donde spaCy clasifica un sustantivo como ADJ.
        Ejemplo: "los químicos" → "químicos" etiquetado como ADJ
        Solo se activa si hay DETs sin usar Y no quedan NOUNs disponibles.
        Si aún hay NOUNs libres, el DET les pertenece a ellos.
        """
        # Si hay algún NOUN sin usar, no tocar ADJs
        hay_nouns_disponibles = any(
            token.pos == "NOUN" and i not in self.indices_usados
            for i, token in enumerate(tokens)
        )
        if hay_nouns_disponibles:
            return

        for i_det, det in enumerate(tokens):
            if det.pos != "DET" or i_det in self.indices_usados:
                continue

            # Hay un DET huérfano → buscar ADJ compatible
            for i_adj, adj in enumerate(tokens):
                if adj.pos != "ADJ" or i_adj in self.indices_usados:
                    continue

                if not self.validador.validar_concordancia([det], adj):
                    continue

                # Concordancia válida → construir FN
                chunks.agregar_frase_nominal(
                    texto=f"{det.texto} {adj.texto}",
                    genero=adj.gen if adj.tiene_gen() else det.gen,
                    numero=adj.num if adj.tiene_num() else det.num,
                )
                self.indices_usados.add(i_det)
                self.indices_usados.add(i_adj)
                break

    def _extraer_determinantes(
        self, tokens: List[Token]
    ) -> Tuple[List[Tuple[int, Token]], int]:
        """
        Extrae y clasifica determinantes en definidos e indefinidos.
        Refactoriza: extraer_determinantes()
        """
        # Identificar determinantes
        dets_indices = []
        for i, token in enumerate(tokens):
            if token.pos == "DET" and i not in self.indices_usados:
                dets_indices.append((i, token))

        # Separar definidos e indefinidos
        dets_definidos = []
        dets_indefinidos = []

        for i, det in dets_indices:
            if det.tiene_gen():
                dets_definidos.append((i, det))
            else:
                dets_indefinidos.append((i, det))

        # Ordenar: definidos primero
        dets_ordenados = dets_definidos + dets_indefinidos
        total_dets = len(dets_indices)

        return dets_ordenados, total_dets

    def _buscar_adj_compatible(
        self, chunk_actual: List[Token], tokens: List[Token]
    ) -> Tuple[Optional[int], Optional[Token]]:
        """
        Busca el primer ADJ compatible con el chunk actual.

        Returns:
            Tupla (índice, token) o (None, None) si no encuentra
        """
        for i, token in enumerate(tokens):
            if token.pos != "ADJ" or i in self.indices_usados:
                continue

            if self.validador.validar_concordancia(chunk_actual, token):
                return i, token

        return None, None

    # OTROS ELEMENTOS

    def _agregar_nouns_sin_articulos(self, chunks: Chunks, tokens: List[Token]) -> None:
        """
        Agrega sustantivos sueltos (sin determinante).
        Refactoriza: agregar_nombres_sin_articulos() de orden.py (líneas 401-412)
        """
        for i, token in enumerate(tokens):
            if i in self.indices_usados:
                continue

            if token.pos == "NOUN":
                chunks.agregar_frase_nominal(
                    texto=token.texto, genero=token.gen, numero=token.num
                )
                self.indices_usados.add(i)

    def _agregar_nombres_propios(self, chunks: Chunks, tokens: List[Token]) -> None:
        """
        Agrega nombres propios y pronombres.

        Refactoriza: agregar_nombres_propios_pronombres() de orden.py (líneas 414-421)
        """
        for i, token in enumerate(tokens):
            if i in self.indices_usados:
                continue

            if token.pos == "PROPN":
                chunks.agregar_frase_nominal(
                    texto=token.texto,
                    genero=token.gen,
                    numero=token.num,
                    es_propio=True,
                )
                self.indices_usados.add(i)

            elif (
                token.pos == "PRON"
            ):  # and token.texto.lower() not in PRONOMBRES_IMPERSONALES:
                # Pronombre personal (él, ella, ellos, nosotros...)
                chunks.agregar_frase_nominal(
                    texto=token.texto,
                    genero=token.gen if token.gen else None,
                    numero=token.num if token.num else None,
                    es_propio=True,
                )
                self.indices_usados.add(i)

    def _agregar_pronombres_impersonales(
        self, chunks: Chunks, tokens: List[Token]
    ) -> None:
        """
        Agrega pronombres impersonales.
        """
        JERARQUIA = [
            "se",
            "te",
            "me",
            "le",
            "lo",
            "la",
            "nos",
            "os",
            "les",
            "las",
            "los",
        ]
        MAX_PRON_IMP = 3

        # Recolectar todos los pronombres impersonales presentes (sin usar)
        candidatos = []
        for i, token in enumerate(tokens):
            if i in self.indices_usados:
                continue
            if token.pos == "PRON" and token.texto.lower() in JERARQUIA:
                candidatos.append((i, token))

        # Ordenar por jerarquía y tomar hasta MAX_PRON_IMP
        candidatos.sort(key=lambda x: JERARQUIA.index(x[1].texto.lower()))
        seleccionados = candidatos[:MAX_PRON_IMP]

        for i, token in seleccionados:
            chunks.pron_imp.append(token.texto)
            self.indices_usados.add(i)

    def _agregar_adjetivos(self, chunks: Chunks, tokens: List[Token]) -> None:
        """Coordina la lógica de adjetivos según el número de DETs en la oración.
        - 2 DETs → _adj_dos_dets (valida contra fn1 y fn2)
        - 1 DET  → _adj_un_det  (valida contra fn1, depende de PROPN)
        """

        if self.total_dets >= 2:
            self._adj_dos_dets(chunks, tokens)
        else:
            self._adj_un_det(chunks, tokens)

    def _agregar_adverbios(self, chunks: Chunks, tokens: List[Token]) -> None:
        """
        Agrega adverbios de negación.

        Refactoriza: agregar_adverbios() de orden.py (líneas 442-452)
        """
        adverbios_negacion = {"no", "nunca", "jamás", "tampoco", "ni"}

        for i, token in enumerate(tokens):
            if i in self.indices_usados:
                continue

            if token.pos == "ADV" and token.texto.lower() in adverbios_negacion:
                chunks.adv_negacion = token.texto
                chunks.adv.append(token.texto)
                self.indices_usados.add(i)
                break

    def _adj_dos_dets(self, chunks: Chunks, tokens: List[Token]) -> None:
        """
        Cuando hay 2 DETs, busca ADJs y valida concordancia contra fn1 y fn2.
        - Concuerda con ambas  → 4 combinaciones ambiguas
        - Concuerda con una    → 2 combinaciones ambiguas
        - No concuerda con ninguna → chunks.adj (fallback)
        """
        # No tenemos una que agrege adj sin
        # Necesitamos al menos 2 FNs construidas
        if len(chunks.fn) < 2:
            return

        fn1 = chunks.fn[0]
        fn2 = chunks.fn[1]

        for i, token in enumerate(tokens):
            if i in self.indices_usados or token.pos != "ADJ":
                continue

            concuerda_fn1 = self.validador.validar_concordancia([fn1.to_token()], token)
            concuerda_fn2 = self.validador.validar_concordancia([fn2.to_token()], token)

            if concuerda_fn1 and concuerda_fn2:
                # 4 combinaciones: adj puede modificar cualquiera de las dos FNs
                chunks.combinaciones_ambiguas = [
                    {"sujeto": f"{fn1.texto} {token.texto}", "objeto": fn2.texto},
                    {"sujeto": f"{fn2.texto} {token.texto}", "objeto": fn1.texto},
                    {"sujeto": fn1.texto, "objeto": f"{fn2.texto} {token.texto}"},
                    {"sujeto": fn2.texto, "objeto": f"{fn1.texto} {token.texto}"},
                ]

            elif concuerda_fn1:
                # 2 combinaciones: adj solo modifica fn1
                chunks.combinaciones_ambiguas = [
                    {"sujeto": f"{fn1.texto} {token.texto}", "objeto": fn2.texto},
                    {"sujeto": fn2.texto, "objeto": f"{fn1.texto} {token.texto}"},
                ]

            elif concuerda_fn2:
                # 2 combinaciones: adj solo modifica fn2
                chunks.combinaciones_ambiguas = [
                    {"sujeto": fn1.texto, "objeto": f"{fn2.texto} {token.texto}"},
                    {"sujeto": f"{fn2.texto} {token.texto}", "objeto": fn1.texto},
                ]

            else:
                chunks.adj.append(token.texto)

            self.indices_usados.add(i)

    def _adj_un_det(self, chunks: Chunks, tokens: List[Token]) -> None:
        """
        Cuando hay 1 DET, busca ADJs y decide dónde colocarlos:
        - Si hay más de 1 actante (NOUN + PROPN/PRON) → adj se adjunta al NOUN que concuerde
        - Si solo hay 1 actante → adj es predicativo, queda suelto en chunks.adj
        """
        if len(chunks.fn) < 1:
            return

        hay_mas_de_un_actante = len(chunks.fn) > 1

        for i, token in enumerate(tokens):
            if i in self.indices_usados or token.pos != "ADJ":
                continue

            fn_objetivo = None
            if hay_mas_de_un_actante:
                for fn in chunks.fn:
                    if fn.es_propio:
                        continue
                    if self.validador.validar_concordancia([fn.to_token()], token):
                        fn_objetivo = fn
                        break

            if fn_objetivo:
                fn_objetivo.texto = f"{fn_objetivo.texto} {token.texto}"
            else:
                chunks.adj.append(token.texto)

            self.indices_usados.add(i)
