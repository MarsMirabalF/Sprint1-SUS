try:
    from tkinter import Button, Entry, Frame, Label, StringVar, Toplevel
except ModuleNotFoundError:
    class widgetNoDisponible:
        def __init__(self, *args, **kwargs):
            raise ModuleNotFoundError(
                "Tkinter no está disponible en este entorno. Instale Tk para usar la interfaz gráfica."
            )

    Button = Entry = Frame = Label = Toplevel = widgetNoDisponible
    StringVar = widgetNoDisponible

COLOR_FONDO = "#0B0D08"
COLOR_TARJETA = "#24262A"
COLOR_TEXTO = "#F2F2ED"
COLOR_TEXTO_SECUNDARIO = "#B8BAB4"
COLOR_ACENTO = "#C27613"
COLOR_VIGENTE = "#9DBB67"
COLOR_VENCIDO = "#D36A42"

ESTADO_VIGENTE = "Vigente"
ESTADO_VENCIDO = "Vencido"


class vistaEstadoVigenciaSeguro:

    def __init__(self, ventanaRaiz, matriculaInicial="", fabricaServicio=None):
        self.ventanaRaiz = ventanaRaiz
        self.fabricaServicio = fabricaServicio or self.crearServicioRenovacion
        self.servicio = None
        self.variableMatricula = StringVar(value=matriculaInicial)
        self.variableEstado = StringVar(value="Sin consulta")
        self.variableInicio = StringVar(value="-")
        self.variableFin = StringVar(value="-")
        self.variableRenovacion = StringVar(value="-")
        self.etiquetaEstado = None
        self.etiquetaMensaje = None

        self.configurarVentana()
        self.construirInterfaz()

        if matriculaInicial.strip():
            self.consultarEstadoSeguro()

    @staticmethod
    def crearServicioRenovacion():
        from servidorSeguroUniversitario.servicios.servicioRenovacion import servicioRenovacion

        return servicioRenovacion()

    def configurarVentana(self):
        self.ventanaRaiz.title("Seguro Universitario - Carnet digital")
        self.ventanaRaiz.configure(bg=COLOR_FONDO)
        self.ventanaRaiz.minsize(640, 560)
        self.ventanaRaiz.columnconfigure(0, weight=1)
        self.ventanaRaiz.rowconfigure(1, weight=1)

    def construirInterfaz(self):
        encabezado = Frame(self.ventanaRaiz, bg=COLOR_FONDO)
        encabezado.grid(row=0, column=0, sticky="ew", padx=44, pady=(28, 14))
        encabezado.columnconfigure(0, weight=1)

        Label(
            encabezado,
            text="HU 10 - Renovación del seguro universitario",
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO,
            font=("Segoe UI Semibold", 20),
            justify="left",
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        consulta = Frame(self.ventanaRaiz, bg=COLOR_FONDO)
        consulta.grid(row=1, column=0, sticky="new", padx=44, pady=(0, 18))
        consulta.columnconfigure(1, weight=1)

        Label(
            consulta,
            text="Matrícula",
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 10),
        ).grid(row=0, column=0, sticky="w", padx=(0, 12))

        Entry(
            consulta,
            textvariable=self.variableMatricula,
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            font=("Segoe UI", 11),
            relief="flat",
            bd=0,
        ).grid(row=0, column=1, sticky="ew", ipady=7)

        Button(
            consulta,
            text="Consultar",
            command=self.consultarEstadoSeguro,
            bg=COLOR_ACENTO,
            fg=COLOR_TEXTO,
            activebackground=COLOR_VIGENTE,
            activeforeground=COLOR_FONDO,
            font=("Segoe UI Semibold", 10),
            relief="flat",
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2",
        ).grid(row=0, column=2, padx=(12, 0))

        carnet = Frame(
            self.ventanaRaiz,
            bg=COLOR_TARJETA,
            bd=0,
            highlightbackground="#3A3C40",
            highlightcolor="#3A3C40",
            highlightthickness=1,
            padx=28,
            pady=26,
        )
        carnet.grid(row=2, column=0, sticky="nsew", padx=44, pady=(0, 30))
        carnet.columnconfigure(0, weight=1)

        Label(
            carnet,
            text="Estado visual de vigencia del seguro",
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO,
            font=("Segoe UI Semibold", 16),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self.etiquetaEstado = Label(
            carnet,
            textvariable=self.variableEstado,
            bg=COLOR_ACENTO,
            fg=COLOR_TEXTO,
            font=("Segoe UI Semibold", 18),
            padx=18,
            pady=8,
            anchor="w",
        )
        self.etiquetaEstado.grid(row=1, column=0, sticky="w", pady=(24, 26))

        datos = Frame(carnet, bg=COLOR_TARJETA)
        datos.grid(row=2, column=0, sticky="ew")
        datos.columnconfigure(1, weight=1)
        self.agregarDato(datos, 0, "Inicio de vigencia", self.variableInicio)
        self.agregarDato(datos, 1, "Fin de vigencia", self.variableFin)
        self.agregarDato(datos, 2, "Última renovación", self.variableRenovacion)

        self.etiquetaMensaje = Label(
            carnet,
            text="Consulta una matrícula para ver el estado del seguro.",
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 10),
            justify="left",
            anchor="w",
            wraplength=520,
        )
        self.etiquetaMensaje.grid(row=3, column=0, sticky="ew", pady=(26, 0))

    def agregarDato(self, padre, fila, texto, variable):
        Label(
            padre,
            text=texto,
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 10),
            anchor="w",
        ).grid(row=fila, column=0, sticky="w", pady=7, padx=(0, 24))
        Label(
            padre,
            textvariable=variable,
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO,
            font=("Segoe UI Semibold", 11),
            anchor="w",
        ).grid(row=fila, column=1, sticky="w", pady=7)

    def obtenerServicioRenovacion(self):
        if self.servicio is None:
            self.servicio = self.fabricaServicio()
        return self.servicio

    def consultarEstadoSeguro(self):
        matricula = self.variableMatricula.get().strip()
        if not matricula:
            self.mostrarError("Debe ingresar una matrícula para consultar el seguro.")
            return

        try:
            resultado = self.obtenerServicioRenovacion().consultarEstadoSeguro(matricula)
        except Exception as error:
            resultado = {
                "exito": False,
                "mensaje": f"Ocurrió un error inesperado al consultar el seguro: {error}",
            }

        if not resultado.get("exito"):
            self.mostrarError(resultado.get("mensaje", "No fue posible consultar el seguro."))
            self.limpiarFechas()
            return

        estado = resultado.get("estadoVigencia", "Sin vigencia registrada")
        self.variableEstado.set(estado)
        self.variableInicio.set(resultado.get("fechaInicioVigencia") or "-")
        self.variableFin.set(resultado.get("fechaFinVigencia") or "-")
        self.variableRenovacion.set(resultado.get("fechaUltimaRenovacion") or "-")
        self.etiquetaEstado.configure(bg=self.obtenerColorEstado(estado))
        self.etiquetaMensaje.configure(
            text=resultado.get("mensaje", "Estado del seguro consultado correctamente."),
            fg=COLOR_TEXTO_SECUNDARIO,
        )

    def obtenerColorEstado(self, estado):
        if estado == ESTADO_VIGENTE:
            return COLOR_VIGENTE
        if estado == ESTADO_VENCIDO:
            return COLOR_VENCIDO
        return COLOR_ACENTO

    def mostrarError(self, mensaje):
        self.variableEstado.set("No disponible")
        self.etiquetaEstado.configure(bg=COLOR_VENCIDO)
        self.etiquetaMensaje.configure(text=mensaje, fg=COLOR_VENCIDO)

    def limpiarFechas(self):
        self.variableInicio.set("-")
        self.variableFin.set("-")
        self.variableRenovacion.set("-")


def abrirVentanaEstadoVigencia(ventanaPadre, matriculaInicial="", fabricaServicio=None):
    ventanaEstado = Toplevel(ventanaPadre)
    vistaEstadoVigenciaSeguro(
        ventanaEstado,
        matriculaInicial=matriculaInicial,
        fabricaServicio=fabricaServicio,
    )
    ventanaEstado.transient(ventanaPadre)
    ventanaEstado.grab_set()
    return ventanaEstado