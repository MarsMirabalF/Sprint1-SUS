import re

PATRON_CORREO = r"^[\w\.\-]+@[\w\.\-]+\.\w+$"
PATRON_CEDULA = r"^\d{6,12}$"
PATRON_TELEFONO = r"^\d{7,15}$"


def esTextoValido(valor):
    """True si el valor es una cadena no vacía (ignorando espacios)."""
    return isinstance(valor, str) and valor.strip() != ""


def esCedulaValida(cedula):
    """Cédula de Identidad: solo dígitos, entre 6 y 12 caracteres."""
    return isinstance(cedula, str) and re.match(PATRON_CEDULA, cedula.strip()) is not None


def esCorreoValido(correo):
    return isinstance(correo, str) and re.match(PATRON_CORREO, correo.strip()) is not None


def esTelefonoValido(telefono):
    return isinstance(telefono, str) and re.match(PATRON_TELEFONO, telefono.strip()) is not None
