import unittest

from servidorSeguroUniversitario.utilidades.validadores import (
    esCedulaValida,
    esCorreoValido,
    esTelefonoValido,
)


class ValidadoresFormatoTest(unittest.TestCase):
    def test_cedula_valida(self):
        self.assertTrue(esCedulaValida("1234567"))

    def test_cedula_invalida(self):
        self.assertFalse(esCedulaValida("12A456"))

    def test_correo_valido(self):
        self.assertTrue(esCorreoValido("persona@uni.edu.bo"))

    def test_correo_invalido(self):
        self.assertFalse(esCorreoValido("persona@uni"))

    def test_telefono_valido(self):
        self.assertTrue(esTelefonoValido("70012345"))

    def test_telefono_invalido(self):
        self.assertFalse(esTelefonoValido("70-012"))


if __name__ == "__main__":
    unittest.main()
