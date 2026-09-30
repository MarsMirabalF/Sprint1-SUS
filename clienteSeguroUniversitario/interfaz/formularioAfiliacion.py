try:
    from tkinter import Button, Entry, Frame, Label, StringVar, messagebox
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

    class messagebox:
        @staticmethod
        def showinfo(*args, **kwargs):
            raise ModuleNotFoundError(
                "Tkinter no está disponible en este entorno. Instale Tk para mostrar mensajes."
            )

        showwarning = showerror = showinfo

COLOR_FONDO = "#F7F3E9"
COLOR_PRINCIPAL = "#2C3B2E"
COLOR_SECUNDARIO = "#6B7C6E"
COLOR_ACENTO = "#A9BBA0"
COLOR_ERROR = "#B3541E"

CODIGO_CAMPOS_INCOMPLETOS = "CAMPOS_INCOMPLETOS"
CODIGO_FORMATO_INVALIDO = "FORMATO_INVALIDO"
CODIGO_MATRICULA_INEXISTENTE = "MATRICULA_INEXISTENTE"
CODIGO_SEGURO_YA_ACTIVO = "SEGURO_YA_ACTIVO"
CODIGO_AFILIACION_EXITOSA = "AFILIACION_EXITOSA"
CODIGO_ERROR_INESPERADO = "ERROR_INESPERADO"


