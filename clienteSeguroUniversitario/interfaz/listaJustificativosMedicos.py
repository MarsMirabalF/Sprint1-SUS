try:
    from tkinter import Button, Frame, Label, Toplevel, StringVar
    from tkinter import ttk
except ModuleNotFoundError:
    class widgetNoDisponible:
        def __init__(self, *args, **kwargs):
            raise ModuleNotFoundError(
                "Tkinter no está disponible en este entorno. Instale Tk para usar la interfaz gráfica."
            )

    Button = Frame = Label = Toplevel = StringVar = widgetNoDisponible
    ttk = None

COLOR_FONDO = "#F7F3E9"
COLOR_PRINCIPAL = "#2C3B2E"
COLOR_SECUNDARIO = "#6B7C6E"
COLOR_ACENTO = "#A9BBA0"
COLOR_ERROR = "#B3541E"


class listaJustificativosMedicos:

    def __init__(self, ventanaRaiz, matricula, fabricaServicio=None):
        self.ventanaRaiz = ventanaRaiz
        self.matricula = matricula
        self.fabricaServicio = fabricaServicio or self.crearServicioHistorial
        self.servicio = None
        self.variableEstado = StringVar(value="Cargando justificativos médicos...")
        self.justificativos = []
        self.justificativoSeleccionado = None
        self.columnaOrdenamiento = "fechaConsulta"
        self.ordenDescendente = True

        self.configurarVentana()
        self.construirInterfaz()
        self.cargarJustificativos()

    @staticmethod
    def crearServicioHistorial():
        from servidorSeguroUniversitario.servicios.servicioHistorialJustificativos import (
            servicioHistorialJustificativos,
        )

        return servicioHistorialJustificativos()

    def configurarVentana(self):
        self.ventanaRaiz.title("Seguro Universitario - Justificativos médicos")
        self.ventanaRaiz.configure(bg=COLOR_FONDO)
        self.ventanaRaiz.minsize(900, 520)
        self.ventanaRaiz.columnconfigure(0, weight=1)
        self.ventanaRaiz.rowconfigure(1, weight=1)

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
        marcoPrincipal.columnconfigure(0, weight=1)
        marcoPrincipal.rowconfigure(2, weight=1)

        encabezado = Frame(marcoPrincipal, bg=COLOR_FONDO)
        encabezado.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        encabezado.columnconfigure(0, weight=1)

        Label(
            encabezado,
            text="Justificativos médicos",
            bg=COLOR_FONDO,
            fg=COLOR_PRINCIPAL,
            font=("Cambria", 20),
        ).grid(row=0, column=0, sticky="w")

        Label(
            encabezado,
            text=f"Matrícula: {self.matricula}",
            bg=COLOR_FONDO,
            fg=COLOR_SECUNDARIO,
            font=("Segoe UI", 11),
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        Button(
            encabezado,
            text="Actualizar",
            command=self.cargarJustificativos,
            bg=COLOR_PRINCIPAL,
            fg=COLOR_FONDO,
            activebackground=COLOR_SECUNDARIO,
            activeforeground=COLOR_FONDO,
            font=("Segoe UI Semibold", 11),
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
        ).grid(row=0, column=1, rowspan=2, sticky="e")

        self.botonDetalle = Button(
            encabezado,
            text="Ver detalle",
            command=self.abrirDetalle,
            state="disabled",
            bg=COLOR_FONDO,
            fg=COLOR_PRINCIPAL,
            activebackground=COLOR_ACENTO,
            activeforeground=COLOR_PRINCIPAL,
            disabledforeground=COLOR_SECUNDARIO,
            font=("Segoe UI Semibold", 11),
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
        )
        self.botonDetalle.grid(row=0, column=2, rowspan=2, sticky="e", padx=(8, 0))

        self.etiquetaEstado = Label(
            marcoPrincipal,
            textvariable=self.variableEstado,
            bg=COLOR_FONDO,
            fg=COLOR_SECUNDARIO,
            font=("Segoe UI", 9),
            anchor="w",
        )
        self.etiquetaEstado.grid(row=1, column=0, sticky="ew", pady=(8, 16))

        marcoTabla = Frame(marcoPrincipal, bg=COLOR_FONDO)
        marcoTabla.grid(row=2, column=0, sticky="nsew")
        marcoTabla.columnconfigure(0, weight=1)
        marcoTabla.rowconfigure(0, weight=1)

        columnas = ("fecha", "servicio", "medico", "generacion", "archivo")
        self.tablaJustificativos = ttk.Treeview(
            marcoTabla,
            columns=columnas,
            show="headings",
            selectmode="browse",
        )
        encabezados = {
            "fecha": "Fecha de atención",
            "servicio": "Servicio médico",
            "medico": "Médico tratante",
            "generacion": "Fecha de generación",
            "archivo": "Archivo",
        }
        anchos = {"fecha": 140, "servicio": 210, "medico": 190, "generacion": 170, "archivo": 270}
        clavesOrdenamiento = {
            "fecha": "fechaConsulta",
            "servicio": "nombreServicio",
            "medico": "medicoTratante",
            "generacion": "fechaGeneracion",
            "archivo": "nombreArchivo",
        }
        for columna in columnas:
            self.tablaJustificativos.heading(
                columna,
                text=encabezados[columna],
                command=lambda clave=clavesOrdenamiento[columna]: self.ordenarJustificativos(clave),
            )
            self.tablaJustificativos.column(columna, width=anchos[columna], anchor="w")
        self.tablaJustificativos.grid(row=0, column=0, sticky="nsew")
        self.tablaJustificativos.bind("<<TreeviewSelect>>", self.seleccionarJustificativo)

        barraDesplazamiento = ttk.Scrollbar(
            marcoTabla, orient="vertical", command=self.tablaJustificativos.yview
        )
        barraDesplazamiento.grid(row=0, column=1, sticky="ns")
        self.tablaJustificativos.configure(yscrollcommand=barraDesplazamiento.set)

    def obtenerServicioHistorial(self):
        if self.servicio is None:
            self.servicio = self.fabricaServicio()
        return self.servicio

    def limpiarTabla(self):
        for elemento in self.tablaJustificativos.get_children():
            self.tablaJustificativos.delete(elemento)
        self.justificativoSeleccionado = None
        self.botonDetalle.configure(state="disabled")

    def construirValoresJustificativo(self, justificativo):
        return (
            justificativo.get("fechaConsulta", ""),
            justificativo.get("nombreServicio", ""),
            justificativo.get("medicoTratante", "") or "-",
            justificativo.get("fechaGeneracion", "") or "-",
            justificativo.get("nombreArchivo", "") or "-",
        )

    def ordenarJustificativos(self, columna):
        if columna == self.columnaOrdenamiento:
            self.ordenDescendente = not self.ordenDescendente
        else:
            self.columnaOrdenamiento = columna
            self.ordenDescendente = False

        self.justificativos.sort(
            key=lambda justificativo: str(justificativo.get(columna, "") or "").casefold(),
            reverse=self.ordenDescendente,
        )

        for posicion, justificativo in enumerate(self.justificativos):
            idConsulta = justificativo.get("idConsulta")
            if idConsulta is not None and self.tablaJustificativos.exists(idConsulta):
                self.tablaJustificativos.move(idConsulta, "", posicion)

    def cargarJustificativos(self):
        self.limpiarTabla()
        try:
            resultado = self.obtenerServicioHistorial().obtenerHistorial(self.matricula)
        except Exception as error:
            resultado = {
                "exito": False,
                "mensaje": f"Ocurrió un error inesperado al obtener los justificativos: {error}",
                "justificativos": [],
            }

        self.justificativos = resultado.get("justificativos", [])
        if not resultado.get("exito"):
            self.variableEstado.set(resultado.get("mensaje", "No fue posible obtener los justificativos."))
            self.etiquetaEstado.configure(fg=COLOR_ERROR)
            return

        for justificativo in self.justificativos:
            self.tablaJustificativos.insert(
                "",
                "end",
                iid=justificativo.get("idConsulta"),
                values=self.construirValoresJustificativo(justificativo),
            )

        self.variableEstado.set(resultado.get("mensaje", "Justificativos consultados."))
        self.etiquetaEstado.configure(fg=COLOR_SECUNDARIO)

    def seleccionarJustificativo(self, evento=None):
        seleccion = self.tablaJustificativos.selection()
        idConsulta = seleccion[0] if seleccion else None
        self.justificativoSeleccionado = next(
            (
                justificativo
                for justificativo in self.justificativos
                if justificativo.get("idConsulta") == idConsulta
            ),
            None,
        )
        self.botonDetalle.configure(
            state="normal" if self.justificativoSeleccionado else "disabled"
        )

    def abrirDetalle(self):
        if not self.justificativoSeleccionado:
            self.botonDetalle.configure(state="disabled")
            return

        from clienteSeguroUniversitario.interfaz.detalleJustificativoMedico import (
            abrirVentanaDetalleJustificativo,
        )

        abrirVentanaDetalleJustificativo(self.ventanaRaiz, self.justificativoSeleccionado)


def abrirVentanaJustificativos(ventanaPadre, matricula, fabricaServicio=None):
    ventanaJustificativos = Toplevel(ventanaPadre)
    listaJustificativosMedicos(
        ventanaJustificativos,
        matricula=matricula,
        fabricaServicio=fabricaServicio,
    )
    ventanaJustificativos.transient(ventanaPadre)
    ventanaJustificativos.grab_set()
    return ventanaJustificativos