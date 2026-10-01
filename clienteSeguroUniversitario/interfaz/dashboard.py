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


class dashboard:

    def __init__(self, ventanaRaiz, resultadoLogin):
        self.ventanaRaiz = ventanaRaiz
        self.resultadoLogin = resultadoLogin
        self.matricula = resultadoLogin.get("matricula", "")
        self.estudiante = resultadoLogin.get("estudiante", {})

        self.configurarVentana()
        self.construirInterfaz()

    def configurarVentana(self):
        self.ventanaRaiz.title("Seguro Universitario - Dashboard")
        self.ventanaRaiz.configure(bg=COLOR_FONDO)
        self.ventanaRaiz.minsize(720, 520)
        self.ventanaRaiz.columnconfigure(0, weight=1)
        self.ventanaRaiz.rowconfigure(1, weight=1)

    def construirInterfaz(self):
        encabezado = Frame(self.ventanaRaiz, bg=COLOR_PRINCIPAL, padx=32, pady=24)
        encabezado.grid(row=0, column=0, sticky="ew")
        encabezado.columnconfigure(0, weight=1)

        Label(
            encabezado,
            text="Seguro Universitario",
            bg=COLOR_PRINCIPAL,
            fg=COLOR_FONDO,
            font=("Cambria", 24),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        nombre = self.estudiante.get("nombreCompleto", "Estudiante")
        Label(
            encabezado,
            text=f"Bienvenido, {nombre} | Matrícula: {self.matricula}",
            bg=COLOR_PRINCIPAL,
            fg=COLOR_ACENTO,
            font=("Segoe UI", 11),
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        contenido = Frame(self.ventanaRaiz, bg=COLOR_FONDO, padx=48, pady=40)
        contenido.grid(row=1, column=0, sticky="nsew")
        contenido.columnconfigure(0, weight=1)
        contenido.columnconfigure(1, weight=1)

        Label(
            contenido,
            text="¿Qué deseas consultar?",
            bg=COLOR_FONDO,
            fg=COLOR_PRINCIPAL,
            font=("Cambria", 22),
        ).grid(row=0, column=0, columnspan=2, pady=(0, 24))

        opciones = [
            ("Afiliación", self.abrirAfiliacion),
            ("Cobertura médica", self.abrirCobertura),
            ("Atenciones médicas", self.abrirAtenciones),
            ("Renovación del seguro", self.abrirRenovacion),
            ("Justificativos médicos", self.abrirJustificativos),
        ]
        for indice, (texto, comando) in enumerate(opciones):
            fila = indice // 2 + 1
            columna = indice % 2
            Button(
                contenido,
                text=texto,
                command=comando,
                bg=COLOR_PRINCIPAL,
                fg=COLOR_FONDO,
                activebackground=COLOR_SECUNDARIO,
                activeforeground=COLOR_FONDO,
                font=("Segoe UI Semibold", 12),
                bd=0,
                padx=18,
                pady=14,
                cursor="hand2",
            ).grid(row=fila, column=columna, sticky="ew", padx=8, pady=8)

    def abrirAfiliacion(self):
        from clienteSeguroUniversitario.interfaz.formularioAfiliacion import formularioAfiliacion

        ventana = Toplevel(self.ventanaRaiz)
        formularioAfiliacion(ventana)
        self.configurarVentanaSecundaria(ventana)

    def abrirCobertura(self):
        from clienteSeguroUniversitario.interfaz.seccionCoberturaMedica import abrirVentanaCobertura

        abrirVentanaCobertura(self.ventanaRaiz)

    def abrirAtenciones(self):
        from clienteSeguroUniversitario.interfaz.vistaAtencionesMedicas import abrirVentanaAtenciones

        abrirVentanaAtenciones(
            self.ventanaRaiz,
            matriculaInicial=self.matricula,
            nombreInicial=self.estudiante.get("nombreCompleto", ""),
        )

    def abrirRenovacion(self):
        from clienteSeguroUniversitario.interfaz.seccionRenovacionSeguro import abrirVentanaRenovacion

        abrirVentanaRenovacion(
            self.ventanaRaiz,
            matriculaInicial=self.matricula,
            nombreInicial=self.estudiante.get("nombreCompleto", ""),
        )

    def abrirJustificativos(self):
        from clienteSeguroUniversitario.interfaz.listaJustificativosMedicos import (
            abrirVentanaJustificativos,
        )

        abrirVentanaJustificativos(self.ventanaRaiz, matricula=self.matricula)

    @staticmethod
    def configurarVentanaSecundaria(ventana):
        ventana.transient()
