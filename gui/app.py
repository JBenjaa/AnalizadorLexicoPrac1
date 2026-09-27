import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import subprocess
import sys

# ==========================================================
# CONFIGURACIÓN DE RUTAS
# ==========================================================

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

LEXER_PATH = BASE_DIR / "lexer" / "lexer.exe"
# ==========================================================
# VENTANA PRINCIPAL
# ==========================================================

ventana = tk.Tk()

ventana.title("Analizador Léxico - MiniLang")
ventana.geometry("1150x800")
ventana.minsize(900, 600)


# ==========================================================
# CONFIGURACIÓN DE ESTILOS
# ==========================================================

estilo = ttk.Style()

estilo.configure(
    "Treeview",
    font=("Consolas", 10),
    rowheight=28
)

estilo.configure(
    "Treeview.Heading",
    font=("Arial", 10, "bold")
)

estilo.configure(
    "TButton",
    font=("Arial", 10)
)


# ==========================================================
# CONTENEDOR PRINCIPAL CON SCROLL
# ==========================================================

# Canvas que contendrá toda la aplicación
canvas = tk.Canvas(
    ventana,
    highlightthickness=0
)

canvas.pack(
    side="left",
    fill="both",
    expand=True
)


# Scrollbar GENERAL de toda la aplicación
scroll_general = ttk.Scrollbar(
    ventana,
    orient="vertical",
    command=canvas.yview
)

scroll_general.pack(
    side="right",
    fill="y"
)


# Frame que estará dentro del Canvas
contenido = tk.Frame(
    canvas
)

ventana_canvas = canvas.create_window(
    (0, 0),
    window=contenido,
    anchor="nw"
)


# ==========================================================
# CONFIGURAR SCROLL GENERAL
# ==========================================================

def actualizar_scroll(event=None):

    canvas.configure(
        scrollregion=canvas.bbox("all")
    )


contenido.bind(
    "<Configure>",
    actualizar_scroll
)


# Hacer que el contenido ocupe todo el ancho disponible
def ajustar_ancho(event):

    canvas.itemconfig(
        ventana_canvas,
        width=event.width
    )


canvas.bind(
    "<Configure>",
    ajustar_ancho
)


# Scroll con la rueda del mouse
def scroll_mouse(event):

    canvas.yview_scroll(
        int(-1 * (event.delta / 120)),
        "units"
    )


canvas.bind_all(
    "<MouseWheel>",
    scroll_mouse
)


# ==========================================================
# TÍTULO
# ==========================================================

titulo = tk.Label(
    contenido,
    text="ANALIZADOR LÉXICO - MINILANG",
    font=("Arial", 22, "bold")
)

titulo.pack(
    pady=(20, 5)
)


subtitulo = tk.Label(
    contenido,
    text="Analizador léxico desarrollado con FLEX + Python",
    font=("Arial", 11)
)

subtitulo.pack(
    pady=(0, 20)
)


# ==========================================================
# FUNCIÓN PARA ACTUALIZAR NÚMEROS DE LÍNEA
# ==========================================================

def actualizar_lineas(event=None):

    lineas_texto = editor.get(
        "1.0",
        tk.END
    )

    cantidad_lineas = lineas_texto.count("\n")

    numeros = "\n".join(
        str(numero)
        for numero in range(
            1,
            cantidad_lineas + 1
        )
    )

    numeros_linea.config(
        state="normal"
    )

    numeros_linea.delete(
        "1.0",
        tk.END
    )

    numeros_linea.insert(
        "1.0",
        numeros
    )

    numeros_linea.config(
        state="disabled"
    )


# ==========================================================
# FUNCIÓN PARA ANALIZAR EL CÓDIGO
# ==========================================================

