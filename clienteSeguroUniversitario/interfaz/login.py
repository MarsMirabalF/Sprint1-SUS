try:
    from tkinter import Button, Entry, Frame, Label, StringVar
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

    Button = Entry = Frame = Label = widgetNoDisponible

COLOR_FONDO = "#F7F3E9"
COLOR_PRINCIPAL = "#2C3B2E"
COLOR_SECUNDARIO = "#6B7C6E"
COLOR_ACENTO = "#A9BBA0"
COLOR_ERROR = "#B3541E"


class login:

    def __init__(self, ventanaRaiz, alAutenticar=None, fabricaServicio=None):
        self.ventanaRaiz = ventanaRaiz
        self.alAutenticar = alAutenticar
        self.fabricaServicio = fabricaServicio or self.crearServicioLogin
        self.servicio = None
        self.variableMatricula = StringVar()
        self.variableCedulaIdentidad = StringVar()
        self.variableEstado = StringVar(value="Ingrese sus credenciales para continuar.")
        self.etiquetaEstado = None

        self.configurarVentana()
        self.construirInterfaz()

    @staticmethod
    def crearServicioLogin():
        from servidorSeguroUniversitario.servicios.servicioLogin import servicioLogin

        return servicioLogin()

    def configurarVentana(self):
        self.ventanaRaiz.title("Seguro Universitario - Inicio de sesión")
        self.ventanaRaiz.configure(bg=COLOR_FONDO)
        self.ventanaRaiz.minsize(520, 400)
        self.ventanaRaiz.columnconfigure(0, weight=1)
        self.ventanaRaiz.rowconfigure(0, weight=1)

    def construirInterfaz(self):
        marco = Frame(self.ventanaRaiz, bg=COLOR_FONDO, padx=48, pady=48)
        marco.grid(row=0, column=0)
        marco.columnconfigure(1, weight=1)

        Label(
            marco,
            text="Seguro Universitario",
            bg=COLOR_FONDO,
            fg=COLOR_PRINCIPAL,
            font=("Cambria", 24),
        ).grid(row=0, column=0, columnspan=2, pady=(0, 8))
        Label(
            marco,
            text="Inicio de sesión",
            bg=COLOR_FONDO,
            fg=COLOR_SECUNDARIO,
            font=("Segoe UI", 13),
        ).grid(row=1, column=0, columnspan=2, pady=(0, 24))

        self.construirCampo(marco, 2, "Matrícula", self.variableMatricula)
        self.construirCampo(marco, 3, "Cédula de identidad", self.variableCedulaIdentidad)

        Button(
            marco,
            text="Ingresar",
            command=self.iniciarSesion,
            bg=COLOR_PRINCIPAL,
            fg=COLOR_FONDO,
            activebackground=COLOR_SECUNDARIO,
            activeforeground=COLOR_FONDO,
            font=("Segoe UI Semibold", 11),
            bd=0,
            padx=18,
            pady=8,
            cursor="hand2",
        ).grid(row=4, column=0, columnspan=2, pady=(20, 12))

        self.etiquetaEstado = Label(
            marco,
            textvariable=self.variableEstado,
            bg=COLOR_FONDO,
            fg=COLOR_SECUNDARIO,
            font=("Segoe UI", 10),
            wraplength=380,
        )
        self.etiquetaEstado.grid(row=5, column=0, columnspan=2)

    def construirCampo(self, marco, fila, texto, variable):
        Label(
            marco,
            text=texto,
            bg=COLOR_FONDO,
            fg=COLOR_PRINCIPAL,
            font=("Segoe UI", 11),
        ).grid(row=fila, column=0, sticky="w", padx=(0, 16), pady=8)
        Entry(
            marco,
            textvariable=variable,
            bg=COLOR_FONDO,
            fg=COLOR_PRINCIPAL,
            font=("Segoe UI", 11),
            relief="solid",
            bd=0,
            highlightbackground=COLOR_ACENTO,
            highlightcolor=COLOR_ACENTO,
            highlightthickness=1,
        ).grid(row=fila, column=1, sticky="ew", pady=8, ipady=4)

    def obtenerServicioLogin(self):
        if self.servicio is None:
            self.servicio = self.fabricaServicio()
        return self.servicio

    def iniciarSesion(self):
        resultado = self.obtenerServicioLogin().autenticarEstudiante(
            self.variableMatricula.get(), self.variableCedulaIdentidad.get()
        )
        self.variableEstado.set(resultado.get("mensaje", "No fue posible iniciar sesión."))
        self.etiquetaEstado.configure(
            fg=COLOR_PRINCIPAL if resultado.get("exito") else COLOR_ERROR
        )
        if resultado.get("exito") and self.alAutenticar:
            self.alAutenticar(resultado)
