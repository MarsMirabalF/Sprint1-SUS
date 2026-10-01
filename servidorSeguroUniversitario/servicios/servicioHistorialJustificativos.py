from servidorSeguroUniversitario.configuracion.configuracionFirebase import obtenerReferencia

NODO_COMPROBANTES_MEDICOS = "comprobantesMedicos"

CODIGO_MATRICULA_NO_ESPECIFICADA = "MATRICULA_NO_ESPECIFICADA"
CODIGO_HISTORIAL_OBTENIDO = "HISTORIAL_OBTENIDO"
CODIGO_SIN_JUSTIFICATIVOS = "SIN_JUSTIFICATIVOS"
CODIGO_ERROR_INESPERADO = "ERROR_INESPERADO"

class servicioHistorialJustificativos:
    def __init__(self):
        self.referenciaComprobantesMedicos = obtenerReferencia(NODO_COMPROBANTES_MEDICOS)

    def _obtenerComprobantesPorMatricula(self, matricula):
        try:
            return (
                self.referenciaComprobantesMedicos.order_by_child("matricula")
                .equal_to(matricula)
                .get()
                or {}
            )
        except Exception as error:
            if "Index not defined" not in str(error):
                raise
            registros = self.referenciaComprobantesMedicos.get() or {}
            return {
                idComprobante: datos
                for idComprobante, datos in registros.items()
                if datos.get("matricula") == matricula
            }

    def obtenerHistorial(self, matricula):
        try:
            matricula = str(matricula).strip() if matricula else ""
            if not matricula:
                return {
                    "exito": False,
                    "codigo": CODIGO_MATRICULA_NO_ESPECIFICADA,
                    "mensaje": "Debe indicar la matrícula del estudiante.",
                }

            resultados = self._obtenerComprobantesPorMatricula(matricula)

            historial = [
                {
                    "idConsulta": idConsulta,
                    "fechaConsulta": datos.get("fechaConsulta", ""),
                    "medicoTratante": datos.get("medicoTratante", ""),
                    "nombreServicio": datos.get("nombreServicio", ""),
                    "nombreArchivo": datos.get("nombreArchivo", ""),
                    "fechaGeneracion": datos.get("fechaGeneracion", ""),
                }
                for idConsulta, datos in resultados.items()
            ]

            historial.sort(key=lambda item: item["fechaConsulta"], reverse=True)

            if not historial:
                return {
                    "exito": True,
                    "codigo": CODIGO_SIN_JUSTIFICATIVOS,
                    "mensaje": "El estudiante todavía no generó ningún justificativo médico.",
                    "justificativos": [],
                }

            return {
                "exito": True,
                "codigo": CODIGO_HISTORIAL_OBTENIDO,
                "mensaje": f"Se encontraron {len(historial)} justificativos.",
                "justificativos": historial,
            }

        except Exception as error:
            return {
                "exito": False,
                "codigo": CODIGO_ERROR_INESPERADO,
                "mensaje": f"Ocurrió un error inesperado al obtener el historial: {error}",
            }