def analizar_codigo():

    # Obtener código del editor
    codigo = editor.get(
        "1.0",
        tk.END
    ).strip()


    # Verificar código vacío
    if not codigo:

        messagebox.showwarning(
            "Advertencia",
            "Debe ingresar código para analizar."
        )

        return


    # Verificar que exista lexer.exe
    if not LEXER_PATH.exists():

        messagebox.showerror(
            "Error",
            f"No se encontró el analizador léxico:\n\n{LEXER_PATH}"
        )

        return


    try:

        # ==================================================
        # EJECUTAR FLEX
        # ==================================================

        resultado = subprocess.run(
            [str(LEXER_PATH)],
            input=codigo,
            text=True,
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )


        # ==================================================
        # LIMPIAR RESULTADOS ANTERIORES
        # ==================================================

        for item in tabla.get_children():

            tabla.delete(item)


        # ==================================================
        # CONTADORES
        # ==================================================

        tokens = 0
        errores = 0


        # ==================================================
        # PROCESAR RESULTADO DE FLEX
        # ==================================================

        lineas_resultado = resultado.stdout.splitlines()


        for linea in lineas_resultado:

            partes = linea.split("|")


            if len(partes) == 3:

                tipo = partes[0]
                lexema = partes[1]
                numero_linea = partes[2]


                # Insertar resultado en la tabla
                if tipo == "ERROR":

                    tabla.insert(
                        "",
                        tk.END,
                        values=(
                            tipo,
                            lexema,
                            numero_linea
                        ),
                        tags=("error",)
                    )

                    errores += 1

                else:

                    tabla.insert(
                        "",
                        tk.END,
                        values=(
                            tipo,
                            lexema,
                            numero_linea
                        )
                    )

                    tokens += 1


        # ==================================================
        # ACTUALIZAR CONTADORES
        # ==================================================

        contador_tokens.config(
            text=f"Tokens: {tokens}"
        )

        contador_errores.config(
            text=f"Errores: {errores}"
        )


        # ==================================================
        # ACTUALIZAR ESTADO
        # ==================================================

        if errores > 0:

            estado.config(
                text="⚠ Análisis terminado con errores léxicos."
            )

        else:

            estado.config(
                text="✓ Análisis terminado correctamente."
            )


        # Actualizar área de scroll
        contenido.update_idletasks()

        canvas.configure(
            scrollregion=canvas.bbox("all")
        )


    except Exception as e:

        messagebox.showerror(
            "Error",
            f"Ocurrió un problema al ejecutar el analizador:\n\n{e}"
        )


# ==========================================================
# FUNCIÓN LIMPIAR
# ==========================================================

def limpiar():

    editor.delete(
        "1.0",
        tk.END
    )


    for item in tabla.get_children():

        tabla.delete(item)


    contador_tokens.config(
        text="Tokens: 0"
    )


    contador_errores.config(
        text="Errores: 0"
    )


    estado.config(
        text="Esperando código..."
    )


    actualizar_lineas()


# ==========================================================
# FUNCIÓN CARGAR ARCHIVO
# ==========================================================

def cargar_archivo():

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

        with open(
            archivo,
            "r",
            encoding="utf-8"
        ) as f:

            contenido_archivo = f.read()


        editor.delete(
            "1.0",
            tk.END
        )


        editor.insert(
            "1.0",
            contenido_archivo
        )


        actualizar_lineas()


        estado.config(
            text=f"Archivo cargado: {Path(archivo).name}"
        )


    except Exception as e:

        messagebox.showerror(
            "Error",
            f"No se pudo abrir el archivo:\n\n{e}"
        )


# ==========================================================
# SECCIÓN CÓDIGO FUENTE
# ==========================================================

frame_codigo = tk.LabelFrame(
    contenido,
    text=" Código fuente ",
    font=("Arial", 11, "bold"),
    padx=10,
    pady=10
)

frame_codigo.pack(
    fill="x",
    padx=20,
    pady=10
)


# ==========================================================
# EDITOR
# ==========================================================

frame_editor = tk.Frame(
    frame_codigo
)

frame_editor.pack(
    fill="x"
)


# ==========================================================
# NÚMEROS DE LÍNEA
# ==========================================================

numeros_linea = tk.Text(
    frame_editor,
    width=5,
    height=12,
    padx=5,
    pady=5,
    font=("Consolas", 11),
    bg="#eeeeee",
    fg="#555555",
    state="disabled",
    takefocus=0
)

numeros_linea.pack(
    side="left",
    fill="y"
)


# ==========================================================
# EDITOR DE CÓDIGO
# ==========================================================

editor = tk.Text(
    frame_editor,
    height=12,
    font=("Consolas", 11),
    wrap="none",
    undo=True
)

