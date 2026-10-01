import base64
import os
import sys
from datetime import datetime

from fpdf import FPDF

from servidorSeguroUniversitario.configuracion.configuracionFirebase import obtenerReferencia

NODO_ESTUDIANTES = "estudiantes"
NODO_CONSULTAS_MEDICAS = "consultasMedicas"
NODO_COMPROBANTES_MEDICOS = "comprobantesMedicos"

FORMATO_FECHA = "%Y-%m-%d"


def _carpetaProyecto():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _carpetaRecursosEmpaquetados():
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "recursos")
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recursos")


CARPETA_COMPROBANTES_POR_DEFECTO = os.path.join(_carpetaProyecto(), "comprobantesGenerados")
RUTA_FIRMA_DIGITAL = os.path.join(_carpetaRecursosEmpaquetados(), "firmaDigital.jpg")

CODIGO_MATRICULA_INEXISTENTE = "MATRICULA_INEXISTENTE"
CODIGO_SIN_CONSULTA_PREVIA = "SIN_CONSULTA_PREVIA"
CODIGO_CONSULTA_PREVIA_ENCONTRADA = "CONSULTA_PREVIA_ENCONTRADA"
CODIGO_CONSULTA_NO_VALIDA = "CONSULTA_NO_VALIDA"
CODIGO_COMPROBANTE_GENERADO = "COMPROBANTE_GENERADO"
CODIGO_COMPROBANTE_NO_ENCONTRADO = "COMPROBANTE_NO_ENCONTRADO"
CODIGO_ERROR_INESPERADO = "ERROR_INESPERADO"


