try:
    from tkinter import Button, Entry, Frame, Label, StringVar, Toplevel, messagebox
    from tkinter import ttk
except ModuleNotFoundError:
    class widgetNoDisponible:
        def __init__(self, *args, **kwargs):
            raise ModuleNotFoundError(
                "Tkinter no está disponible en este entorno. Instale Tk para usar la interfaz gráfica."
            )

    Button = Entry = Frame = Label = Toplevel = widgetNoDisponible
    StringVar = widgetNoDisponible
    ttk = None

    class messagebox:
        showinfo = showwarning = showerror = widgetNoDisponible

COLOR_FONDO = "#F7F3E9"
COLOR_PRINCIPAL = "#2C3B2E"
COLOR_SECUNDARIO = "#6B7C6E"
COLOR_ACENTO = "#A9BBA0"
COLOR_ERROR = "#B3541E"


class vistaAtencionesMedicas:

    def __init__(self, ventanaRaiz, matriculaInicial="", fabricaServicio=None):
        self.ventanaRaiz = ventanaRaiz
        self.matriculaInicial = matriculaInicial
        self.fabricaServicio = fabricaServicio or self.crearServicioComprobante
        self.servicio = None
        self.consultas = []
        self.consultaSeleccionada = None
        self.descargaHabilitada = False
        self.botonDescargar = None
        self.variableMatricula = StringVar(value=matriculaInicial)
        self.variableEstado = StringVar(value="Ingrese una matrícula para consultar las atenciones.")

        self.configurarVentana()
        self.construirInterfaz()

        if matriculaInicial.strip():
            self.cargarAtenciones()

    @staticmethod
    def crearServicioComprobante():
        from servidorSeguroUniversitario.servicios.servicioComprobante import servicioComprobante

        return servicioComprobante()

    def configurarVentana(self):
        self.ventanaRaiz.title("Seguro Universitario - Atenciones médicas")
        self.ventanaRaiz.configure(bg=COLOR_FONDO)
        self.ventanaRaiz.minsize(900, 560)
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

        Label(
            marcoPrincipal,
            text="Atenciones médicas",
            bg=COLOR_FONDO,
            fg=COLOR_PRINCIPAL,
            font=("Cambria", 20),
        ).grid(row=0, column=0, sticky="w", pady=(0, 16))

        marcoBusqueda = Frame(marcoPrincipal, bg=COLOR_FONDO)
        marcoBusqueda.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        marcoBusqueda.columnconfigure(1, weight=1)

        Label(
            marcoBusqueda,
            text="Matrícula",
            bg=COLOR_FONDO,
            fg=COLOR_PRINCIPAL,
            font=("Segoe UI", 11),
        ).grid(row=0, column=0, sticky="w", padx=(0, 16))

        Entry(
            marcoBusqueda,
            textvariable=self.variableMatricula,
            bg=COLOR_FONDO,
            fg=COLOR_PRINCIPAL,
            font=("Segoe UI", 11),
            relief="solid",
            bd=0,
            highlightbackground=COLOR_ACENTO,
            highlightcolor=COLOR_ACENTO,
            highlightthickness=1,
            insertbackground=COLOR_PRINCIPAL,
        ).grid(row=0, column=1, sticky="ew", ipady=4)

        Button(
            marcoBusqueda,
            text="Consultar",
            command=self.cargarAtenciones,
            bg=COLOR_PRINCIPAL,
            fg=COLOR_FONDO,
            activebackground=COLOR_SECUNDARIO,
            activeforeground=COLOR_FONDO,
            font=("Segoe UI Semibold", 11),
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
        ).grid(row=0, column=2, padx=(16, 0))

        marcoTabla = Frame(marcoPrincipal, bg=COLOR_FONDO)
        marcoTabla.grid(row=2, column=0, sticky="nsew")
        marcoTabla.columnconfigure(0, weight=1)
        marcoTabla.rowconfigure(0, weight=1)

        columnas = ("fecha", "hora", "servicio", "medico", "observaciones")
        self.tablaAtenciones = ttk.Treeview(
            marcoTabla,
            columns=columnas,
            show="headings",
            selectmode="browse",
        )
        encabezados = {
            "fecha": "Fecha",
            "hora": "Hora",
            "servicio": "Servicio médico",
            "medico": "Médico tratante",
            "observaciones": "Observaciones",
        }
        anchos = {"fecha": 100, "hora": 80, "servicio": 190, "medico": 170, "observaciones": 280}
        for columna in columnas:
            self.tablaAtenciones.heading(columna, text=encabezados[columna])
            self.tablaAtenciones.column(columna, width=anchos[columna], anchor="w")
        self.tablaAtenciones.grid(row=0, column=0, sticky="nsew")
        self.tablaAtenciones.bind("<<TreeviewSelect>>", self.seleccionarAtencion)

        barraDesplazamiento = ttk.Scrollbar(
            marcoTabla, orient="vertical", command=self.tablaAtenciones.yview
        )
        barraDesplazamiento.grid(row=0, column=1, sticky="ns")
        self.tablaAtenciones.configure(yscrollcommand=barraDesplazamiento.set)

        self.etiquetaEstado = Label(
            marcoPrincipal,
            textvariable=self.variableEstado,
            bg=COLOR_FONDO,
            fg=COLOR_SECUNDARIO,
            font=("Segoe UI", 9),
            justify="left",
            anchor="w",
            wraplength=820,
        )
        self.etiquetaEstado.grid(row=3, column=0, sticky="ew", pady=(16, 8))

        self.botonDescargar = Button(
            marcoPrincipal,
            text="Descargar comprobante",
            command=self.descargarComprobante,
            state="disabled",
            bg=COLOR_PRINCIPAL,
            fg=COLOR_FONDO,
            activebackground=COLOR_SECUNDARIO,
            activeforeground=COLOR_FONDO,
            disabledforeground=COLOR_SECUNDARIO,
            font=("Segoe UI Semibold", 11),
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
        )
        self.botonDescargar.grid(row=4, column=0, sticky="w", pady=(8, 0))

    def obtenerServicioComprobante(self):
        if self.servicio is None:
            self.servicio = self.fabricaServicio()
        return self.servicio

    def limpiarTabla(self):
        for elemento in self.tablaAtenciones.get_children():
            self.tablaAtenciones.delete(elemento)
        self.consultas = []
        self.consultaSeleccionada = None
        self.descargaHabilitada = False
        self.botonDescargar.configure(state="disabled")

    def cargarAtenciones(self):
        matricula = self.variableMatricula.get().strip()
        self.limpiarTabla()

        if not matricula:
            self.variableEstado.set("Debe ingresar una matrícula para consultar las atenciones.")
            self.etiquetaEstado.configure(fg=COLOR_ERROR)
            return

        try:
            resultado = self.obtenerServicioComprobante().obtenerConsultasDelEstudiante(matricula)
            resultadoDescarga = self.obtenerServicioComprobante().habilitarBotonDescarga(matricula)
        except Exception as error:
            resultado = {"exito": False, "mensaje": f"Ocurrió un error inesperado: {error}"}
            resultadoDescarga = {"habilitado": False}

        if not resultado.get("exito"):
            self.variableEstado.set(resultado.get("mensaje", "No fue posible obtener las atenciones."))
            self.etiquetaEstado.configure(fg=COLOR_ERROR)
            return

        self.consultas = resultado.get("consultas", [])
        self.descargaHabilitada = resultadoDescarga.get("habilitado", False) is True
        for consulta in self.consultas:
            self.tablaAtenciones.insert(
                "",
                "end",
                iid=consulta.get("idConsulta"),
                values=(
                    consulta.get("fechaConsulta", ""),
                    consulta.get("horaConsulta", ""),
                    consulta.get("nombreServicio", ""),
                    consulta.get("medicoTratante", "") or "-",
                    consulta.get("observaciones", "") or "-",
                ),
            )

        self.variableEstado.set(resultado.get("mensaje", "Atenciones consultadas."))
        self.etiquetaEstado.configure(fg=COLOR_SECUNDARIO)
        if resultadoDescarga.get("habilitado"):
            self.variableEstado.set(
                f"{resultado.get('mensaje', 'Atenciones consultadas.')} "
                "Seleccione una atención para descargar su comprobante."
            )

    def seleccionarAtencion(self, evento=None):
        seleccion = self.tablaAtenciones.selection()
        self.consultaSeleccionada = seleccion[0] if seleccion else None

        habilitado = self.descargaHabilitada and self.consultaSeleccionada is not None and any(
            consulta.get("idConsulta") == self.consultaSeleccionada for consulta in self.consultas
        )
        self.botonDescargar.configure(state="normal" if habilitado else "disabled")

    def descargarComprobante(self):
        if not self.consultaSeleccionada:
            self.botonDescargar.configure(state="disabled")
            return

        matricula = self.variableMatricula.get().strip()
        resultado = self.obtenerServicioComprobante().generarComprobante(
            matricula, self.consultaSeleccionada
        )

        if resultado.get("exito"):
            messagebox.showinfo(
                "Comprobante generado",
                f"El comprobante se guardó correctamente en:\n{resultado.get('rutaArchivo', '')}",
                parent=self.ventanaRaiz,
            )
        else:
            messagebox.showwarning(
                "Descarga no disponible",
                resultado.get("mensaje", "No fue posible generar el comprobante."),
                parent=self.ventanaRaiz,
            )


def abrirVentanaAtenciones(ventanaPadre, matriculaInicial="", fabricaServicio=None):
    ventanaAtenciones = Toplevel(ventanaPadre)
    vistaAtencionesMedicas(
        ventanaAtenciones,
        matriculaInicial=matriculaInicial,
        fabricaServicio=fabricaServicio,
    )
    ventanaAtenciones.transient(ventanaPadre)
    ventanaAtenciones.grab_set()
    return ventanaAtenciones