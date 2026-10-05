import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import subprocess
import sys


# ============================================================
# RUTAS DEL PROYECTO
# ============================================================

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

LEXER_PATH = BASE_DIR / "lexer" / "lexer.exe"
PARSER_PATH = BASE_DIR / "parser" / "parser.py"


# ============================================================
# COLORES
# ============================================================

BG = "#f4f6f8"
PANEL = "#ffffff"
PRIMARY = "#2563eb"
PRIMARY_DARK = "#1d4ed8"
TEXT = "#1f2937"
MUTED = "#6b7280"
SUCCESS = "#15803d"
ERROR = "#dc2626"
WARNING = "#d97706"


# ============================================================
# APLICACIÓN
# ============================================================

class AnalizadorApp:

    def __init__(self, root):
        self.root = root

        self.root.title("Analizador Léxico y Sintáctico")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg=BG)

        self.crear_interfaz()
        self.cargar_ejemplo()

    # ========================================================
    # INTERFAZ
    # ========================================================

    def crear_interfaz(self):

        # ----------------------------------------------------
        # CONTENEDOR PRINCIPAL CON SCROLL
        # ----------------------------------------------------

        self.canvas = tk.Canvas(
            self.root,
            bg=BG,
            highlightthickness=0
        )

        self.scrollbar = ttk.Scrollbar(
            self.root,
            orient="vertical",
            command=self.canvas.yview
        )

        self.canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.scrollbar.pack(
            side="right",
            fill="y"
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.main_frame = tk.Frame(
            self.canvas,
            bg=BG
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.main_frame,
            anchor="nw"
        )

        self.main_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.bind(
            "<Configure>",
            self.ajustar_ancho_canvas
        )

        # ----------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------

        titulo = tk.Label(
            self.main_frame,
            text="Analizador Léxico y Sintáctico",
            font=("Segoe UI", 24, "bold"),
            bg=BG,
            fg=TEXT
        )

        titulo.pack(
            pady=(25, 5)
        )

        subtitulo = tk.Label(
            self.main_frame,
            text="Análisis de código mediante FLEX + Analizador Sintáctico",
            font=("Segoe UI", 11),
            bg=BG,
            fg=MUTED
        )

        subtitulo.pack(
            pady=(0, 20)
        )

        # ----------------------------------------------------
        # EDITOR DE CÓDIGO
        # ----------------------------------------------------

        editor_frame = tk.Frame(
            self.main_frame,
            bg=PANEL,
            bd=0,
            highlightthickness=1,
            highlightbackground="#d1d5db"
        )

        editor_frame.pack(
            fill="x",
            padx=25,
            pady=5
        )

        editor_title = tk.Label(
            editor_frame,
            text="Código fuente",
            font=("Segoe UI", 13, "bold"),
            bg=PANEL,
            fg=TEXT
        )

        editor_title.pack(
            anchor="w",
            padx=15,
            pady=(12, 5)
        )

        editor_container = tk.Frame(
            editor_frame,
            bg=PANEL
        )

        editor_container.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=5
        )

        self.editor = tk.Text(
            editor_container,
            height=12,
            font=("Consolas", 11),
            bg="#111827",
            fg="#f9fafb",
            insertbackground="white",
            padx=12,
            pady=12,
            wrap="none"
        )

        self.editor_scroll = ttk.Scrollbar(
            editor_container,
            orient="vertical",
            command=self.editor.yview
        )

        self.editor.configure(
            yscrollcommand=self.editor_scroll.set
        )

        self.editor.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.editor_scroll.pack(
            side="right",
            fill="y"
        )

        # ----------------------------------------------------
        # BOTONES
        # ----------------------------------------------------

        botones = tk.Frame(
            editor_frame,
            bg=PANEL
        )

        botones.pack(
            fill="x",
            padx=15,
            pady=12
        )

        self.btn_analizar = tk.Button(
            botones,
            text="▶  Analizar código",
            command=self.analizar_codigo,
            bg=PRIMARY,
            fg="white",
            activebackground=PRIMARY_DARK,
            activeforeground="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=9
        )

        self.btn_analizar.pack(
            side="left",
            padx=(0, 8)
        )

        tk.Button(
            botones,
            text="📂  Cargar archivo",
            command=self.cargar_archivo,
            font=("Segoe UI", 10),
            relief="flat",
            bg="#e5e7eb",
            fg=TEXT,
            cursor="hand2",
            padx=15,
            pady=9
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            botones,
            text="🗑  Limpiar",
            command=self.limpiar,
            font=("Segoe UI", 10),
            relief="flat",
            bg="#e5e7eb",
            fg=TEXT,
            cursor="hand2",
            padx=15,
            pady=9
        ).pack(
            side="left",
            padx=5
        )

        # ----------------------------------------------------
        # RESULTADOS DEL ANÁLISIS
        # ----------------------------------------------------

        resultados = tk.Frame(
            self.main_frame,
            bg=BG
        )

        resultados.pack(
            fill="x",
            padx=25,
            pady=15
        )

        # ====================================================
        # ESTADO LÉXICO
        # ====================================================

        self.lexico_frame = tk.Frame(
            resultados,
            bg=PANEL,
            highlightthickness=1,
            highlightbackground="#d1d5db"
        )

        self.lexico_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 7)
        )

        tk.Label(
            self.lexico_frame,
            text="ANÁLISIS LÉXICO",
            font=("Segoe UI", 11, "bold"),
            bg=PANEL,
            fg=TEXT
        ).pack(
            pady=(15, 5)
        )

        self.lexico_status = tk.Label(
            self.lexico_frame,
            text="Pendiente",
            font=("Segoe UI", 16, "bold"),
            bg=PANEL,
            fg=MUTED
        )

        self.lexico_status.pack(
            pady=(0, 15)
        )

        # ====================================================
        # ESTADO SINTÁCTICO
        # ====================================================

        self.sintactico_frame = tk.Frame(
            resultados,
            bg=PANEL,
            highlightthickness=1,
            highlightbackground="#d1d5db"
        )

        self.sintactico_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=7
        )

        tk.Label(
            self.sintactico_frame,
            text="ANÁLISIS SINTÁCTICO",
            font=("Segoe UI", 11, "bold"),
            bg=PANEL,
            fg=TEXT
        ).pack(
            pady=(15, 5)
        )

        self.sintactico_status = tk.Label(
            self.sintactico_frame,
            text="Pendiente",
            font=("Segoe UI", 16, "bold"),
            bg=PANEL,
            fg=MUTED
        )

        self.sintactico_status.pack(
            pady=(0, 15)
        )

        # ====================================================
        # ESTADÍSTICAS
        # ====================================================

        self.stats_frame = tk.Frame(
            resultados,
            bg=PANEL,
            highlightthickness=1,
            highlightbackground="#d1d5db"
        )

        self.stats_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(7, 0)
        )

        tk.Label(
            self.stats_frame,
            text="ESTADÍSTICAS",
            font=("Segoe UI", 11, "bold"),
            bg=PANEL,
            fg=TEXT
        ).pack(
            pady=(15, 5)
        )

        self.stats_label = tk.Label(
            self.stats_frame,
            text="Tokens: 0\nErrores léxicos: 0",
            font=("Segoe UI", 11),
            bg=PANEL,
            fg=MUTED,
            justify="center"
        )

        self.stats_label.pack(
            pady=(0, 15)
        )

        # ----------------------------------------------------
        # TABLA DE TOKENS
        # ----------------------------------------------------

        tokens_frame = tk.Frame(
            self.main_frame,
            bg=PANEL,
            highlightthickness=1,
            highlightbackground="#d1d5db"
        )

        tokens_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=5
        )

        tk.Label(
            tokens_frame,
            text="Tokens reconocidos",
            font=("Segoe UI", 13, "bold"),
            bg=PANEL,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=15,
            pady=(12, 8)
        )

        tabla_container = tk.Frame(
            tokens_frame,
            bg=PANEL
        )

        tabla_container.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        columnas = (
            "numero",
            "tipo",
            "lexema",
            "linea"
        )

        self.tabla = ttk.Treeview(
            tabla_container,
            columns=columnas,
            show="headings",
            height=15
        )

        self.tabla.heading(
            "numero",
            text="#"
        )

        self.tabla.heading(
            "tipo",
            text="TIPO"
        )

        self.tabla.heading(
            "lexema",
            text="LEXEMA"
        )

        self.tabla.heading(
            "linea",
            text="LÍNEA"
        )

        self.tabla.column(
            "numero",
            width=60,
            anchor="center"
        )

        self.tabla.column(
            "tipo",
            width=180,
            anchor="center"
        )

        self.tabla.column(
            "lexema",
            width=400,
            anchor="w"
        )

        self.tabla.column(
            "linea",
            width=100,
            anchor="center"
        )

        tabla_scroll = ttk.Scrollbar(
            tabla_container,
            orient="vertical",
            command=self.tabla.yview
        )

        self.tabla.configure(
            yscrollcommand=tabla_scroll.set
        )

        self.tabla.pack(
            side="left",
            fill="both",
            expand=True
        )

        tabla_scroll.pack(
            side="right",
            fill="y"
        )

        # ----------------------------------------------------
        # DETALLES DEL ERROR
        # ----------------------------------------------------

        error_frame = tk.Frame(
            self.main_frame,
            bg=PANEL,
            highlightthickness=1,
            highlightbackground="#d1d5db"
        )

        error_frame.pack(
            fill="x",
            padx=25,
            pady=15
        )

        tk.Label(
            error_frame,
            text="Detalles del análisis",
            font=("Segoe UI", 13, "bold"),
            bg=PANEL,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=15,
            pady=(12, 5)
        )

        self.detalles = tk.Text(
            error_frame,
            height=5,
            font=("Consolas", 10),
            bg="#f9fafb",
            fg=TEXT,
            relief="flat",
            wrap="word",
            padx=12,
            pady=8
        )

        self.detalles.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        self.detalles.configure(
            state="disabled"
        )

        # ----------------------------------------------------
        # BARRA DE ESTADO
        # ----------------------------------------------------

        self.status_bar = tk.Label(
            self.main_frame,
            text="Listo para analizar",
            font=("Segoe UI", 10),
            bg="#e5e7eb",
            fg=TEXT,
            anchor="w",
            padx=15,
            pady=8
        )

        self.status_bar.pack(
            fill="x",
            padx=25,
            pady=(0, 25)
        )

        # ----------------------------------------------------
        # SCROLL CON RUEDA DEL MOUSE
        # ----------------------------------------------------

        self.canvas.bind_all(
            "<MouseWheel>",
            self.scroll_mouse
        )

    # ========================================================
    # AJUSTAR CANVAS
    # ========================================================

    def ajustar_ancho_canvas(self, event):
        self.canvas.itemconfig(
            self.canvas_window,
            width=event.width
        )

    # ========================================================
    # SCROLL
    # ========================================================

    def scroll_mouse(self, event):
        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    # ========================================================
    # CARGAR EJEMPLO
    # ========================================================

    def cargar_ejemplo(self):

        codigo = '''int edad = 23;
float precio = 150.50;
string nombre = "Jose";
bool activo = true;

if (edad >= 18) {
    print("Mayor de edad");
}'''

        self.editor.delete(
            "1.0",
            tk.END
        )

        self.editor.insert(
            "1.0",
            codigo
        )

    # ========================================================
    # CARGAR ARCHIVO
    # ========================================================

    def cargar_archivo(self):

        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[
                ("Archivos de texto", "*.txt"),
                ("Todos los archivos", "*.*")
            ]
        )

        if not archivo:
            return

        try:

            contenido = Path(
                archivo
            ).read_text(
                encoding="utf-8"
            )

            self.editor.delete(
                "1.0",
                tk.END
            )

            self.editor.insert(
                "1.0",
                contenido
            )

            self.status_bar.config(
                text=f"Archivo cargado: {Path(archivo).name}"
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"No se pudo cargar el archivo:\n\n{e}"
            )

    # ========================================================
    # LIMPIAR
    # ========================================================

    def limpiar(self):

        self.editor.delete(
            "1.0",
            tk.END
        )

        for item in self.tabla.get_children():
            self.tabla.delete(item)

        self.lexico_status.config(
            text="Pendiente",
            fg=MUTED
        )

        self.sintactico_status.config(
            text="Pendiente",
            fg=MUTED
        )

        self.stats_label.config(
            text="Tokens: 0\nErrores léxicos: 0"
        )

        self.mostrar_detalles(
            ""
        )

        self.status_bar.config(
            text="Listo para analizar"
        )

    # ========================================================
    # ANALIZAR CÓDIGO
    # ========================================================

    def analizar_codigo(self):

        codigo = self.editor.get(
            "1.0",
            tk.END
        ).strip()

        if not codigo:

            messagebox.showwarning(
                "Código vacío",
                "Escribe o carga código antes de analizar."
            )

            return

        # ----------------------------------------------------
        # VERIFICAR ARCHIVOS
        # ----------------------------------------------------

        if not LEXER_PATH.exists():

            messagebox.showerror(
                "Error",
                f"No se encontró el lexer:\n\n{LEXER_PATH}"
            )

            return

        if not PARSER_PATH.exists():

            messagebox.showerror(
                "Error",
                f"No se encontró el parser:\n\n{PARSER_PATH}"
            )

            return

        # ----------------------------------------------------
        # LIMPIAR TABLA
        # ----------------------------------------------------

        for item in self.tabla.get_children():
            self.tabla.delete(item)

        self.btn_analizar.config(
            state="disabled",
            text="Analizando..."
        )

        self.status_bar.config(
            text="Ejecutando análisis léxico..."
        )

        self.root.update_idletasks()

        try:

            # =================================================
            # 1. ANÁLISIS LÉXICO
            # =================================================

            resultado_lexico = subprocess.run(
                [str(LEXER_PATH)],
                input=codigo,
                text=True,
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            salida_lexica = resultado_lexico.stdout.strip()

            error_lexico_sistema = resultado_lexico.stderr.strip()

            tokens = []

            errores_lexicos = 0

            # -------------------------------------------------
            # PROCESAR TOKENS
            # -------------------------------------------------

            if salida_lexica:

                for linea in salida_lexica.splitlines():

                    partes = linea.split("|")

                    if len(partes) != 3:
                        continue

                    tipo = partes[0]
                    lexema = partes[1]
                    numero_linea = partes[2]

                    tokens.append(
                        (
                            tipo,
                            lexema,
                            numero_linea
                        )
                    )

                    if tipo == "ERROR":
                        errores_lexicos += 1

            # -------------------------------------------------
            # MOSTRAR TOKENS
            # -------------------------------------------------

            for i, token in enumerate(
                tokens,
                start=1
            ):

                tipo, lexema, numero_linea = token

                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        i,
                        tipo,
                        lexema,
                        numero_linea
                    )
                )

            # -------------------------------------------------
            # ESTADO LÉXICO
            # -------------------------------------------------

            if errores_lexicos == 0:

                self.lexico_status.config(
                    text="✓ Correcto",
                    fg=SUCCESS
                )

            else:

                self.lexico_status.config(
                    text=f"✗ {errores_lexicos} error(es)",
                    fg=ERROR
                )

            # -------------------------------------------------
            # ESTADÍSTICAS
            # -------------------------------------------------

            self.stats_label.config(
                text=(
                    f"Tokens: {len(tokens)}\n"
                    f"Errores léxicos: {errores_lexicos}"
                )
            )

            # =================================================
            # SI HAY ERROR LÉXICO
            # =================================================

            if errores_lexicos > 0:

                self.sintactico_status.config(
                    text="No ejecutado",
                    fg=WARNING
                )

                errores = []

                for token in tokens:

                    if token[0] == "ERROR":

                        errores.append(
                            f"Línea {token[2]}: símbolo no reconocido '{token[1]}'"
                        )

                self.mostrar_detalles(
                    "ERRORES LÉXICOS:\n\n" +
                    "\n".join(errores)
                )

                self.status_bar.config(
                    text="Análisis finalizado con errores léxicos."
                )

                return

            # =================================================
            # 2. ANÁLISIS SINTÁCTICO
            # =================================================

            self.status_bar.config(
                text="Análisis léxico correcto. Ejecutando análisis sintáctico..."
            )

            self.root.update_idletasks()

            resultado_sintactico = subprocess.run(
                [
                    sys.executable,
                    str(PARSER_PATH)
                ],
                input=salida_lexica,
                text=True,
                capture_output=True
            )

            salida_sintactica = (
                resultado_sintactico.stdout.strip()
            )

            error_sintactico_sistema = (
                resultado_sintactico.stderr.strip()
            )

            # =================================================
            # RESULTADO SINTÁCTICO
            # =================================================

            if salida_sintactica.startswith(
                "SINTAXIS_OK"
            ):

                self.sintactico_status.config(
                    text="✓ Correcto",
                    fg=SUCCESS
                )

                self.mostrar_detalles(
                    "ANÁLISIS COMPLETADO CORRECTAMENTE\n\n"
                    "✓ Análisis léxico: correcto\n"
                    "✓ Análisis sintáctico: correcto\n\n"
                    f"Se reconocieron {len(tokens)} tokens."
                )

                self.status_bar.config(
                    text="✓ Análisis completado correctamente."
                )

            else:

                self.sintactico_status.config(
                    text="✗ Error",
                    fg=ERROR
                )

                self.mostrar_detalles(
                    "ERROR SINTÁCTICO:\n\n" +
                    salida_sintactica
                )

                self.status_bar.config(
                    text="✗ Se encontraron errores sintácticos."
                )

            # =================================================
            # ERRORES INTERNOS
            # =================================================

            if error_lexico_sistema:

                self.mostrar_detalles(
                    self.obtener_detalles_actuales()
                    + "\n\nSalida del lexer:\n"
                    + error_lexico_sistema
                )

            if error_sintactico_sistema:

                self.mostrar_detalles(
                    self.obtener_detalles_actuales()
                    + "\n\nSalida del parser:\n"
                    + error_sintactico_sistema
                )

        except Exception as e:

            self.lexico_status.config(
                text="Error",
                fg=ERROR
            )

            self.sintactico_status.config(
                text="Error",
                fg=ERROR
            )

            self.mostrar_detalles(
                f"ERROR AL EJECUTAR EL ANALIZADOR:\n\n{e}"
            )

            self.status_bar.config(
                text="Error durante el análisis."
            )

            messagebox.showerror(
                "Error",
                f"Ocurrió un error durante el análisis:\n\n{e}"
            )

        finally:

            self.btn_analizar.config(
                state="normal",
                text="▶  Analizar código"
            )

    # ========================================================
    # MOSTRAR DETALLES
    # ========================================================

    def mostrar_detalles(self, texto):

        self.detalles.config(
            state="normal"
        )

        self.detalles.delete(
            "1.0",
            tk.END
        )

        self.detalles.insert(
            "1.0",
            texto
        )

        self.detalles.config(
            state="disabled"
        )

    # ========================================================
    # OBTENER DETALLES ACTUALES
    # ========================================================

    def obtener_detalles_actuales(self):

        self.detalles.config(
            state="normal"
        )

        texto = self.detalles.get(
            "1.0",
            tk.END
        ).strip()

        self.detalles.config(
            state="disabled"
        )

        return texto


# ============================================================
# INICIAR APLICACIÓN
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = AnalizadorApp(
        root
    )

    root.mainloop()