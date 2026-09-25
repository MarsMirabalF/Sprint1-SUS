from datetime import datetime

from servidorSeguroUniversitario.configuracion.configuracionFirebase import obtenerReferencia
from servidorSeguroUniversitario.utilidades.validadores import (
    esTextoValido,
    esCedulaValida,
    esCorreoValido,
    esTelefonoValido,
)

NODO_ESTUDIANTES = "estudiantes"
NODO_AFILIADOS = "afiliados"

CAMPOS_OBLIGATORIOS = [
    "matricula",
    "cedulaIdentidad",
    "nombreCompleto",
    "carrera",
    "correoElectronico",
    "telefono",
    "direccion",
    "fechaNacimiento",
]

ESTADO_ACTIVO = "activo"

CODIGO_CAMPOS_INCOMPLETOS = "CAMPOS_INCOMPLETOS"
CODIGO_FORMATO_INVALIDO = "FORMATO_INVALIDO"
CODIGO_MATRICULA_INEXISTENTE = "MATRICULA_INEXISTENTE"
CODIGO_SEGURO_YA_ACTIVO = "SEGURO_YA_ACTIVO"
CODIGO_AFILIACION_EXITOSA = "AFILIACION_EXITOSA"
CODIGO_ERROR_INESPERADO = "ERROR_INESPERADO"


class servicioAfiliacion:

    def __init__(self):
        self.referenciaEstudiantes = obtenerReferencia(NODO_ESTUDIANTES)
        self.referenciaAfiliados = obtenerReferencia(NODO_AFILIADOS)

    def validarCamposObligatorios(self, datosFormulario):
        camposFaltantes = []
        for campo in CAMPOS_OBLIGATORIOS:
            valor = datosFormulario.get(campo)
            if not esTextoValido(valor):
                camposFaltantes.append(campo)
        return camposFaltantes

    def validarFormatoDeDatos(self, datosFormulario):
        camposInvalidos = []
        if not esCedulaValida(datosFormulario.get("cedulaIdentidad", "")):
            camposInvalidos.append("cedulaIdentidad")
        if not esCorreoValido(datosFormulario.get("correoElectronico", "")):
            camposInvalidos.append("correoElectronico")
        if not esTelefonoValido(datosFormulario.get("telefono", "")):
            camposInvalidos.append("telefono")
        return camposInvalidos

    def buscarEstudiantePorMatricula(self, matricula):
        return self.referenciaEstudiantes.child(matricula).get()

    def existeSeguroActivoPorCedula(self, cedulaIdentidad):
        resultados = (
            self.referenciaAfiliados.order_by_child("cedulaIdentidad")
            .equal_to(cedulaIdentidad)
            .get()
        )
        if not resultados:
            return False
        for registro in resultados.values():
            if registro.get("estado") == ESTADO_ACTIVO:
                return True
        return False

    def afiliarEstudiante(self, datosFormulario):
        try:
            camposFaltantes = self.validarCamposObligatorios(datosFormulario)
            if camposFaltantes:
                return {
                    "exito": False,
                    "codigo": CODIGO_CAMPOS_INCOMPLETOS,
                    "mensaje": "Debe completar todos los campos obligatorios.",
                    "camposFaltantes": camposFaltantes,
                }

            camposInvalidos = self.validarFormatoDeDatos(datosFormulario)
            if camposInvalidos:
                return {
                    "exito": False,
                    "codigo": CODIGO_FORMATO_INVALIDO,
                    "mensaje": "Uno o más campos tienen un formato inválido.",
                    "camposInvalidos": camposInvalidos,
                }

            matricula = datosFormulario["matricula"].strip()
            cedulaIdentidad = datosFormulario["cedulaIdentidad"].strip()

            estudiante = self.buscarEstudiantePorMatricula(matricula)
            if estudiante is None:
                return {
                    "exito": False,
                    "codigo": CODIGO_MATRICULA_INEXISTENTE,
                    "mensaje": "La matrícula ingresada no existe en los registros de la universidad.",
                }

            if estudiante.get("tieneSeguroActivo") is True:
                return {
                    "exito": False,
                    "codigo": CODIGO_SEGURO_YA_ACTIVO,
                    "mensaje": "El estudiante ya posee un seguro activo según los registros de la universidad.",
                }

            if self.existeSeguroActivoPorCedula(cedulaIdentidad):
                return {
                    "exito": False,
                    "codigo": CODIGO_SEGURO_YA_ACTIVO,
                    "mensaje": "Ya existe una afiliación activa registrada con esta Cédula de Identidad.",
                }

            nuevoRegistro = {
                "matricula": matricula,
                "cedulaIdentidad": cedulaIdentidad,
                "nombreCompleto": datosFormulario["nombreCompleto"].strip(),
                "carrera": datosFormulario["carrera"].strip(),
                "correoElectronico": datosFormulario["correoElectronico"].strip(),
                "telefono": datosFormulario["telefono"].strip(),
                "direccion": datosFormulario["direccion"].strip(),
                "fechaNacimiento": datosFormulario["fechaNacimiento"].strip(),
                "fechaAfiliacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "estado": ESTADO_ACTIVO,
            }

            referenciaNuevoAfiliado = self.referenciaAfiliados.push(nuevoRegistro)
            self.referenciaEstudiantes.child(matricula).update({"tieneSeguroActivo": True})

            return {
                "exito": True,
                "codigo": CODIGO_AFILIACION_EXITOSA,
                "mensaje": "La afiliación se realizó con éxito.",
                "idAfiliado": referenciaNuevoAfiliado.key,
            }

        except Exception as error:
            return {
                "exito": False,
                "codigo": CODIGO_ERROR_INESPERADO,
                "mensaje": f"Ocurrió un error inesperado al procesar la afiliación: {error}",
            }