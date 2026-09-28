try:
    from tkinter import Button, Entry, Frame, Label, StringVar, Toplevel, messagebox
except ModuleNotFoundError:
    class widgetNoDisponible:
        def __init__(self, *args, **kwargs):
            raise ModuleNotFoundError(
                "Tkinter no está disponible en este entorno. Instale Tk para usar la interfaz gráfica."
            )

    Button = Entry = Frame = Label = Toplevel = widgetNoDisponible
    StringVar = widgetNoDisponible

    class messagebox:
        @staticmethod
        def askyesno(*args, **kwargs):
            raise ModuleNotFoundError(
                "Tkinter no está disponible en este entorno. Instale Tk para usar la interfaz gráfica."
            )

        showinfo = showwarning = showerror = askyesno

COLOR_FONDO = "#F7F3E9"
COLOR_PRINCIPAL = "#2C3B2E"
COLOR_SECUNDARIO = "#6B7C6E"
COLOR_ACENTO = "#A9BBA0"
COLOR_ERROR = "#B3541E"

ESTADO_VIGENTE = "Vigente"
ESTADO_VENCIDO = "Vencido"


class seccionRenovacionSeguro:

    def __init__(self, ventanaRaiz, matriculaInicial="", fabricaServicio=None):
        self.ventanaRaiz = ventanaRaiz
        self.matriculaInicial = matriculaInicial
        self.fabricaServicio = fabricaServicio or self.crearServicioRenovacion
        self.servicio = None
        self.variableMatricula = StringVar(value=matriculaInicial)
        self.variableEstado = StringVar(value="Ingrese una matrícula para consultar el seguro.")
        self.variableInicio = StringVar(value="-")
        self.variableFin = StringVar(value="-")
        self.variableUltimaRenovacion = StringVar(value="-")

        self.configurarVentana()
        self.construirInterfaz()

        if matriculaInicial.strip():
            self.consultarEstadoSeguro()

    @staticmethod
    def crearServicioRenovacion():
        from servidorSeguroUniversitario.servicios.servicioRenovacion import servicioRenovacion

        return servicioRenovacion()

    def configurarVentana(self):
        self.ventanaRaiz.title("Seguro Universitario - Renovación")
        self.ventanaRaiz.configure(bg=COLOR_FONDO)
        self.ventanaRaiz.minsize(760, 480)
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

        Label(
            marcoPrincipal,
            text="Renovación del seguro",
            bg=COLOR_FONDO,
            fg=COLOR_PRINCIPAL,
            font=("Cambria", 20),
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        Label(
            marcoPrincipal,
            text="Consulta la vigencia del seguro asociado al perfil del estudiante.",
            bg=COLOR_FONDO,
            fg=COLOR_SECUNDARIO,
            font=("Segoe UI", 11),
        ).grid(row=1, column=0, sticky="w", pady=(0, 24))

        marcoBusqueda = Frame(marcoPrincipal, bg=COLOR_FONDO)
        marcoBusqueda.grid(row=2, column=0, sticky="ew", pady=(0, 24))
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
            command=self.consultarEstadoSeguro,
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

        Button(
            marcoBusqueda,
            text="Renovar seguro",
            command=self.confirmarRenovacion,
            bg=COLOR_ACENTO,
            fg=COLOR_PRINCIPAL,
            activebackground=COLOR_SECUNDARIO,
            activeforeground=COLOR_FONDO,
            font=("Segoe UI Semibold", 11),
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
        ).grid(row=0, column=3, padx=(8, 0))

        marcoEstado = Frame(
            marcoPrincipal,
            bg=COLOR_FONDO,
            bd=0,
            relief="solid",
            highlightbackground=COLOR_ACENTO,
            highlightcolor=COLOR_ACENTO,
            highlightthickness=1,
            padx=16,
            pady=16,
        )
        marcoEstado.grid(row=3, column=0, sticky="ew")
        marcoEstado.columnconfigure(1, weight=1)

        Label(
            marcoEstado,
            text="Estado de vigencia",
            bg=COLOR_FONDO,
            fg=COLOR_PRINCIPAL,
            font=("Segoe UI Semibold", 11),
        ).grid(row=0, column=0, sticky="w", padx=(0, 24), pady=8)
        self.etiquetaEstado = Label(
            marcoEstado,
            textvariable=self.variableEstado,
            bg=COLOR_FONDO,
            fg=COLOR_SECUNDARIO,
            font=("Segoe UI Semibold", 11),
            anchor="w",
        )
        self.etiquetaEstado.grid(row=0, column=1, sticky="ew", pady=8)

        datosVigencia = [
            ("Inicio de vigencia", self.variableInicio),
            ("Fin de vigencia", self.variableFin),
            ("Última renovación", self.variableUltimaRenovacion),
        ]
        for indice, (texto, variable) in enumerate(datosVigencia, start=1):
            Label(
                marcoEstado,
                text=texto,
                bg=COLOR_FONDO,
                fg=COLOR_PRINCIPAL,
                font=("Segoe UI", 11),
            ).grid(row=indice, column=0, sticky="w", padx=(0, 24), pady=8)
            Label(
                marcoEstado,
                textvariable=variable,
                bg=COLOR_FONDO,
                fg=COLOR_SECUNDARIO,
                font=("Segoe UI", 11),
                anchor="w",
            ).grid(row=indice, column=1, sticky="ew", pady=8)

    def obtenerServicioRenovacion(self):
        if self.servicio is None:
            self.servicio = self.fabricaServicio()
        return self.servicio

    def consultarEstadoSeguro(self):
        matricula = self.variableMatricula.get().strip()
        if not matricula:
            self.variableEstado.set("Debe ingresar una matrícula para consultar el seguro.")
            self.etiquetaEstado.configure(fg=COLOR_ERROR)
            return

        try:
            resultado = self.obtenerServicioRenovacion().consultarEstadoSeguro(matricula)
        except Exception as error:
            resultado = {
                "exito": False,
                "mensaje": f"Ocurrió un error inesperado al consultar el seguro: {error}",
            }

        if not resultado.get("exito"):
            self.variableEstado.set(resultado.get("mensaje", "No fue posible consultar el seguro."))
            self.etiquetaEstado.configure(fg=COLOR_ERROR)
            self.limpiarFechas()
            return

        self.variableEstado.set(resultado.get("estadoVigencia", "Sin vigencia registrada"))
        self.variableInicio.set(resultado.get("fechaInicioVigencia") or "-")
        self.variableFin.set(resultado.get("fechaFinVigencia") or "-")
        self.variableUltimaRenovacion.set(resultado.get("fechaUltimaRenovacion") or "-")
        colorEstado = (
            COLOR_PRINCIPAL
            if resultado.get("estadoVigencia") == ESTADO_VIGENTE
            else COLOR_ERROR
            if resultado.get("estadoVigencia") == ESTADO_VENCIDO
            else COLOR_SECUNDARIO
        )
        self.etiquetaEstado.configure(fg=colorEstado)

    def limpiarFechas(self):
        self.variableInicio.set("-")
        self.variableFin.set("-")
        self.variableUltimaRenovacion.set("-")

    def confirmarRenovacion(self):
        matricula = self.variableMatricula.get().strip()
        if not matricula:
            self.variableEstado.set("Debe ingresar una matrícula para renovar el seguro.")
            self.etiquetaEstado.configure(fg=COLOR_ERROR)
            return

        confirmar = messagebox.askyesno(
            "Confirmar renovación",
            (
                f"¿Desea renovar el seguro universitario de la matrícula {matricula}?\n\n"
                "La operación verificará la matrícula del periodo vigente y actualizará "
                "la vigencia del seguro."
            ),
            parent=self.ventanaRaiz,
        )
        if confirmar:
            self.renovarSeguro()

    def renovarSeguro(self):
        matricula = self.variableMatricula.get().strip()
        try:
            resultado = self.obtenerServicioRenovacion().renovarSeguro(matricula)
        except Exception as error:
            resultado = {
                "exito": False,
                "mensaje": f"Ocurrió un error inesperado al renovar el seguro: {error}",
            }

        if resultado.get("exito"):
            self.variableEstado.set(resultado.get("estadoVigencia", ESTADO_VIGENTE))
            self.variableInicio.set(resultado.get("fechaInicioVigencia") or "-")
            self.variableFin.set(resultado.get("fechaFinVigencia") or "-")
            self.variableUltimaRenovacion.set(resultado.get("fechaRenovacion") or "-")
            self.etiquetaEstado.configure(fg=COLOR_PRINCIPAL)
            messagebox.showinfo(
                "Renovación exitosa",
                resultado.get("mensaje", "La renovación del seguro se realizó con éxito."),
                parent=self.ventanaRaiz,
            )
            return

        messagebox.showwarning(
            "Renovación no realizada",
            resultado.get("mensaje", "No fue posible renovar el seguro."),
            parent=self.ventanaRaiz,
        )


def abrirVentanaRenovacion(ventanaPadre, matriculaInicial="", fabricaServicio=None):
    ventanaRenovacion = Toplevel(ventanaPadre)
    seccionRenovacionSeguro(
        ventanaRenovacion,
        matriculaInicial=matriculaInicial,
        fabricaServicio=fabricaServicio,
    )
    ventanaRenovacion.transient(ventanaPadre)
    ventanaRenovacion.grab_set()
    return ventanaRenovacion