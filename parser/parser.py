import sys


class ParserError(Exception):
    """Error producido durante el análisis sintáctico."""
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0

    # ==========================================================
    # UTILIDADES
    # ==========================================================

    def token_actual(self):
        if self.posicion < len(self.tokens):
            return self.tokens[self.posicion]
        return None

    def avanzar(self):
        token = self.token_actual()

        if token is not None:
            self.posicion += 1

        return token

    def error(self, mensaje):
        token = self.token_actual()

        if token:
            tipo, lexema, linea = token
            raise ParserError(
                f"Error sintáctico en línea {linea}: {mensaje}. "
                f"Se encontró '{lexema}' ({tipo})."
            )

        raise ParserError(
            f"Error sintáctico: {mensaje}. Se encontró el final del código."
        )

    def esperar(self, tipo, mensaje=None):
        token = self.token_actual()

        if token is None:
            self.error(
                mensaje or f"Se esperaba '{tipo}' pero terminó el código"
            )

        if token[0] != tipo:
            self.error(
                mensaje or f"Se esperaba '{tipo}'"
            )

        return self.avanzar()

    def es(self, tipo, lexema=None):
        token = self.token_actual()

        if token is None:
            return False

        if token[0] != tipo:
            return False

        if lexema is not None and token[1] != lexema:
            return False

        return True

    # ==========================================================
    # PROGRAMA
    # ==========================================================

    def analizar(self):
        """
        programa → sentencia*
        """

        while self.token_actual() is not None:
            self.sentencia()

        return True

    # ==========================================================
    # SENTENCIAS
    # ==========================================================

    def sentencia(self):

        if self.es("KEYWORD", "int"):
            return self.declaracion()

        if self.es("KEYWORD", "float"):
            return self.declaracion()

        if self.es("KEYWORD", "string"):
            return self.declaracion()

        if self.es("KEYWORD", "bool"):
            return self.declaracion()

        if self.es("IDENTIFIER"):
            return self.asignacion()

        if self.es("KEYWORD", "if"):
            return self.sentencia_if()

        if self.es("KEYWORD", "while"):
            return self.sentencia_while()

        if self.es("KEYWORD", "print"):
            return self.sentencia_print()

        self.error("sentencia no válida")

    # ==========================================================
    # DECLARACIONES
    # ==========================================================

    def declaracion(self):
        """
        declaración → tipo IDENTIFIER ASSIGN expresión SEMICOLON
        """

        self.avanzar()  # int, float, string o bool

        self.esperar(
            "IDENTIFIER",
            "se esperaba un identificador después del tipo"
        )

        self.esperar(
            "ASSIGN",
            "se esperaba '=' después del identificador"
        )

        self.expresion()

        self.esperar(
            "SEMICOLON",
            "se esperaba ';' al final de la declaración"
        )

    # ==========================================================
    # ASIGNACIONES
    # ==========================================================

    def asignacion(self):
        """
        asignación → IDENTIFIER ASSIGN expresión SEMICOLON
        """

        self.esperar("IDENTIFIER")

        self.esperar(
            "ASSIGN",
            "se esperaba '=' después del identificador"
        )

        self.expresion()

        self.esperar(
            "SEMICOLON",
            "se esperaba ';' al final de la asignación"
        )

    # ==========================================================
    # IF
    # ==========================================================

    def sentencia_if(self):
        """
        if → if LPAREN condición RPAREN bloque [else bloque]
        """

        self.esperar("KEYWORD",)

        self.esperar(
            "LPAREN",
            "se esperaba '(' después de 'if'"
        )

        self.condicion()

        self.esperar(
            "RPAREN",
            "se esperaba ')' después de la condición"
        )

        self.bloque()

        if self.es("KEYWORD", "else"):
            self.avanzar()
            self.bloque()

    # ==========================================================
    # WHILE
    # ==========================================================

    def sentencia_while(self):
        """
        while → while LPAREN condición RPAREN bloque
        """

        self.esperar("KEYWORD")

        self.esperar(
            "LPAREN",
            "se esperaba '(' después de 'while'"
        )

        self.condicion()

        self.esperar(
            "RPAREN",
            "se esperaba ')' después de la condición"
        )

        self.bloque()

    # ==========================================================
    # BLOQUES
    # ==========================================================

    def bloque(self):
        """
        bloque → LBRACE sentencia* RBRACE
        """

        self.esperar(
            "LBRACE",
            "se esperaba '{' para iniciar el bloque"
        )

        while self.token_actual() is not None and not self.es("RBRACE"):
            self.sentencia()

        self.esperar(
            "RBRACE",
            "se esperaba '}' para cerrar el bloque"
        )

    # ==========================================================
    # PRINT
    # ==========================================================

    def sentencia_print(self):
        """
        print → print LPAREN expresión RPAREN SEMICOLON
        """

        self.esperar("KEYWORD")

        self.esperar(
            "LPAREN",
            "se esperaba '(' después de 'print'"
        )

        self.expresion()

        self.esperar(
            "RPAREN",
            "se esperaba ')' después de la expresión"
        )

        self.esperar(
            "SEMICOLON",
            "se esperaba ';' después de print"
        )

    # ==========================================================
    # CONDICIONES
    # ==========================================================

    def condicion(self):
        """
        condición → expresión operador_comparación expresión
        """

        self.expresion()

        if self.es("EQUAL"):
            self.avanzar()

        elif self.es("NOT_EQUAL"):
            self.avanzar()

        elif self.es("GREATER"):
            self.avanzar()

        elif self.es("LESS"):
            self.avanzar()

        elif self.es("GREATER_EQUAL"):
            self.avanzar()

        elif self.es("LESS_EQUAL"):
            self.avanzar()

        else:
            self.error(
                "se esperaba un operador de comparación"
            )

        self.expresion()

    # ==========================================================
    # EXPRESIONES
    # ==========================================================

    def expresion(self):
        """
        expresión → término ((PLUS | MINUS) término)*
        """

        self.termino()

        while self.es("PLUS") or self.es("MINUS"):
            self.avanzar()
            self.termino()

    def termino(self):
        """
        término → factor ((MULTIPLY | DIVIDE) factor)*
        """

        self.factor()

        while self.es("MULTIPLY") or self.es("DIVIDE"):
            self.avanzar()
            self.factor()

    def factor(self):
        """
        factor →
            IDENTIFIER
            INTEGER
            FLOAT
            STRING
            BOOLEAN
            LPAREN expresión RPAREN
        """

        if self.es("IDENTIFIER"):
            self.avanzar()
            return

        if self.es("INTEGER"):
            self.avanzar()
            return

        if self.es("FLOAT"):
            self.avanzar()
            return

        if self.es("STRING"):
            self.avanzar()
            return

        if self.es("BOOLEAN"):
            self.avanzar()
            return

        if self.es("LPAREN"):
            self.avanzar()

            self.expresion()

            self.esperar(
                "RPAREN",
                "se esperaba ')' después de la expresión"
            )

            return

        self.error("se esperaba una expresión válida")


# ==========================================================
# LEER TOKENS DESDE STDIN
# ==========================================================

def leer_tokens():
    tokens = []

    for linea in sys.stdin:
        linea = linea.strip()

        if not linea:
            continue

        partes = linea.split("|")

        if len(partes) != 3:
            continue

        tipo = partes[0]
        lexema = partes[1]
        numero_linea = partes[2]

        if tipo == "ERROR":
            raise ParserError(
                f"Error léxico en línea {numero_linea}: "
                f"carácter no reconocido '{lexema}'."
            )

        tokens.append(
            (tipo, lexema, numero_linea)
        )

    return tokens


# ==========================================================
# PROGRAMA PRINCIPAL
# ==========================================================

if __name__ == "__main__":

    try:
        tokens = leer_tokens()

        parser = Parser(tokens)

        parser.analizar()

        print("SINTAXIS_OK")

    except ParserError as error:
        print(f"SINTAXIS_ERROR|{error}")