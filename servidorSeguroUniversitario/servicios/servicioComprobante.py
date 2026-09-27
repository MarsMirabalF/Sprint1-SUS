"""
servicioComprobante.py

HU 17 — Obtención de comprobantes médicos.

Servicio de backend (sin UI) responsable de:
    1. Determinar si el botón de descarga debe estar habilitado: el
       estudiante debe tener al menos una consulta médica registrada con
       fecha anterior o igual a hoy (criterio de aceptación 3).
    2. Generar el archivo descargable (PDF) con el nombre del estudiante y
       la fecha de la atención (criterio de aceptación 2).
    3. Guardar ese PDF en el "perfil" del estudiante dentro de la Realtime
       Database (nodo "comprobantesMedicos"), para que quede disponible
       para verlo/descargarlo de nuevo desde cualquier instalación de la
       app (no solo en la máquina donde se generó la primera vez), y para
       que el equipo pueda verlo conectándose a la misma base de Firebase.

No registra las consultas médicas en sí (eso lo carga el personal médico /
otra HU, fuera de este alcance): este servicio solo lee el nodo
"consultasMedicas" para validar y armar el comprobante.

Nota sobre el diseño: Realtime Database no es un servicio de almacenamiento
de archivos (no es Firebase Storage); guardar el PDF como texto base64 en un
nodo funciona bien para un documento de texto simple como este (pocos KB),
pero no es recomendable para archivos grandes (fotos, escaneos). Si más
adelante se necesita adjuntar ese tipo de archivos, conviene migrar a
Firebase Storage.

Cada método público devuelve un diccionario con el resultado (éxito/código/
mensaje/datos) para que la capa de UI decida qué mostrar (habilitar o no el
botón, abrir el archivo generado, listar comprobantes guardados, etc.).
"""

import base64
import os
from datetime import datetime

from fpdf import FPDF

from servidorSeguroUniversitario.configuracion.configuracionFirebase import obtenerReferencia

NODO_ESTUDIANTES = "estudiantes"
NODO_CONSULTAS_MEDICAS = "consultasMedicas"
NODO_COMPROBANTES_MEDICOS = "comprobantesMedicos"

FORMATO_FECHA = "%Y-%m-%d"

CARPETA_COMPROBANTES_POR_DEFECTO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "comprobantesGenerados",
)

CODIGO_MATRICULA_INEXISTENTE = "MATRICULA_INEXISTENTE"
CODIGO_SIN_CONSULTA_PREVIA = "SIN_CONSULTA_PREVIA"
CODIGO_CONSULTA_PREVIA_ENCONTRADA = "CONSULTA_PREVIA_ENCONTRADA"
CODIGO_CONSULTA_NO_VALIDA = "CONSULTA_NO_VALIDA"
CODIGO_COMPROBANTE_GENERADO = "COMPROBANTE_GENERADO"
CODIGO_COMPROBANTE_NO_ENCONTRADO = "COMPROBANTE_NO_ENCONTRADO"
CODIGO_ERROR_INESPERADO = "ERROR_INESPERADO"


class servicioComprobante:
    """Encapsula la validación de descarga, la generación del PDF y su guardado en el perfil (DB)."""

    def __init__(self, carpetaComprobantes=None):
        self.referenciaEstudiantes = obtenerReferencia(NODO_ESTUDIANTES)
        self.referenciaConsultasMedicas = obtenerReferencia(NODO_CONSULTAS_MEDICAS)
        self.referenciaComprobantesMedicos = obtenerReferencia(NODO_COMPROBANTES_MEDICOS)
        self.carpetaComprobantes = carpetaComprobantes or CARPETA_COMPROBANTES_POR_DEFECTO

    # ------------------------------------------------------------------
    # Consultas internas
    # ------------------------------------------------------------------
    def _obtenerConsultasDelEstudiante(self, matricula):
        """Todas las consultas registradas de esa matrícula (sin filtrar por fecha)."""
        resultados = (
            self.referenciaConsultasMedicas.order_by_child("matricula")
            .equal_to(matricula)
            .get()
        )
        return resultados or {}

    def _obtenerConsultasPrevias(self, matricula, fechaReferencia=None):
        """
        Consultas de esa matrícula con fechaConsulta <= fechaReferencia
        (por defecto, la fecha de hoy). Se devuelven ordenadas de la más
        reciente a la más antigua.
        """
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

    # ------------------------------------------------------------------
    # Operaciones públicas
    # ------------------------------------------------------------------
    def habilitarBotonDescarga(self, matricula, fechaReferencia=None):
        """
        Determina si el botón de descarga debe estar habilitado para esta
        matrícula (criterio de aceptación 3).
        """
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
        """Lista completa de consultas de un estudiante (para una futura vista de atenciones)."""
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
        """
        Genera el PDF descargable con el nombre del estudiante y la fecha de
        la atención (criterio de aceptación 2), siempre que exista al menos
        una consulta previa válida (criterio de aceptación 3), y lo guarda
        en el perfil del estudiante en la base de datos (nodo
        "comprobantesMedicos"), además de dejarlo en disco.

        matricula: matrícula del estudiante.
        idConsulta: opcional. Si no se indica, se usa la consulta previa más
            reciente. Si se indica, debe ser una consulta previa válida de
            ese mismo estudiante.
        """
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
        """
        Lista los comprobantes ya guardados en el perfil del estudiante
        (metadatos únicamente, sin el contenido del PDF, para que la lista
        sea liviana). Pensado para la futura pantalla "mis comprobantes".
        """
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
        """
        Recupera un comprobante ya guardado en la DB (por su idConsulta) y lo
        vuelve a escribir como archivo PDF en disco. Sirve para volver a
        verlo/descargarlo sin depender de que siga existiendo el archivo
        local original (por ejemplo, en otra instalación de la app).
        """
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

    # ------------------------------------------------------------------
    # Generación del archivo y guardado en el perfil (DB)
    # ------------------------------------------------------------------
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
        pdf.set_font("Helvetica", "I", 9)
        fechaGeneracion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf.cell(0, 6, f"Comprobante generado el {fechaGeneracion}.", ln=True)

        contenidoPdf = bytes(pdf.output())
        with open(rutaArchivo, "wb") as archivoPdf:
            archivoPdf.write(contenidoPdf)

        return nombreArchivo, rutaArchivo, contenidoPdf

    def _guardarComprobanteEnPerfil(self, idConsulta, datosConsulta, nombreArchivo, contenidoPdf):
        """Guarda el PDF (en base64) y sus metadatos en comprobantesMedicos/{idConsulta}."""
        registro = {
            "matricula": datosConsulta.get("matricula", ""),
            "cedulaIdentidad": datosConsulta.get("cedulaIdentidad", ""),
            "nombreCompleto": datosConsulta.get("nombreCompleto", ""),
            "idConsulta": idConsulta,
            "nombreServicio": datosConsulta.get("nombreServicio", ""),
            "fechaConsulta": datosConsulta.get("fechaConsulta", ""),
            "fechaGeneracion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nombreArchivo": nombreArchivo,
            "contenidoBase64": base64.b64encode(contenidoPdf).decode("ascii"),
        }
        self.referenciaComprobantesMedicos.child(idConsulta).set(registro)
