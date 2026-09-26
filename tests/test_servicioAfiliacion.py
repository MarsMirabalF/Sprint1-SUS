import unittest
from unittest.mock import MagicMock

from servidorSeguroUniversitario.servicios.servicioAfiliacion import (
    CODIGO_AFILIACION_EXITOSA,
    CODIGO_CAMPOS_INCOMPLETOS,
    CODIGO_FORMATO_INVALIDO,
    CODIGO_MATRICULA_INEXISTENTE,
    CODIGO_SEGURO_YA_ACTIVO,
    servicioAfiliacion,
)


class ServicioAfiliacionTest(unittest.TestCase):
    def setUp(self):
        self.referenciaEstudiantes = MagicMock()
        self.referenciaAfiliados = MagicMock()
        self.servicio = servicioAfiliacion(
            referenciaEstudiantes=self.referenciaEstudiantes,
            referenciaAfiliados=self.referenciaAfiliados,
        )
        self.datosBase = {
            "matricula": "20231001",
            "cedulaIdentidad": "9876543",
            "nombreCompleto": "Maria Fernanda Rojas",
            "carrera": "Ingenieria de Sistemas",
            "correoElectronico": "maria.rojas@uni.edu.bo",
            "telefono": "70012345",
            "direccion": "Av. Siempre Viva #123",
            "fechaNacimiento": "2001-05-14",
        }

    def _mock_busqueda_estudiante(self, estudiante):
        referenciaMatricula = MagicMock()
        referenciaMatricula.get.return_value = estudiante
        self.referenciaEstudiantes.child.return_value = referenciaMatricula
        return referenciaMatricula

    def _mock_query_afiliados(self, campo, valor, resultados):
        queryOrdenada = MagicMock()
        queryFiltrada = MagicMock()
        queryFiltrada.get.return_value = resultados
        queryOrdenada.equal_to.return_value = queryFiltrada
        self.referenciaAfiliados.order_by_child.return_value = queryOrdenada

    def test_retorna_campos_incompletos(self):
        datos = dict(self.datosBase)
        datos["telefono"] = ""

        respuesta = self.servicio.afiliarEstudiante(datos)

        self.assertFalse(respuesta["exito"])
        self.assertEqual(respuesta["codigo"], CODIGO_CAMPOS_INCOMPLETOS)
        self.assertIn("telefono", respuesta["camposFaltantes"])

    def test_retorna_formato_invalido(self):
        datos = dict(self.datosBase)
        datos["correoElectronico"] = "correo-sin-formato"

        respuesta = self.servicio.afiliarEstudiante(datos)

        self.assertFalse(respuesta["exito"])
        self.assertEqual(respuesta["codigo"], CODIGO_FORMATO_INVALIDO)
        self.assertIn("correoElectronico", respuesta["camposInvalidos"])

    def test_retorna_matricula_inexistente(self):
        self._mock_busqueda_estudiante(None)

        respuesta = self.servicio.afiliarEstudiante(dict(self.datosBase))

        self.assertFalse(respuesta["exito"])
        self.assertEqual(respuesta["codigo"], CODIGO_MATRICULA_INEXISTENTE)

    def test_retorna_seguro_ya_activo_por_matricula_en_afiliados(self):
        self._mock_busqueda_estudiante({"tieneSeguroActivo": False})
        self._mock_query_afiliados(
            "matricula",
            self.datosBase["matricula"],
            {"id1": {"estado": "activo"}},
        )

        respuesta = self.servicio.afiliarEstudiante(dict(self.datosBase))

        self.assertFalse(respuesta["exito"])
        self.assertEqual(respuesta["codigo"], CODIGO_SEGURO_YA_ACTIVO)

    def test_retorna_seguro_ya_activo_por_cedula(self):
        self._mock_busqueda_estudiante({"tieneSeguroActivo": False})

        queryPorMatricula = MagicMock()
        resultadoMatricula = MagicMock()
        resultadoMatricula.get.return_value = {}
        queryPorMatricula.equal_to.return_value = resultadoMatricula

        queryPorCedula = MagicMock()
        resultadoCedula = MagicMock()
        resultadoCedula.get.return_value = {"id2": {"estado": "activo"}}
        queryPorCedula.equal_to.return_value = resultadoCedula

        self.referenciaAfiliados.order_by_child.side_effect = [queryPorMatricula, queryPorCedula]

        respuesta = self.servicio.afiliarEstudiante(dict(self.datosBase))

        self.assertFalse(respuesta["exito"])
        self.assertEqual(respuesta["codigo"], CODIGO_SEGURO_YA_ACTIVO)

    def test_retorna_afiliacion_exitosa(self):
        referenciaMatricula = self._mock_busqueda_estudiante({"tieneSeguroActivo": False})

        queryPorMatricula = MagicMock()
        resultadoMatricula = MagicMock()
        resultadoMatricula.get.return_value = {}
        queryPorMatricula.equal_to.return_value = resultadoMatricula

        queryPorCedula = MagicMock()
        resultadoCedula = MagicMock()
        resultadoCedula.get.return_value = {}
        queryPorCedula.equal_to.return_value = resultadoCedula

        self.referenciaAfiliados.order_by_child.side_effect = [queryPorMatricula, queryPorCedula]

        referenciaNuevoAfiliado = MagicMock()
        referenciaNuevoAfiliado.key = "-NUEVOID"
        self.referenciaAfiliados.push.return_value = referenciaNuevoAfiliado

        respuesta = self.servicio.afiliarEstudiante(dict(self.datosBase))

        self.assertTrue(respuesta["exito"])
        self.assertEqual(respuesta["codigo"], CODIGO_AFILIACION_EXITOSA)
        self.assertEqual(respuesta["idAfiliado"], "-NUEVOID")
        referenciaMatricula.update.assert_called_once_with({"tieneSeguroActivo": True})


if __name__ == "__main__":
    unittest.main()
