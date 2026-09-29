from servidorSeguroUniversitario.configuracion.configuracionFirebase import obtenerReferencia
from servidorSeguroUniversitario.utilidades.validadores import esCedulaValida, esTextoValido


NODO_ESTUDIANTES = "estudiantes"

CODIGO_CAMPOS_INCOMPLETOS = "CAMPOS_INCOMPLETOS"
CODIGO_FORMATO_INVALIDO = "FORMATO_INVALIDO"
CODIGO_CREDENCIALES_INVALIDAS = "CREDENCIALES_INVALIDAS"
CODIGO_LOGIN_EXITOSO = "LOGIN_EXITOSO"
CODIGO_ERROR_INESPERADO = "ERROR_INESPERADO"


class servicioLogin:

    def __init__(self):
        self.referenciaEstudiantes = obtenerReferencia(NODO_ESTUDIANTES)

    def autenticarEstudiante(self, matricula, cedulaIdentidad):
        try:
            matricula = matricula.strip() if isinstance(matricula, str) else matricula
            cedulaIdentidad = (
                cedulaIdentidad.strip()
                if isinstance(cedulaIdentidad, str)
                else cedulaIdentidad
            )

            camposFaltantes = []
            if not esTextoValido(matricula):
                camposFaltantes.append("matricula")
            if not esTextoValido(cedulaIdentidad):
                camposFaltantes.append("cedulaIdentidad")
            if camposFaltantes:
                return {
                    "exito": False,
                    "codigo": CODIGO_CAMPOS_INCOMPLETOS,
                    "mensaje": "Debe ingresar la matrícula y la Cédula de Identidad.",
                    "camposFaltantes": camposFaltantes,
                }

            if not esCedulaValida(cedulaIdentidad):
                return {
                    "exito": False,
                    "codigo": CODIGO_FORMATO_INVALIDO,
                    "mensaje": "La Cédula de Identidad debe contener entre 6 y 12 dígitos.",
                    "camposInvalidos": ["cedulaIdentidad"],
                }

            estudiante = self.referenciaEstudiantes.child(matricula).get()
            if not estudiante or estudiante.get("cedulaIdentidad") != cedulaIdentidad:
                return {
                    "exito": False,
                    "codigo": CODIGO_CREDENCIALES_INVALIDAS,
                    "mensaje": "La matrícula o la Cédula de Identidad no son válidas.",
                }

            return {
                "exito": True,
                "codigo": CODIGO_LOGIN_EXITOSO,
                "mensaje": "Inicio de sesión exitoso.",
                "matricula": matricula,
                "estudiante": estudiante,
            }
        except Exception as error:
            return {
                "exito": False,
                "codigo": CODIGO_ERROR_INESPERADO,
                "mensaje": f"Ocurrió un error inesperado al iniciar sesión: {error}",
            }
