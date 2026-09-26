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


if __name__ == "__main__":
    unittest.main()