class formularioAfiliacion:

    def __init__(self, ventanaRaiz, fabricaServicio=None):
        self.ventanaRaiz = ventanaRaiz
        self.fabricaServicio = fabricaServicio or self.crearServicioAfiliacion
        self.servicio = None

        self.estadoMensajeVar = StringVar(value="Complete el formulario y presione Afiliar.")
        self.estadoColorActual = COLOR_SECUNDARIO
        self.variablesFormulario = {}

        self.mensajesPorCodigo = {
            CODIGO_CAMPOS_INCOMPLETOS: "Debe completar todos los campos obligatorios.",
            CODIGO_FORMATO_INVALIDO: "Verifique formato de cédula, correo y teléfono.",
            CODIGO_MATRICULA_INEXISTENTE: "La matrícula ingresada no existe.",
            CODIGO_SEGURO_YA_ACTIVO: "El estudiante ya cuenta con un seguro activo.",
            CODIGO_AFILIACION_EXITOSA: "Afiliación realizada con éxito.",
            CODIGO_ERROR_INESPERADO: "Ocurrió un error inesperado durante la afiliación.",
        }

        self.camposFormulario = [
            ("matricula", "Matrícula"),
            ("cedulaIdentidad", "Cédula de identidad"),
            ("nombreCompleto", "Nombre completo"),
            ("carrera", "Carrera"),
            ("correoElectronico", "Correo electrónico"),
            ("telefono", "Teléfono"),
            ("direccion", "Dirección"),
            ("fechaNacimiento", "Fecha de nacimiento (AAAA-MM-DD)"),
        ]

        self.configurarVentana()
        self.construirInterfaz()

    @staticmethod
    def crearServicioAfiliacion():
        from servidorSeguroUniversitario.servicios.servicioAfiliacion import servicioAfiliacion

        return servicioAfiliacion()

    def configurarVentana(self):
        self.ventanaRaiz.title("Seguro Universitario - Afiliación")
        self.ventanaRaiz.configure(bg=COLOR_FONDO)
        self.ventanaRaiz.minsize(860, 620)
        self.ventanaRaiz.columnconfigure(0, weight=1)
        self.ventanaRaiz.rowconfigure(1, weight=1)

    def construirInterfaz(self):
        marcoEncabezado = Frame(self.ventanaRaiz, bg=COLOR_PRINCIPAL)
        marcoEncabezado.grid(row=0, column=0, sticky="ew")

        etiquetaEncabezado = Label(
            marcoEncabezado,
            text="Seguro Universitario",
            bg=COLOR_PRINCIPAL,
            fg=COLOR_FONDO,
            font=("Cambria", 20),
            padx=24,
            pady=16,
        )
        etiquetaEncabezado.grid(row=0, column=0, sticky="w")

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

        etiquetaTitulo = Label(
            marcoPrincipal,
            text="Formulario de afiliación",
            bg=COLOR_FONDO,
            fg=COLOR_PRINCIPAL,
            font=("Cambria", 20),
        )
        etiquetaTitulo.grid(row=0, column=0, sticky="w", pady=(0, 16))

        marcoFormulario = Frame(marcoPrincipal, bg=COLOR_FONDO)
        marcoFormulario.grid(row=1, column=0, sticky="nsew")
        marcoFormulario.columnconfigure(0, weight=0)
        marcoFormulario.columnconfigure(1, weight=1)

        for indice, (nombreCampo, textoEtiqueta) in enumerate(self.camposFormulario):
            etiquetaCampo = Label(
                marcoFormulario,
                text=textoEtiqueta,
                bg=COLOR_FONDO,
                fg=COLOR_PRINCIPAL,
                font=("Segoe UI", 11),
            )
            etiquetaCampo.grid(row=indice, column=0, sticky="w", padx=(0, 16), pady=8)

            variableCampo = StringVar()
            self.variablesFormulario[nombreCampo] = variableCampo

            entradaCampo = Entry(
                marcoFormulario,
                textvariable=variableCampo,
                bg=COLOR_FONDO,
                fg=COLOR_PRINCIPAL,
                font=("Segoe UI", 11),
                relief="solid",
                bd=0,
                highlightbackground=COLOR_ACENTO,
                highlightcolor=COLOR_ACENTO,
                highlightthickness=1,
                insertbackground=COLOR_PRINCIPAL,
            )
            entradaCampo.grid(row=indice, column=1, sticky="ew", pady=8, ipady=4)

        marcoBotones = Frame(marcoPrincipal, bg=COLOR_FONDO)
        marcoBotones.grid(row=2, column=0, sticky="w", pady=(16, 8))

        botonAfiliar = Button(
            marcoBotones,
            text="Afiliar",
            command=self.enviarAfiliacion,
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
        )
        botonAfiliar.grid(row=0, column=0, padx=(0, 8))

        botonLimpiar = Button(
            marcoBotones,
            text="Limpiar",
            command=self.limpiarFormulario,
            bg=COLOR_FONDO,
            fg=COLOR_PRINCIPAL,
            activebackground=COLOR_ACENTO,
            activeforeground=COLOR_PRINCIPAL,
            font=("Segoe UI Semibold", 11),
            bd=0,
            relief="solid",
            highlightbackground=COLOR_ACENTO,
            highlightcolor=COLOR_ACENTO,
            highlightthickness=1,
            padx=16,
            pady=8,
            cursor="hand2",
        )
        botonLimpiar.grid(row=0, column=1)

        self.etiquetaEstado = Label(
            marcoPrincipal,
            textvariable=self.estadoMensajeVar,
            bg=COLOR_FONDO,
            fg=self.estadoColorActual,
            font=("Segoe UI", 9),
            justify="left",
            anchor="w",
            wraplength=760,
        )
        self.etiquetaEstado.grid(row=3, column=0, sticky="ew", pady=(8, 0))

    def construirDatosAfiliacion(self):
        datos = {}
        for nombreCampo, _ in self.camposFormulario:
            datos[nombreCampo] = self.variablesFormulario[nombreCampo].get().strip()
        return datos

    def obtenerServicioAfiliacion(self):
        if self.servicio is None:
            self.servicio = self.fabricaServicio()
        return self.servicio

    def abrirCoberturaMedica(self):
        from clienteSeguroUniversitario.interfaz.seccionCoberturaMedica import abrirVentanaCobertura

        abrirVentanaCobertura(self.ventanaRaiz)

    def abrirAtencionesMedicas(self):
        from clienteSeguroUniversitario.interfaz.vistaAtencionesMedicas import abrirVentanaAtenciones

        matricula = self.variablesFormulario.get("matricula")
        matriculaInicial = matricula.get().strip() if matricula else ""
        abrirVentanaAtenciones(self.ventanaRaiz, matriculaInicial=matriculaInicial)

    def abrirRenovacionSeguro(self):
        from clienteSeguroUniversitario.interfaz.seccionRenovacionSeguro import abrirVentanaRenovacion

        matricula = self.variablesFormulario.get("matricula")
        matriculaInicial = matricula.get().strip() if matricula else ""
        abrirVentanaRenovacion(self.ventanaRaiz, matriculaInicial=matriculaInicial)

    def enviarAfiliacion(self):
        try:
            datosFormulario = self.construirDatosAfiliacion()
            resultado = self.obtenerServicioAfiliacion().afiliarEstudiante(datosFormulario)
        except Exception as error:
            resultado = {
                "exito": False,
                "codigo": CODIGO_ERROR_INESPERADO,
                "mensaje": f"Ocurrió un error inesperado: {error}",
            }

        self.actualizarEstadoSegunResultado(resultado)
        self.mostrarPopupResultado(resultado)

    def obtenerDetalleResultado(self, resultado):
        codigo = resultado.get("codigo", CODIGO_ERROR_INESPERADO)

        if codigo == CODIGO_CAMPOS_INCOMPLETOS:
            campos = resultado.get("camposFaltantes", [])
            if campos:
                etiquetas = dict(self.camposFormulario)
                return "Campos pendientes:\n- " + "\n- ".join(
                    etiquetas.get(campo, campo) for campo in campos
                )

        if codigo == CODIGO_FORMATO_INVALIDO:
            campos = resultado.get("camposInvalidos", [])
            if campos:
                etiquetas = dict(self.camposFormulario)
                return "Revise los siguientes campos:\n- " + "\n- ".join(
                    etiquetas.get(campo, campo) for campo in campos
                )

        if codigo == CODIGO_AFILIACION_EXITOSA and resultado.get("idAfiliado"):
            return f"Identificador de afiliación: {resultado['idAfiliado']}"

        return ""

    def mostrarPopupResultado(self, resultado):
        codigo = resultado.get("codigo", CODIGO_ERROR_INESPERADO)
        mensaje = resultado.get("mensaje") or self.mensajesPorCodigo.get(
            codigo, self.mensajesPorCodigo[CODIGO_ERROR_INESPERADO]
        )
        detalle = self.obtenerDetalleResultado(resultado)
        texto = f"{mensaje}\n\n{detalle}" if detalle else mensaje

        if codigo == CODIGO_AFILIACION_EXITOSA:
            messagebox.showinfo("Afiliación exitosa", texto, parent=self.ventanaRaiz)
        elif codigo in {
            CODIGO_CAMPOS_INCOMPLETOS,
            CODIGO_FORMATO_INVALIDO,
            CODIGO_MATRICULA_INEXISTENTE,
            CODIGO_SEGURO_YA_ACTIVO,
        }:
            messagebox.showwarning("Advertencia de afiliación", texto, parent=self.ventanaRaiz)
        else:
            messagebox.showerror("Error de afiliación", texto, parent=self.ventanaRaiz)

    def actualizarEstadoSegunResultado(self, resultado):
        codigo = resultado.get("codigo", CODIGO_ERROR_INESPERADO)
        mensaje = resultado.get("mensaje") or self.mensajesPorCodigo.get(
            codigo, self.mensajesPorCodigo[CODIGO_ERROR_INESPERADO]
        )

        if codigo == CODIGO_AFILIACION_EXITOSA:
            colorEstado = COLOR_PRINCIPAL
        elif codigo in {
            CODIGO_CAMPOS_INCOMPLETOS,
            CODIGO_FORMATO_INVALIDO,
            CODIGO_MATRICULA_INEXISTENTE,
            CODIGO_SEGURO_YA_ACTIVO,
            CODIGO_ERROR_INESPERADO,
        }:
            colorEstado = COLOR_ERROR
        else:
            colorEstado = COLOR_SECUNDARIO

        self.estadoMensajeVar.set(mensaje)
        self.estadoColorActual = colorEstado
        self.etiquetaEstado.configure(fg=colorEstado)

    def limpiarFormulario(self):
        for variableCampo in self.variablesFormulario.values():
            variableCampo.set("")

        self.estadoMensajeVar.set("Formulario restablecido. Complete los datos para continuar.")
        self.estadoColorActual = COLOR_SECUNDARIO
        self.etiquetaEstado.configure(fg=COLOR_SECUNDARIO)
