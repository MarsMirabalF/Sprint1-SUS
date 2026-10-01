import unittest
from unittest.mock import Mock, patch

from clienteSeguroUniversitario.interfaz.formularioAfiliacion import (
    CODIGO_AFILIACION_EXITOSA,
    CODIGO_MATRICULA_INEXISTENTE,
    COLOR_ERROR,
    COLOR_PRINCIPAL,
    formularioAfiliacion,
)


class variableSimulada:

    def __init__(self, valor=""):
        self.valor = valor

    def get(self):
        return self.valor

    def set(self, valor):
        self.valor = valor


class pruebasFormularioAfiliacion(unittest.TestCase):

    def crearFormularioBase(self):
        formulario = formularioAfiliacion.__new__(formularioAfiliacion)
        formulario.camposFormulario = [
            ("matricula", "Matrícula"),
            ("cedulaIdentidad", "Cédula de identidad"),
            ("nombreCompleto", "Nombre completo"),
            ("carrera", "Carrera"),
            ("correoElectronico", "Correo electrónico"),
            ("telefono", "Teléfono"),
            ("direccion", "Dirección"),
            ("fechaNacimiento", "Fecha de nacimiento"),
        ]
        formulario.variablesFormulario = {
            "matricula": variableSimulada(" 20231001 "),
            "cedulaIdentidad": variableSimulada(" 9876543 "),
            "nombreCompleto": variableSimulada(" Maria Rojas "),
            "carrera": variableSimulada(" Ingeniería de Sistemas "),
            "correoElectronico": variableSimulada(" maria@uni.edu "),
            "telefono": variableSimulada(" 70012345 "),
            "direccion": variableSimulada(" Av. Siempre Viva #123 "),
            "fechaNacimiento": variableSimulada(" 2001-05-14 "),
        }
        formulario.estadoMensajeVar = variableSimulada("")
        formulario.etiquetaEstado = Mock()
        formulario.mensajesPorCodigo = {}
        formulario.fabricaServicio = Mock()
        formulario.servicio = None
        return formulario

    def test_construir_datos_envia_campos_esperados(self):
        formulario = self.crearFormularioBase()

        datos = formulario.construirDatosAfiliacion()

        self.assertEqual(
            datos,
            {
                "matricula": "20231001",
                "cedulaIdentidad": "9876543",
                "nombreCompleto": "Maria Rojas",
                "carrera": "Ingeniería de Sistemas",
                "correoElectronico": "maria@uni.edu",
                "telefono": "70012345",
                "direccion": "Av. Siempre Viva #123",
                "fechaNacimiento": "2001-05-14",
            },
        )

    def test_enviar_afiliacion_llama_servicio_y_actualiza_estado_exitoso(self):
        formulario = self.crearFormularioBase()
        servicioSimulado = Mock()
        servicioSimulado.afiliarEstudiante.return_value = {
            "codigo": CODIGO_AFILIACION_EXITOSA,
            "mensaje": "La afiliación se realizó con éxito.",
        }
        formulario.fabricaServicio = Mock(return_value=servicioSimulado)

        with patch(
            "clienteSeguroUniversitario.interfaz.formularioAfiliacion.messagebox.showinfo"
        ):
            formulario.ventanaRaiz = Mock()
            formulario.enviarAfiliacion()

        servicioSimulado.afiliarEstudiante.assert_called_once_with(
            {
                "matricula": "20231001",
                "cedulaIdentidad": "9876543",
                "nombreCompleto": "Maria Rojas",
                "carrera": "Ingeniería de Sistemas",
                "correoElectronico": "maria@uni.edu",
                "telefono": "70012345",
                "direccion": "Av. Siempre Viva #123",
                "fechaNacimiento": "2001-05-14",
            }
        )
        self.assertEqual(formulario.estadoMensajeVar.get(), "La afiliación se realizó con éxito.")
        formulario.etiquetaEstado.configure.assert_called_with(fg=COLOR_PRINCIPAL)

    def test_actualizar_estado_interpreta_codigo_error(self):
        formulario = self.crearFormularioBase()

        formulario.actualizarEstadoSegunResultado(
            {
                "codigo": CODIGO_MATRICULA_INEXISTENTE,
                "mensaje": "La matrícula ingresada no existe en los registros de la universidad.",
            }
        )

        self.assertEqual(
            formulario.estadoMensajeVar.get(),
            "La matrícula ingresada no existe en los registros de la universidad.",
        )
        formulario.etiquetaEstado.configure.assert_called_with(fg=COLOR_ERROR)

    def test_popup_muestra_campos_faltantes(self):
        formulario = self.crearFormularioBase()
        formulario.ventanaRaiz = Mock()

        with patch(
            "clienteSeguroUniversitario.interfaz.formularioAfiliacion.messagebox.showwarning"
        ) as mostrarAdvertencia:
            formulario.mostrarPopupResultado(
                {
                    "codigo": "CAMPOS_INCOMPLETOS",
                    "mensaje": "Debe completar todos los campos obligatorios.",
                    "camposFaltantes": ["correoElectronico", "telefono"],
                }
            )

        texto = mostrarAdvertencia.call_args.args[1]
        self.assertIn("Correo electrónico", texto)
        self.assertIn("Teléfono", texto)

    def test_popup_exitoso_muestra_id_afiliacion(self):
        formulario = self.crearFormularioBase()
        formulario.ventanaRaiz = Mock()

        with patch(
            "clienteSeguroUniversitario.interfaz.formularioAfiliacion.messagebox.showinfo"
        ) as mostrarInformacion:
            formulario.mostrarPopupResultado(
                {
                    "codigo": CODIGO_AFILIACION_EXITOSA,
                    "mensaje": "La afiliación se realizó con éxito.",
                    "idAfiliado": "-ABC123",
                }
            )

        self.assertIn("-ABC123", mostrarInformacion.call_args.args[1])

    def test_seccion_cobertura_calcula_resumen(self):
        from clienteSeguroUniversitario.interfaz.seccionCoberturaMedica import (
            seccionCoberturaMedica,
        )

        seccion = seccionCoberturaMedica.__new__(seccionCoberturaMedica)
        resultado = {
            "servicios": [
                {"cubierto": True},
                {"cubierto": False},
                {"cubierto": True},
            ]
        }

        self.assertEqual(
            seccion.construirResumenCobertura(resultado),
            "2 de 3 servicios médicos cuentan con cobertura.",
        )

    def test_vista_atenciones_conserva_descarga_deshabilitada_sin_consulta_previa(self):
        from clienteSeguroUniversitario.interfaz.vistaAtencionesMedicas import (
            vistaAtencionesMedicas,
        )

        vista = vistaAtencionesMedicas.__new__(vistaAtencionesMedicas)
        vista.consultas = [{"idConsulta": "consulta-futura"}]
        vista.consultaSeleccionada = None
        vista.descargaHabilitada = False
        vista.botonDescargar = Mock()
        vista.tablaAtenciones = Mock()
        vista.tablaAtenciones.selection.return_value = ("consulta-futura",)

        vista.seleccionarAtencion()

        vista.botonDescargar.configure.assert_called_once_with(state="disabled")

    def test_seccion_renovacion_actualiza_estado_y_fechas(self):
        from clienteSeguroUniversitario.interfaz.seccionRenovacionSeguro import (
            seccionRenovacionSeguro,
        )

        seccion = seccionRenovacionSeguro.__new__(seccionRenovacionSeguro)
        seccion.matriculaInicial = "20231002"
        seccion.variableEstado = variableSimulada("")
        seccion.variableInicio = variableSimulada("")
        seccion.variableFin = variableSimulada("")
        seccion.variableUltimaRenovacion = variableSimulada("")
        seccion.etiquetaEstado = Mock()
        seccion.botonRenovar = Mock()
        seccion.fabricaServicio = Mock(
            return_value=Mock(
                consultarEstadoSeguro=Mock(
                    return_value={
                        "exito": True,
                        "estadoVigencia": "Vigente",
                        "fechaInicioVigencia": "2026-08-01",
                        "fechaFinVigencia": "2026-12-15",
                        "fechaUltimaRenovacion": "2026-08-03 09:45:00",
                    }
                )
            )
        )
        seccion.servicio = None

        seccion.consultarEstadoSeguro()

        self.assertEqual(seccion.variableEstado.get(), "Vigente")
        self.assertEqual(seccion.variableFin.get(), "2026-12-15")

    def test_lista_justificativos_construye_filas(self):
        from clienteSeguroUniversitario.interfaz.listaJustificativosMedicos import (
            listaJustificativosMedicos,
        )

        lista = listaJustificativosMedicos.__new__(listaJustificativosMedicos)

        self.assertEqual(
            lista.construirValoresJustificativo(
                {
                    "fechaConsulta": "2026-09-15",
                    "nombreServicio": "Exámenes de laboratorio",
                    "medicoTratante": "Dra. Lucia Perez",
                    "fechaGeneracion": "2026-09-15 13:20:00",
                    "nombreArchivo": "comprobante_20231001_consultaPrueba002.pdf",
                }
            ),
            (
                "2026-09-15",
                "Exámenes de laboratorio",
                "Dra. Lucia Perez",
                "2026-09-15 13:20:00",
                "comprobante_20231001_consultaPrueba002.pdf",
            ),
        )

    def test_detalle_justificativo_construye_datos(self):
        from clienteSeguroUniversitario.interfaz.detalleJustificativoMedico import (
            detalleJustificativoMedico,
        )

        detalle = detalleJustificativoMedico.__new__(detalleJustificativoMedico)
        detalle.justificativo = {
            "idConsulta": "consultaPrueba002",
            "fechaConsulta": "2026-09-15",
            "nombreServicio": "Exámenes de laboratorio",
            "medicoTratante": "Dra. Lucia Perez",
            "fechaGeneracion": "2026-09-15 13:20:00",
            "nombreArchivo": "comprobante_20231001_consultaPrueba002.pdf",
        }

        datos = detalle.obtenerDatosDetalle()

        self.assertEqual(datos[0], ("ID de consulta", "consultaPrueba002"))
        self.assertEqual(datos[2], ("Servicio médico", "Exámenes de laboratorio"))


if __name__ == "__main__":
    unittest.main()
