from typing import List, Optional

from core.modelos.token_datos import Token

"""
Servicio de Validación de Concordancia.
Verifica la concordancia gramatical entre tokens.

- Solo valida concordancia
- Fácil extender reglas sin modificar código base
"""


class ValidarConcordancia:
    """
    Verifica que los tokens concuerden en género y número.
    """

    def validar_concordancia(
        self,
        chunk_actual: List[Token],
        nuevo_token: Token,
        permitir_plural: bool = False,
    ) -> bool:
        """
        Verifica si un nuevo token concuerda con un chunk actual.
            chunk_actual: Lista de tokens del chunk
            nuevo_token: Token a validar
            permitir_plural: Si True, acepta que un NOUN con num=Sing
                             que termina en -s también concuerde con Plur
        """
        genero_ref = None
        numero_ref = None

        # PASO 1: Buscar NOUN completo como referencia (tiene gen y num)
        for token in chunk_actual:
            if token.pos == "NOUN" and token.tiene_gen() and token.tiene_num():
                genero_ref = token.gen
                numero_ref = token.num
                break

        # PASO 2: Si no hay NOUN completo, buscar DET como referencia
        if not genero_ref and not numero_ref:
            for token in chunk_actual:
                if token.pos == "DET" and token.tiene_num():
                    genero_ref = token.gen
                    numero_ref = token.num
                    break

        # PASO 3: Validar que haya referencia
        if not genero_ref and not numero_ref:
            return False

        return self._concordancia_parcial(
            genero_ref, numero_ref, nuevo_token, permitir_plural
        )

    def _concordancia_parcial(
        self,
        genero_ref: Optional[str],
        numero_ref: Optional[str],
        nuevo_token: Token,
        permitir_plural: bool = False,
    ) -> bool:
        """
        Valida concordancia según lo que tenga el nuevo token.

        Prioridad:
            gen + num → valida ambos estrictamente
            solo gen  → valida solo género
            solo num  → valida solo número
            ninguno   → infiere número por terminación -s, acepta género
        """
        tiene_gen = nuevo_token.tiene_gen()
        tiene_num = nuevo_token.tiene_num()

        # CASO 1: tiene gen y num → validación estricta
        # Género solo se valida si la referencia también tiene género
        # Si permitir_plural=True y termina en -s, también acepta Plur
        if tiene_gen and tiene_num:
            num_valido = nuevo_token.num == numero_ref
            if not num_valido and permitir_plural:
                num_valido = (
                    numero_ref == "Plur" and nuevo_token.texto.lower().endswith("s")
                )
            gen_valido = nuevo_token.gen == genero_ref if genero_ref else True
            return num_valido and gen_valido

        # CASO 2: solo tiene gen → validar solo género
        if tiene_gen and not tiene_num:
            if genero_ref:
                return nuevo_token.gen == genero_ref
            return True

        # CASO 3: solo tiene num → validar solo número
        if not tiene_gen and tiene_num:
            if numero_ref:
                return nuevo_token.num == numero_ref
            return True

        # CASO 4: None/None → inferir número por terminación -s
        if numero_ref:
            termina_en_s = nuevo_token.texto.lower().endswith("s")
            if termina_en_s:
                return numero_ref == "Plur"
            else:
                return numero_ref == "Sing"

        return True

    def validar_concordancia_dict(
        self, chunk_actual: List[dict], nuevo_token: dict
    ) -> bool:
        """
        Versión compatible con diccionarios.
        """
        tokens_chunk = [Token.para_diccionario(t) for t in chunk_actual]
        token_nuevo = Token.para_diccionario(nuevo_token)

        return self.validar_concordancia(tokens_chunk, token_nuevo)
