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


class detalleJustificativoMedico:

    def __init__(self, ventanaRaiz, justificativo):
        self.ventanaRaiz = ventanaRaiz
        self.justificativo = justificativo
        self.configurarVentana()
        self.construirInterfaz()

    def configurarVentana(self):
        self.ventanaRaiz.title("Seguro Universitario - Detalle del justificativo")
        self.ventanaRaiz.configure(bg=COLOR_FONDO)
        self.ventanaRaiz.minsize(620, 450)
        self.ventanaRaiz.columnconfigure(0, weight=1)

    def construirInterfaz(self):
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
        marcoPrincipal.columnconfigure(1, weight=1)

        Label(
            marcoPrincipal,
            text="Detalle del justificativo médico",
            bg=COLOR_FONDO,
            fg=COLOR_PRINCIPAL,
            font=("Cambria", 20),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 16))

        datos = self.obtenerDatosDetalle()
        for indice, (etiqueta, valor) in enumerate(datos, start=1):
            Label(
                marcoPrincipal,
                text=etiqueta,
                bg=COLOR_FONDO,
                fg=COLOR_PRINCIPAL,
                font=("Segoe UI Semibold", 11),
            ).grid(row=indice, column=0, sticky="nw", padx=(0, 24), pady=8)
            Label(
                marcoPrincipal,
                text=valor,
                bg=COLOR_FONDO,
                fg=COLOR_SECUNDARIO,
                font=("Segoe UI", 11),
                anchor="w",
                justify="left",
                wraplength=420,
            ).grid(row=indice, column=1, sticky="ew", pady=8)

        Button(
            marcoPrincipal,
            text="Cerrar",
            command=self.ventanaRaiz.destroy,
            bg=COLOR_PRINCIPAL,
            fg=COLOR_FONDO,
            activebackground=COLOR_SECUNDARIO,
            activeforeground=COLOR_FONDO,
            font=("Segoe UI Semibold", 11),
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
        ).grid(row=len(datos) + 1, column=0, columnspan=2, sticky="w", pady=(16, 0))

    def obtenerDatosDetalle(self):
        return (
            ("ID de consulta", self.justificativo.get("idConsulta", "-")),
            ("Fecha de atención", self.justificativo.get("fechaConsulta", "-")),
            ("Servicio médico", self.justificativo.get("nombreServicio", "-")),
            ("Médico tratante", self.justificativo.get("medicoTratante", "-") or "-"),
            ("Fecha de generación", self.justificativo.get("fechaGeneracion", "-") or "-"),
            ("Archivo", self.justificativo.get("nombreArchivo", "-") or "-"),
        )


def abrirVentanaDetalleJustificativo(ventanaPadre, justificativo):
    ventanaDetalle = Toplevel(ventanaPadre)
    detalleJustificativoMedico(ventanaDetalle, justificativo)
    ventanaDetalle.transient(ventanaPadre)
    ventanaDetalle.grab_set()
    return ventanaDetalle