class servicioComprobante:

    def __init__(self, carpetaComprobantes=None):
        self.referenciaEstudiantes = obtenerReferencia(NODO_ESTUDIANTES)
        self.referenciaConsultasMedicas = obtenerReferencia(NODO_CONSULTAS_MEDICAS)
        self.referenciaComprobantesMedicos = obtenerReferencia(NODO_COMPROBANTES_MEDICOS)
        self.carpetaComprobantes = carpetaComprobantes or CARPETA_COMPROBANTES_POR_DEFECTO

    def _obtenerConsultasDelEstudiante(self, matricula):
        """Todas las consultas registradas de esa matrícula (sin filtrar por fecha)."""
        resultados = (
            self.referenciaConsultasMedicas.order_by_child("matricula")
            .equal_to(matricula)
            .get()
        )
        return resultados or {}

    def _obtenerConsultasPrevias(self, matricula, fechaReferencia=None):

        fechaLimite = fechaReferencia or datetime.now().strftime(FORMATO_FECHA)
        todasLasConsultas = self._obtenerConsultasDelEstudiante(matricula)

        consultasPrevias = {
            idConsulta: datos
            for idConsulta, datos in todasLasConsultas.items()
            if datos.get("fechaConsulta", "") <= fechaLimite
        }

        return dict(
            sorted(
                consultasPrevias.items(),
                key=lambda item: item[1].get("fechaConsulta", ""),
                reverse=True,
            )
        )


    def habilitarBotonDescarga(self, matricula, fechaReferencia=None):
        try:
            if not matricula or not str(matricula).strip():
                return {
                    "exito": False,
                    "codigo": CODIGO_MATRICULA_INEXISTENTE,
                    "mensaje": "Debe indicar la matrícula del estudiante.",
                    "habilitado": False,
                }

            matricula = str(matricula).strip()

            estudiante = self.referenciaEstudiantes.child(matricula).get()
            if estudiante is None:
                return {
                    "exito": False,
                    "codigo": CODIGO_MATRICULA_INEXISTENTE,
                    "mensaje": "La matrícula ingresada no existe en los registros de la universidad.",
                    "habilitado": False,
                }

            consultasPrevias = self._obtenerConsultasPrevias(matricula, fechaReferencia)

            if not consultasPrevias:
                return {
                    "exito": True,
                    "codigo": CODIGO_SIN_CONSULTA_PREVIA,
                    "mensaje": "El estudiante no registra ninguna consulta médica previa a la fecha actual.",
                    "habilitado": False,
                }

            return {
                "exito": True,
                "codigo": CODIGO_CONSULTA_PREVIA_ENCONTRADA,
                "mensaje": "El estudiante registra al menos una consulta médica previa.",
                "habilitado": True,
                "totalConsultasPrevias": len(consultasPrevias),
            }

        except Exception as error:
            return {
                "exito": False,
                "codigo": CODIGO_ERROR_INESPERADO,
                "mensaje": f"Ocurrió un error inesperado al verificar la consulta previa: {error}",
                "habilitado": False,
            }

    def obtenerConsultasDelEstudiante(self, matricula):
        try:
            if not matricula or not str(matricula).strip():
                return {
                    "exito": False,
                    "codigo": CODIGO_MATRICULA_INEXISTENTE,
                    "mensaje": "Debe indicar la matrícula del estudiante.",
                }

            registros = self._obtenerConsultasDelEstudiante(str(matricula).strip())
            listaConsultas = [
                {"idConsulta": idConsulta, **datos} for idConsulta, datos in registros.items()
            ]
            listaConsultas.sort(key=lambda consulta: consulta.get("fechaConsulta", ""), reverse=True)

            return {
                "exito": True,
                "codigo": "CONSULTAS_OBTENIDAS",
                "mensaje": f"Se encontraron {len(listaConsultas)} consultas.",
                "consultas": listaConsultas,
            }

        except Exception as error:
            return {
                "exito": False,
                "codigo": CODIGO_ERROR_INESPERADO,
                "mensaje": f"Ocurrió un error inesperado al obtener las consultas: {error}",
            }

    def generarComprobante(self, matricula, idConsulta=None):
        try:
            matricula = str(matricula).strip() if matricula else ""

            resultadoHabilitacion = self.habilitarBotonDescarga(matricula)
            if not resultadoHabilitacion["habilitado"]:
                return resultadoHabilitacion

            consultasPrevias = self._obtenerConsultasPrevias(matricula)

            if idConsulta:
                if idConsulta not in consultasPrevias:
                    return {
                        "exito": False,
                        "codigo": CODIGO_CONSULTA_NO_VALIDA,
                        "mensaje": "La consulta seleccionada no existe, no es previa a hoy, o no pertenece a este estudiante.",
                    }
                consultaSeleccionada = consultasPrevias[idConsulta]
                idConsultaSeleccionada = idConsulta
            else:
                idConsultaSeleccionada, consultaSeleccionada = next(iter(consultasPrevias.items()))

            nombreArchivo, rutaArchivo, contenidoPdf = self._generarArchivoPdf(
                idConsultaSeleccionada, consultaSeleccionada
            )

            self._guardarComprobanteEnPerfil(
                idConsultaSeleccionada, consultaSeleccionada, nombreArchivo, contenidoPdf
            )

            return {
                "exito": True,
                "codigo": CODIGO_COMPROBANTE_GENERADO,
                "mensaje": "El comprobante se generó y se guardó en el perfil del estudiante.",
                "rutaArchivo": rutaArchivo,
                "idConsulta": idConsultaSeleccionada,
                "nombreCompleto": consultaSeleccionada.get("nombreCompleto", ""),
                "fechaConsulta": consultaSeleccionada.get("fechaConsulta", ""),
                "guardadoEnPerfil": True,
            }

        except Exception as error:
            return {
                "exito": False,
                "codigo": CODIGO_ERROR_INESPERADO,
                "mensaje": f"Ocurrió un error inesperado al generar el comprobante: {error}",
            }

    def listarComprobantesDelEstudiante(self, matricula):
        try:
            matricula = str(matricula).strip() if matricula else ""
            if not matricula:
                return {
                    "exito": False,
                    "codigo": CODIGO_MATRICULA_INEXISTENTE,
                    "mensaje": "Debe indicar la matrícula del estudiante.",
                }

            resultados = (
                self.referenciaComprobantesMedicos.order_by_child("matricula")
                .equal_to(matricula)
                .get()
                or {}
            )

            listaComprobantes = [
                {
                    "idConsulta": idConsulta,
                    "nombreCompleto": datos.get("nombreCompleto", ""),
                    "nombreServicio": datos.get("nombreServicio", ""),
                    "fechaConsulta": datos.get("fechaConsulta", ""),
                    "fechaGeneracion": datos.get("fechaGeneracion", ""),
                    "nombreArchivo": datos.get("nombreArchivo", ""),
                }
                for idConsulta, datos in resultados.items()
            ]
            listaComprobantes.sort(key=lambda item: item.get("fechaConsulta", ""), reverse=True)

            return {
                "exito": True,
                "codigo": "COMPROBANTES_OBTENIDOS",
                "mensaje": f"Se encontraron {len(listaComprobantes)} comprobantes guardados.",
                "comprobantes": listaComprobantes,
            }

        except Exception as error:
            return {
                "exito": False,
                "codigo": CODIGO_ERROR_INESPERADO,
                "mensaje": f"Ocurrió un error inesperado al listar los comprobantes: {error}",
            }

    def descargarComprobanteGuardado(self, idConsulta, carpetaDestino=None):
        try:
            if not idConsulta or not str(idConsulta).strip():
                return {
                    "exito": False,
                    "codigo": CODIGO_COMPROBANTE_NO_ENCONTRADO,
                    "mensaje": "Debe indicar el comprobante a descargar.",
                }

            datos = self.referenciaComprobantesMedicos.child(str(idConsulta).strip()).get()
            if datos is None:
                return {
                    "exito": False,
                    "codigo": CODIGO_COMPROBANTE_NO_ENCONTRADO,
                    "mensaje": "No existe un comprobante guardado con ese identificador.",
                }

            carpetaDestino = carpetaDestino or self.carpetaComprobantes
            os.makedirs(carpetaDestino, exist_ok=True)

            nombreArchivo = datos.get("nombreArchivo") or f"comprobante_{idConsulta}.pdf"
            rutaArchivo = os.path.join(carpetaDestino, nombreArchivo)

            contenidoPdf = base64.b64decode(datos.get("contenidoBase64", ""))
            with open(rutaArchivo, "wb") as archivoPdf:
                archivoPdf.write(contenidoPdf)

            return {
                "exito": True,
                "codigo": CODIGO_COMPROBANTE_GENERADO,
                "mensaje": "El comprobante guardado se recuperó correctamente.",
                "rutaArchivo": rutaArchivo,
                "nombreCompleto": datos.get("nombreCompleto", ""),
                "fechaConsulta": datos.get("fechaConsulta", ""),
            }

        except Exception as error:
            return {
                "exito": False,
                "codigo": CODIGO_ERROR_INESPERADO,
                "mensaje": f"Ocurrió un error inesperado al recuperar el comprobante: {error}",
            }

    def _generarArchivoPdf(self, idConsulta, datosConsulta):
        os.makedirs(self.carpetaComprobantes, exist_ok=True)

        matricula = datosConsulta.get("matricula", "")
        nombreCompleto = datosConsulta.get("nombreCompleto", "")
        fechaConsulta = datosConsulta.get("fechaConsulta", "")
        nombreServicio = datosConsulta.get("nombreServicio", "")
        medicoTratante = datosConsulta.get("medicoTratante", "")

        nombreArchivo = f"comprobante_{matricula}_{idConsulta}.pdf"
        rutaArchivo = os.path.join(self.carpetaComprobantes, nombreArchivo)

        pdf = FPDF(format="A4")
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 12, "Comprobante de Atención Médica", ln=True, align="C")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, "Seguro Social Universitario", ln=True, align="C")
        pdf.ln(8)

        pdf.set_font("Helvetica", "", 12)
        filas = [
            ("Nombre del estudiante:", nombreCompleto),
            ("Matrícula:", matricula),
            ("Fecha de la atención:", fechaConsulta),
            ("Servicio médico:", nombreServicio),
            ("Médico tratante:", medicoTratante or "-"),
        ]
        for etiqueta, valor in filas:
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(55, 9, etiqueta)
            pdf.set_font("Helvetica", "", 12)
            pdf.cell(0, 9, str(valor), ln=True)

        pdf.ln(10)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 5, "Este comprobante es válido solo si incluye la firma digital autorizada.", ln=True)
        pdf.ln(6)

        if os.path.exists(RUTA_FIRMA_DIGITAL):
            anchoFirma = 55
            altoFirma = 25
            yFirma = pdf.get_y()
            pdf.image(RUTA_FIRMA_DIGITAL, x=20, y=yFirma, w=anchoFirma, h=altoFirma)
            pdf.set_y(yFirma + altoFirma + 2)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(anchoFirma + 10, 5, "_" * 32, ln=True)
            pdf.cell(anchoFirma + 10, 5, "Firma digital autorizada", ln=True)
            pdf.cell(anchoFirma + 10, 5, "Seguro Social Universitario", ln=True)
        else:
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(0, 5, "[Firma digital no disponible]", ln=True)

        pdf.ln(8)
        pdf.set_font("Helvetica", "I", 9)
        fechaGeneracion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf.cell(0, 6, f"Comprobante generado el {fechaGeneracion}.", ln=True)

        contenidoPdf = bytes(pdf.output())
        with open(rutaArchivo, "wb") as archivoPdf:
            archivoPdf.write(contenidoPdf)

        return nombreArchivo, rutaArchivo, contenidoPdf

    def _guardarComprobanteEnPerfil(self, idConsulta, datosConsulta, nombreArchivo, contenidoPdf):
        registro = {
            "matricula": datosConsulta.get("matricula", ""),
            "cedulaIdentidad": datosConsulta.get("cedulaIdentidad", ""),
            "nombreCompleto": datosConsulta.get("nombreCompleto", ""),
            "idConsulta": idConsulta,
            "nombreServicio": datosConsulta.get("nombreServicio", ""),
            "medicoTratante": datosConsulta.get("medicoTratante", ""),
            "fechaConsulta": datosConsulta.get("fechaConsulta", ""),
            "fechaGeneracion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nombreArchivo": nombreArchivo,
            "contenidoBase64": base64.b64encode(contenidoPdf).decode("ascii"),
        }
        self.referenciaComprobantesMedicos.child(idConsulta).set(registro)