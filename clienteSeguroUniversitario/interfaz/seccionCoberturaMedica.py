try:
    from tkinter import Button, Frame, Label, Toplevel
except ModuleNotFoundError:
    class widgetNoDisponible:
        def __init__(self, *args, **kwargs):
            raise ModuleNotFoundError(
                "Tkinter no está disponible en este entorno. Instale Tk para usar la interfaz gráfica."
            )

    Button = Frame = Label = Toplevel = widgetNoDisponible

COLOR_FONDO = "#F7F3E9"
COLOR_PRINCIPAL = "#2C3B2E"
COLOR_SECUNDARIO = "#6B7C6E"
COLOR_ACENTO = "#A9BBA0"
COLOR_ERROR = "#B3541E"


class seccionCoberturaMedica:

    def __init__(self, ventanaRaiz, fabricaServicio=None):
        self.ventanaRaiz = ventanaRaiz
        self.fabricaServicio = fabricaServicio or self.crearServicioCobertura
        self.servicio = None
        self.etiquetaEstado = None
        self.etiquetaResumen = None
        self.construirVentana()
        self.cargarEstadoCobertura()

    @staticmethod
    def crearServicioCobertura():
        from servidorSeguroUniversitario.servicios.servicioCobertura import servicioCobertura

        return servicioCobertura()

    def construirVentana(self):
        self.ventanaRaiz.title("Seguro Universitario - Cobertura médica")
        self.ventanaRaiz.configure(bg=COLOR_FONDO)
        self.ventanaRaiz.minsize(760, 420)
        self.ventanaRaiz.columnconfigure(0, weight=1)
        self.ventanaRaiz.rowconfigure(1, weight=1)

        marcoEncabezado = Frame(self.ventanaRaiz, bg=COLOR_PRINCIPAL)
        marcoEncabezado.grid(row=0, column=0, sticky="ew")

        Label(
            marcoEncabezado,
            text="Seguro Universitario",
            bg=COLOR_PRINCIPAL,
            fg=COLOR_FONDO,
            font=("Cambria", 20),
            padx=24,
            pady=16,
        ).grid(row=0, column=0, sticky="w")

        marcoPrincipal = Frame(
            self.ventanaRaiz,
            bg=COLOR_FONDO,
            bd=0,
            relief="solid",
            highlightbackground=COLOR_ACENTO,
            highlightcolor=COLOR_ACENTO,
            highlightthickness=1,
            padx=24,
            pady=24,
        )
        marcoPrincipal.grid(row=1, column=0, sticky="nsew", padx=24, pady=24)
        marcoPrincipal.columnconfigure(0, weight=1)

        Label(
            marcoPrincipal,
            text="Cobertura médica",
            bg=COLOR_FONDO,
            fg=COLOR_PRINCIPAL,
            font=("Cambria", 20),
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        Label(
            marcoPrincipal,
            text="Consulta el estado general de la cobertura médica disponible.",
            bg=COLOR_FONDO,
            fg=COLOR_SECUNDARIO,
            font=("Segoe UI", 11),
        ).grid(row=1, column=0, sticky="w", pady=(0, 24))

        self.etiquetaResumen = Label(
            marcoPrincipal,
            text="Consultando cobertura...",
            bg=COLOR_FONDO,
            fg=COLOR_PRINCIPAL,
            font=("Segoe UI Semibold", 11),
            anchor="w",
        )
        self.etiquetaResumen.grid(row=2, column=0, sticky="ew", pady=8)

        self.etiquetaEstado = Label(
            marcoPrincipal,
            text="",
            bg=COLOR_FONDO,
            fg=COLOR_SECUNDARIO,
            font=("Segoe UI", 9),
            justify="left",
            anchor="w",
            wraplength=680,
        )
        self.etiquetaEstado.grid(row=3, column=0, sticky="ew", pady=(8, 16))

        Button(
            marcoPrincipal,
            text="Actualizar cobertura",
            command=self.cargarEstadoCobertura,
            bg=COLOR_PRINCIPAL,
            fg=COLOR_FONDO,
            activebackground=COLOR_SECUNDARIO,
            activeforeground=COLOR_FONDO,
            font=("Segoe UI Semibold", 11),
            bd=0,
            relief="solid",
            highlightbackground=COLOR_ACENTO,
            highlightcolor=COLOR_ACENTO,
            highlightthickness=1,
            padx=16,
            pady=8,
            cursor="hand2",
        ).grid(row=4, column=0, sticky="w", pady=(8, 0))

    def obtenerServicioCobertura(self):
        if self.servicio is None:
            self.servicio = self.fabricaServicio()
        return self.servicio

    def cargarEstadoCobertura(self):
        try:
            resultado = self.obtenerServicioCobertura().listarServiciosMedicos()
        except Exception as error:
            resultado = {
                "exito": False,
                "mensaje": f"Ocurrió un error inesperado al consultar la cobertura: {error}",
                "servicios": [],
            }

        servicios = resultado.get("servicios", [])
        if resultado.get("exito"):
            self.etiquetaResumen.configure(
                text=self.construirResumenCobertura(resultado),
                fg=COLOR_PRINCIPAL,
            )
            self.etiquetaEstado.configure(
                text=resultado.get("mensaje", "Cobertura consultada correctamente."),
                fg=COLOR_SECUNDARIO,
            )
        else:
            self.etiquetaResumen.configure(text="No fue posible consultar la cobertura.", fg=COLOR_ERROR)
            self.etiquetaEstado.configure(text=resultado.get("mensaje", "Error al consultar la cobertura."), fg=COLOR_ERROR)

    def construirResumenCobertura(self, resultado):
        servicios = resultado.get("servicios", [])
        cubiertos = sum(1 for servicio in servicios if servicio.get("cubierto") is True)
        return f"{cubiertos} de {len(servicios)} servicios médicos cuentan con cobertura."


def abrirVentanaCobertura(ventanaPadre, fabricaServicio=None):
    ventanaCobertura = Toplevel(ventanaPadre)
    seccionCoberturaMedica(ventanaCobertura, fabricaServicio=fabricaServicio)
    ventanaCobertura.transient(ventanaPadre)
    ventanaCobertura.grab_set()
    return ventanaCobertura