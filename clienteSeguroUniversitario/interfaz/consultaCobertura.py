try:
    from tkinter import Frame, Label, Listbox, Scrollbar, StringVar, SINGLE
except ModuleNotFoundError:
    class StringVar:
        def __init__(self, value=""):
            self._value = value

        def get(self):
            return self._value

        def set(self, value):
            self._value = value

    class widgetNoDisponible:
        def __init__(self, *args, **kwargs):
            raise ModuleNotFoundError(
                "Tkinter no está disponible en este entorno. Instale Tk para usar la interfaz gráfica."
            )

    Frame = Label = Listbox = Scrollbar = widgetNoDisponible
    SINGLE = "single"

COLOR_FONDO = "#F7F3E9"
COLOR_PRINCIPAL = "#2C3B2E"
COLOR_SECUNDARIO = "#6B7C6E"
COLOR_ACENTO = "#A9BBA0"
COLOR_ERROR = "#B3541E"
COLOR_ADVERTENCIA = "#B38E1E"

ESTADO_CUBIERTO = "cubierto"
ESTADO_PARCIAL = "parcial"
ESTADO_NO_CUBIERTO = "no cubierto"

COLORES_POR_ESTADO = {
    ESTADO_CUBIERTO: COLOR_PRINCIPAL,
    ESTADO_PARCIAL: COLOR_ADVERTENCIA,
    ESTADO_NO_CUBIERTO: COLOR_ERROR,
}

TEXTOS_POR_ESTADO = {
    ESTADO_CUBIERTO: "Cubierto por el seguro",
    ESTADO_PARCIAL: "Cobertura parcial",
    ESTADO_NO_CUBIERTO: "No cubierto",
}


class consultaCobertura:

    def __init__(self, ventanaRaiz, fabricaServicio=None):
        self.ventanaRaiz = ventanaRaiz
        self.fabricaServicio = fabricaServicio or self.crearServicioCobertura
        self.servicio = None
        self.servicios = []

        self.estadoMensajeVar = StringVar(value="Seleccione un servicio para ver su cobertura.")
        self.estadoColorActual = COLOR_SECUNDARIO

        self.configurarVentana()
        self.construirInterfaz()
        self.cargarServicios()

    @staticmethod
    def crearServicioCobertura():
        from servidorSeguroUniversitario.servicios.servicioCobertura import servicioCobertura

        return servicioCobertura()

    def configurarVentana(self):
        self.ventanaRaiz.title("Seguro Universitario - Cobertura médica")
        self.ventanaRaiz.configure(bg=COLOR_FONDO)
        self.ventanaRaiz.minsize(700, 500)
        self.ventanaRaiz.columnconfigure(0, weight=1)
        self.ventanaRaiz.rowconfigure(0, weight=1)

    def construirInterfaz(self):
        marcoPrincipal = Frame(
            self.ventanaRaiz,
            bg=COLOR_FONDO,
            bd=1,
            relief="solid",
            highlightbackground=COLOR_ACENTO,
            highlightcolor=COLOR_ACENTO,
            highlightthickness=1,
            padx=24,
            pady=24,
        )
        marcoPrincipal.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
        marcoPrincipal.columnconfigure(0, weight=1)
        marcoPrincipal.rowconfigure(1, weight=1)

        etiquetaTitulo = Label(
            marcoPrincipal,
            text="Cobertura médica",
            bg=COLOR_FONDO,
            fg=COLOR_PRINCIPAL,
            font=("Cambria", 20),
        )
        etiquetaTitulo.grid(row=0, column=0, sticky="w", pady=(0, 16))

        marcoLista = Frame(marcoPrincipal, bg=COLOR_FONDO)
        marcoLista.grid(row=1, column=0, sticky="nsew")
        marcoLista.columnconfigure(0, weight=1)
        marcoLista.rowconfigure(0, weight=1)

        barraDesplazamiento = Scrollbar(marcoLista)
        barraDesplazamiento.grid(row=0, column=1, sticky="ns")

        self.listaServicios = Listbox(
            marcoLista,
            bg=COLOR_FONDO,
            fg=COLOR_PRINCIPAL,
            font=("Segoe UI", 11),
            relief="solid",
            bd=1,
            highlightbackground=COLOR_ACENTO,
            highlightcolor=COLOR_ACENTO,
            highlightthickness=1,
            selectmode=SINGLE,
            activestyle="none",
            yscrollcommand=barraDesplazamiento.set,
        )
        self.listaServicios.grid(row=0, column=0, sticky="nsew", ipady=6)
        self.listaServicios.bind("<<ListboxSelect>>", self.alSeleccionarServicio)
        barraDesplazamiento.configure(command=self.listaServicios.yview)

        marcoEstado = Frame(
            marcoPrincipal,
            bg=COLOR_FONDO,
            bd=1,
            relief="solid",
            highlightbackground=COLOR_ACENTO,
            highlightcolor=COLOR_ACENTO,
            highlightthickness=1,
            padx=16,
            pady=16,
        )
        marcoEstado.grid(row=2, column=0, sticky="ew", pady=(16, 0))
        marcoEstado.columnconfigure(0, weight=1)

        self.etiquetaEstado = Label(
            marcoEstado,
            textvariable=self.estadoMensajeVar,
            bg=COLOR_FONDO,
            fg=self.estadoColorActual,
            font=("Segoe UI Semibold", 13),
            justify="left",
            anchor="w",
        )
        self.etiquetaEstado.grid(row=0, column=0, sticky="ew")

    def obtenerServicioCobertura(self):
        if self.servicio is None:
            self.servicio = self.fabricaServicio()
        return self.servicio

    def cargarServicios(self):
        try:
            self.servicios = self.obtenerServicioCobertura().obtenerServiciosCubiertos()
        except Exception as error:
            self.servicios = []
            self.estadoMensajeVar.set(f"No se pudieron cargar los servicios: {error}")
            self.estadoColorActual = COLOR_ERROR
            self.etiquetaEstado.configure(fg=COLOR_ERROR)
            return

        self.listaServicios.delete(0, "end")
        for servicio in self.servicios:
            self.listaServicios.insert("end", servicio.get("nombre", "Servicio sin nombre"))

    def alSeleccionarServicio(self, evento=None):
        seleccion = self.listaServicios.curselection()
        if not seleccion:
            return

        indice = seleccion[0]
        if indice >= len(self.servicios):
            return

        servicio = self.servicios[indice]
        estado = (servicio.get("estado") or "").strip().lower()
        nombre = servicio.get("nombre", "Servicio")

        textoEstado = TEXTOS_POR_ESTADO.get(estado, "Estado desconocido")
        colorEstado = COLORES_POR_ESTADO.get(estado, COLOR_SECUNDARIO)

        self.estadoMensajeVar.set(f"{nombre}: {textoEstado}")
        self.estadoColorActual = colorEstado
        self.etiquetaEstado.configure(fg=colorEstado)