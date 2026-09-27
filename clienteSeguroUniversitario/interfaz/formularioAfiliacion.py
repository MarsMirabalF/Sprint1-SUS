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

    class messagebox:
        @staticmethod
        def showinfo(*args, **kwargs):
            return None

        @staticmethod
        def showwarning(*args, **kwargs):
            return None

        @staticmethod
        def showerror(*args, **kwargs):
            return None

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
COLOR_BORDE_NORMAL = COLOR_ACENTO
COLOR_BORDE_ERROR = COLOR_ERROR

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
        self.entradasFormulario = {}
        self.habilitarPopups = True

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
            self.entradasFormulario[nombreCampo] = entradaCampo

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

        botonCobertura = Button(
            marcoBotones,
            text="Consultar cobertura",
            command=self.abrirCoberturaMedica,
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
        botonCobertura.grid(row=0, column=2, padx=(8, 0))

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

    def enviarAfiliacion(self):
        datosFormulario = self.construirDatosAfiliacion()
        camposFaltantes = self.obtenerCamposFaltantes(datosFormulario)
        if camposFaltantes:
            self.actualizarEstadoSegunResultado(
                {
                    "exito": False,
                    "codigo": CODIGO_CAMPOS_INCOMPLETOS,
                    "mensaje": self.mensajesPorCodigo.get(
                        CODIGO_CAMPOS_INCOMPLETOS, "Debe completar todos los campos obligatorios."
                    ),
                    "camposFaltantes": camposFaltantes,
                }
            )
            return

        try:
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

    def obtenerCamposFaltantes(self, datosFormulario):
        camposFaltantes = []
        for nombreCampo, _ in self.camposFormulario:
            if not datosFormulario.get(nombreCampo):
                camposFaltantes.append(nombreCampo)
        return camposFaltantes

    def obtenerNombreCampo(self, nombreCampo):
        for codigoCampo, textoEtiqueta in self.camposFormulario:
            if codigoCampo == nombreCampo:
                return textoEtiqueta
        return nombreCampo

    def limpiarResaltadoCampos(self):
        for entradaCampo in getattr(self, "entradasFormulario", {}).values():
            entradaCampo.configure(
                highlightbackground=COLOR_BORDE_NORMAL, highlightcolor=COLOR_BORDE_NORMAL
            )

    def resaltarCampos(self, campos):
        for nombreCampo in campos:
            entradaCampo = getattr(self, "entradasFormulario", {}).get(nombreCampo)
            if entradaCampo is not None:
                entradaCampo.configure(
                    highlightbackground=COLOR_BORDE_ERROR, highlightcolor=COLOR_BORDE_ERROR
                )

    def construirMensajeDetallado(self, resultado):
        mensajeBase = resultado.get("mensaje") or self.mensajesPorCodigo.get(
            resultado.get("codigo", CODIGO_ERROR_INESPERADO),
            self.mensajesPorCodigo[CODIGO_ERROR_INESPERADO],
        )
        detalles = []

        camposFaltantes = resultado.get("camposFaltantes") or []
        if camposFaltantes:
            nombresCampos = [self.obtenerNombreCampo(campo) for campo in camposFaltantes]
            detalles.append(f"Campos obligatorios faltantes: {', '.join(nombresCampos)}.")

        camposInvalidos = resultado.get("camposInvalidos") or []
        if camposInvalidos:
            nombresCampos = [self.obtenerNombreCampo(campo) for campo in camposInvalidos]
            detalles.append(f"Campos con formato inválido: {', '.join(nombresCampos)}.")

        idAfiliado = resultado.get("idAfiliado")
        if idAfiliado:
            detalles.append(f"ID de afiliación generado: {idAfiliado}.")

        if not detalles:
            return mensajeBase
        return f"{mensajeBase}\n\n" + "\n".join(detalles)

    def mostrarPopupResultado(self, codigo, mensajeDetallado):
        if not getattr(self, "habilitarPopups", False):
            return

        if codigo == CODIGO_AFILIACION_EXITOSA:
            messagebox.showinfo("Afiliación exitosa", mensajeDetallado)
            return

        if codigo == CODIGO_MATRICULA_INEXISTENTE:
            messagebox.showwarning("Matrícula inexistente", mensajeDetallado)
            return

        if codigo == CODIGO_SEGURO_YA_ACTIVO:
            messagebox.showwarning("Seguro activo detectado", mensajeDetallado)
            return

        if codigo == CODIGO_CAMPOS_INCOMPLETOS:
            messagebox.showerror("Campos obligatorios incompletos", mensajeDetallado)
            return

        if codigo == CODIGO_FORMATO_INVALIDO:
            messagebox.showerror("Formato de datos inválido", mensajeDetallado)
            return

        messagebox.showerror("Error de afiliación", mensajeDetallado)

    def actualizarEstadoSegunResultado(self, resultado):
        codigo = resultado.get("codigo", CODIGO_ERROR_INESPERADO)
        mensajeDetallado = self.construirMensajeDetallado(resultado)
        self.limpiarResaltadoCampos()

        camposAResaltar = []
        camposFaltantes = resultado.get("camposFaltantes")
        if camposFaltantes:
            camposAResaltar.extend(camposFaltantes)
        camposInvalidos = resultado.get("camposInvalidos")
        if camposInvalidos:
            camposAResaltar.extend(camposInvalidos)
        if camposAResaltar:
            self.resaltarCampos(camposAResaltar)

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

        self.estadoMensajeVar.set(mensajeDetallado)
        self.estadoColorActual = colorEstado
        self.etiquetaEstado.configure(fg=colorEstado)
        self.mostrarPopupResultado(codigo, mensajeDetallado)

    def limpiarFormulario(self):
        for variableCampo in self.variablesFormulario.values():
            variableCampo.set("")
        self.limpiarResaltadoCampos()

        self.estadoMensajeVar.set("Formulario restablecido. Complete los datos para continuar.")
        self.estadoColorActual = COLOR_SECUNDARIO
        self.etiquetaEstado.configure(fg=COLOR_SECUNDARIO)
