try:
    from tkinter import Button, Canvas, Frame, Label, Scrollbar, Toplevel
except ModuleNotFoundError:
    class widgetNoDisponible:
        def __init__(self, *args, **kwargs):
            raise ModuleNotFoundError(
                "Tkinter no está disponible en este entorno. Instale Tk para usar la interfaz gráfica."
            )

    Button = Canvas = Frame = Label = Scrollbar = Toplevel = widgetNoDisponible

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
        self.marcoLista = None
        self.canvasLista = None
        self.ventanaLista = None
        self.construirVentana()
        self.cargarEstadoCobertura()

    @staticmethod
    def crearServicioCobertura():
        from servidorSeguroUniversitario.servicios.servicioCobertura import servicioCobertura

        return servicioCobertura()

    def construirVentana(self):
        self.ventanaRaiz.title("Seguro Universitario - Cobertura médica")
        self.ventanaRaiz.configure(bg=COLOR_FONDO)
        self.ventanaRaiz.minsize(860, 620)
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

        marcoLista = Frame(marcoPrincipal, bg=COLOR_FONDO)
        marcoLista.grid(row=3, column=0, sticky="nsew", pady=(8, 0))
        marcoLista.columnconfigure(0, weight=1)
        marcoLista.rowconfigure(0, weight=1)
        marcoPrincipal.rowconfigure(3, weight=1)

        self.canvasLista = Canvas(
            marcoLista,
            bg=COLOR_FONDO,
            bd=0,
            highlightthickness=0,
        )
        self.canvasLista.grid(row=0, column=0, sticky="nsew")

        barraDesplazamiento = Scrollbar(
            marcoLista,
            orient="vertical",
            command=self.canvasLista.yview,
            troughcolor=COLOR_FONDO,
            bg=COLOR_ACENTO,
            activebackground=COLOR_SECUNDARIO,
        )
        barraDesplazamiento.grid(row=0, column=1, sticky="ns", padx=(8, 0))
        self.canvasLista.configure(yscrollcommand=barraDesplazamiento.set)

        self.marcoLista = Frame(self.canvasLista, bg=COLOR_FONDO)
        self.ventanaLista = self.canvasLista.create_window(
            (0, 0), window=self.marcoLista, anchor="nw"
        )
        self.marcoLista.bind(
            "<Configure>",
            lambda evento: self.canvasLista.configure(
                scrollregion=self.canvasLista.bbox("all")
            ),
        )
        self.canvasLista.bind(
            "<Configure>",
            lambda evento: self.canvasLista.itemconfigure(
                self.ventanaLista, width=evento.width
            ),
        )

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
        self.etiquetaEstado.grid(row=4, column=0, sticky="ew", pady=(8, 16))

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
        ).grid(row=5, column=0, sticky="w", pady=(8, 0))

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
            self.mostrarServicios(servicios)
        else:
            self.etiquetaResumen.configure(text="No fue posible consultar la cobertura.", fg=COLOR_ERROR)
            self.etiquetaEstado.configure(text=resultado.get("mensaje", "Error al consultar la cobertura."), fg=COLOR_ERROR)
            self.mostrarServicios([])

    def mostrarServicios(self, servicios):
        for widget in self.marcoLista.winfo_children():
            widget.destroy()

        self.marcoLista.columnconfigure(0, weight=1)
        if not servicios:
            Label(
                self.marcoLista,
                text="No hay servicios médicos disponibles.",
                bg=COLOR_FONDO,
                fg=COLOR_SECUNDARIO,
                font=("Segoe UI", 11),
                anchor="w",
            ).grid(row=0, column=0, sticky="ew", padx=8, pady=8)
            return

        for indice, servicio in enumerate(servicios):
            self.construirTarjetaServicio(indice, servicio)

    def construirTarjetaServicio(self, indice, servicio):
        cubierto = servicio.get("cubierto") is True
        colorEstado = COLOR_PRINCIPAL if cubierto else COLOR_ERROR
        tarjeta = Frame(
            self.marcoLista,
            bg=COLOR_FONDO,
            bd=0,
            highlightbackground=COLOR_ACENTO,
            highlightcolor=COLOR_ACENTO,
            highlightthickness=1,
            padx=16,
            pady=12,
        )
        tarjeta.grid(row=indice, column=0, sticky="ew", padx=4, pady=4)
        tarjeta.columnconfigure(0, weight=1)

        Label(
            tarjeta,
            text=servicio.get("nombreServicio", "Servicio médico"),
            bg=COLOR_FONDO,
            fg=COLOR_PRINCIPAL,
            font=("Cambria", 16),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew")

        Label(
            tarjeta,
            text=servicio.get("categoria", "Sin categoría"),
            bg=COLOR_FONDO,
            fg=COLOR_SECUNDARIO,
            font=("Segoe UI Semibold", 11),
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", pady=(4, 0))

        Label(
            tarjeta,
            text=servicio.get("descripcion", "Sin descripción disponible."),
            bg=COLOR_FONDO,
            fg=COLOR_PRINCIPAL,
            font=("Segoe UI", 11),
            justify="left",
            anchor="w",
            wraplength=680,
        ).grid(row=2, column=0, sticky="ew", pady=(8, 0))

        Label(
            tarjeta,
            text=servicio.get("estadoCobertura", "No especificado"),
            bg=COLOR_FONDO,
            fg=colorEstado,
            font=("Segoe UI Semibold", 9),
            anchor="w",
        ).grid(row=3, column=0, sticky="w", pady=(8, 0))

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