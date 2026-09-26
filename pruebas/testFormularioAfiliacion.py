import unittest
from unittest.mock import Mock

from clienteSeguroUniversitario.interfaz.formularioAfiliacion import (
    CODIGO_AFILIACION_EXITOSA,
    CODIGO_FORMATO_INVALIDO,
    CODIGO_MATRICULA_INEXISTENTE,
    COLOR_BORDE_ERROR,
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
        formulario.entradasFormulario = {
            nombreCampo: Mock() for nombreCampo, _ in formulario.camposFormulario
        }
        formulario.mensajesPorCodigo = {}
        formulario.fabricaServicio = Mock()
        formulario.servicio = None
        formulario.habilitarPopups = False
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

    def test_enviar_afiliacion_valida_campos_obligatorios_antes_del_servicio(self):
        formulario = self.crearFormularioBase()
        formulario.variablesFormulario["correoElectronico"].set("   ")
        servicioSimulado = Mock()
        formulario.fabricaServicio = Mock(return_value=servicioSimulado)

        formulario.enviarAfiliacion()

        servicioSimulado.afiliarEstudiante.assert_not_called()
        self.assertIn(
            "Campos obligatorios faltantes: Correo electrónico.",
            formulario.estadoMensajeVar.get(),
        )
        formulario.entradasFormulario["correoElectronico"].configure.assert_any_call(
            highlightbackground=COLOR_BORDE_ERROR, highlightcolor=COLOR_BORDE_ERROR
        )

    def test_actualizar_estado_agrega_detalles_de_campos_invalidos(self):
        formulario = self.crearFormularioBase()

        formulario.actualizarEstadoSegunResultado(
            {
                "codigo": CODIGO_FORMATO_INVALIDO,
                "mensaje": "Uno o más campos tienen un formato inválido.",
                "camposInvalidos": ["cedulaIdentidad", "telefono"],
            }
        )

        self.assertIn(
            "Campos con formato inválido: Cédula de identidad, Teléfono.",
            formulario.estadoMensajeVar.get(),
        )


if __name__ == "__main__":
    unittest.main()