editor.pack(
    side="left",
    fill="both",
    expand=True
)


# ==========================================================
# SCROLLBAR DEL EDITOR
# ==========================================================

scroll_editor = ttk.Scrollbar(
    frame_editor,
    orient="vertical",
    command=editor.yview
)

scroll_editor.pack(
    side="right",
    fill="y"
)


editor.configure(
    yscrollcommand=scroll_editor.set
)


# ==========================================================
# CÓDIGO DE EJEMPLO
# ==========================================================

codigo_ejemplo = """int edad = 23;
float precio = 150.50;

if (edad >= 18) {
    print("Mayor de edad");
}
"""


editor.insert(
    "1.0",
    codigo_ejemplo
)


actualizar_lineas()


editor.bind(
    "<KeyRelease>",
    actualizar_lineas
)


# ==========================================================
# BOTONES
# ==========================================================

frame_botones = tk.Frame(
    contenido
)

frame_botones.pack(
    pady=10
)


boton_analizar = ttk.Button(
    frame_botones,
    text="Analizar",
    command=analizar_codigo
)

boton_analizar.pack(
    side="left",
    padx=5
)


boton_cargar = ttk.Button(
    frame_botones,
    text="Cargar archivo",
    command=cargar_archivo
)

boton_cargar.pack(
    side="left",
    padx=5
)


boton_limpiar = ttk.Button(
    frame_botones,
    text="Limpiar",
    command=limpiar
)

boton_limpiar.pack(
    side="left",
    padx=5
)


# ==========================================================
# SECCIÓN DE RESULTADOS
# ==========================================================

frame_resultados = tk.LabelFrame(
    contenido,
    text=" Tokens reconocidos ",
    font=("Arial", 11, "bold"),
    padx=10,
    pady=10
)

frame_resultados.pack(
    fill="x",
    padx=20,
    pady=10
)


# ==========================================================
# TABLA
# ==========================================================

frame_tabla = tk.Frame(
    frame_resultados
)

frame_tabla.pack(
    fill="x"
)


columnas = (
    "token",
    "lexema",
    "linea"
)


tabla = ttk.Treeview(
    frame_tabla,
    columns=columnas,
    show="headings",
    height=15
)


tabla.heading(
    "token",
    text="TOKEN"
)

tabla.heading(
    "lexema",
    text="LEXEMA"
)

tabla.heading(
    "linea",
    text="LÍNEA"
)


tabla.column(
    "token",
    width=220,
    anchor="center"
)

tabla.column(
    "lexema",
    width=550,
    anchor="center"
)

tabla.column(
    "linea",
    width=100,
    anchor="center"
)


tabla.pack(
    side="left",
    fill="both",
    expand=True
)


# ==========================================================
# SCROLLBAR DE LA TABLA
# ==========================================================

scroll_tabla = ttk.Scrollbar(
    frame_tabla,
    orient="vertical",
    command=tabla.yview
)

scroll_tabla.pack(
    side="right",
    fill="y"
)


tabla.configure(
    yscrollcommand=scroll_tabla.set
)


# ==========================================================
# ESTILO PARA ERRORES
# ==========================================================

tabla.tag_configure(
    "error",
    background="#ffcccc"
)


# ==========================================================
# ESTADÍSTICAS
# ==========================================================

frame_estadisticas = tk.Frame(
    contenido
)

frame_estadisticas.pack(
    fill="x",
    padx=20,
    pady=5
)


contador_tokens = tk.Label(
    frame_estadisticas,
    text="Tokens: 0",
    font=("Arial", 10, "bold")
)

contador_tokens.pack(
    side="left"
)


contador_errores = tk.Label(
    frame_estadisticas,
    text="Errores: 0",
    font=("Arial", 10, "bold")
)

contador_errores.pack(
    side="left",
    padx=30
)


# ==========================================================
# ESTADO
# ==========================================================

estado = tk.Label(
    contenido,
    text="Esperando código...",
    anchor="w",
    font=("Arial", 10)
)

estado.pack(
    fill="x",
    padx=20,
    pady=10
)


# ==========================================================
# INICIAR APLICACIÓN
# ==========================================================

ventana.mainloop()