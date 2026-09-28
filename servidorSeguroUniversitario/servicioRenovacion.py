"""
servicioRenovacion.py

HU 10 — Renovación del seguro universitario.

Servicio de backend (sin UI) responsable de:
    1. Renovar el seguro de un estudiante recibiendo SOLO su matrícula (los
       datos personales se toman de su afiliación ya registrada, no se
       vuelven a pedir).
    2. Validar que el estudiante figure como matriculado en el periodo
       académico vigente antes de aprobar la renovación.
    3. Registrar la nueva vigencia del seguro y dejar constancia de la
       renovación.
    4. Consultar el estado de vigencia del seguro (para el perfil y el
       carnet digital).

Reglas de negocio aplicadas:
    - Debe existir una afiliación activa (HU 6) para poder renovar.
    - Debe existir un periodo académico vigente (hoy dentro de su rango).
    - El estudiante debe estar "matriculado" en ese periodo.
    - No se puede renovar dos veces para el mismo periodo.
    - La nueva vigencia va desde el inicio hasta el fin del periodo vigente.

Cada método público devuelve un diccionario con el resultado (éxito/código/
mensaje/datos) para que la capa de UI decida qué mostrar.
"""

from datetime import datetime

from servidorSeguroUniversitario.configuracion.configuracionFirebase import obtenerReferencia

NODO_RAIZ = "/"
NODO_ESTUDIANTES = "estudiantes"
NODO_AFILIADOS = "afiliados"
NODO_PERIODOS_ACADEMICOS = "periodosAcademicos"
NODO_MATRICULACIONES = "matriculaciones"
NODO_SEGUROS = "seguros"
NODO_RENOVACIONES = "renovaciones"

FORMATO_FECHA = "%Y-%m-%d"
FORMATO_FECHA_HORA = "%Y-%m-%d %H:%M:%S"

ESTADO_AFILIADO_ACTIVO = "activo"
ESTADO_MATRICULADO = "matriculado"

ESTADO_VIGENTE = "Vigente"
ESTADO_VENCIDO = "Vencido"
ESTADO_SIN_SEGURO_REGISTRADO = "Sin vigencia registrada"

CODIGO_MATRICULA_NO_ESPECIFICADA = "MATRICULA_NO_ESPECIFICADA"
CODIGO_MATRICULA_INEXISTENTE = "MATRICULA_INEXISTENTE"
CODIGO_SIN_AFILIACION_ACTIVA = "SIN_AFILIACION_ACTIVA"
CODIGO_PERIODO_NO_VIGENTE = "PERIODO_NO_VIGENTE"
CODIGO_NO_MATRICULADO_EN_PERIODO = "NO_MATRICULADO_EN_PERIODO"
CODIGO_YA_RENOVADO_EN_PERIODO = "YA_RENOVADO_EN_PERIODO"
CODIGO_RENOVACION_EXITOSA = "RENOVACION_EXITOSA"
CODIGO_ESTADO_SEGURO_OBTENIDO = "ESTADO_SEGURO_OBTENIDO"
CODIGO_ERROR_INESPERADO = "ERROR_INESPERADO"


class servicioRenovacion:
    """Encapsula las reglas y el acceso a datos de la renovación del seguro."""

    def __init__(self):
        self.referenciaRaiz = obtenerReferencia(NODO_RAIZ)
        self.referenciaEstudiantes = obtenerReferencia(NODO_ESTUDIANTES)
        self.referenciaAfiliados = obtenerReferencia(NODO_AFILIADOS)
        self.referenciaPeriodosAcademicos = obtenerReferencia(NODO_PERIODOS_ACADEMICOS)
        self.referenciaMatriculaciones = obtenerReferencia(NODO_MATRICULACIONES)
        self.referenciaSeguros = obtenerReferencia(NODO_SEGUROS)

    # ------------------------------------------------------------------
    # Consultas internas
    # ------------------------------------------------------------------
    def _obtenerPeriodoVigente(self, fechaHoy):
        """Devuelve (idPeriodo, datos) del periodo cuyo rango contiene fechaHoy, o (None, None)."""
        periodos = self.referenciaPeriodosAcademicos.get() or {}
        for idPeriodo, datos in periodos.items():
            if datos.get("fechaInicio", "") <= fechaHoy <= datos.get("fechaFin", ""):
                return idPeriodo, datos
        return None, None

    def _obtenerAfiliacionActiva(self, matricula):
        """Devuelve el registro de afiliación activo de esa matrícula, o None."""
        resultados = (
            self.referenciaAfiliados.order_by_child("matricula")
            .equal_to(matricula)
            .get()
        )
        for registro in (resultados or {}).values():
            if registro.get("estado") == ESTADO_AFILIADO_ACTIVO:
                return registro
        return None

    def _estaMatriculado(self, matricula, idPeriodo):
        registro = self.referenciaMatriculaciones.child(f"{matricula}_{idPeriodo}").get()
        return registro is not None and registro.get("estado") == ESTADO_MATRICULADO

    def _calcularEstadoVigencia(self, fechaFinVigencia, fechaHoy):
        if not fechaFinVigencia:
            return ESTADO_SIN_SEGURO_REGISTRADO
        return ESTADO_VIGENTE if fechaFinVigencia >= fechaHoy else ESTADO_VENCIDO

    def _validarMatricula(self, matricula):
        """Devuelve (matriculaLimpia, resultadoError). Si hay error, matriculaLimpia es None."""
        if not matricula or not str(matricula).strip():
            return None, {
                "exito": False,
                "codigo": CODIGO_MATRICULA_NO_ESPECIFICADA,
                "mensaje": "Debe indicar la matrícula del estudiante.",
            }
        matricula = str(matricula).strip()
        if self.referenciaEstudiantes.child(matricula).get() is None:
            return None, {
                "exito": False,
                "codigo": CODIGO_MATRICULA_INEXISTENTE,
                "mensaje": "La matrícula ingresada no existe en los registros de la universidad.",
            }
        return matricula, None

    # ------------------------------------------------------------------
    # Operaciones públicas
    # ------------------------------------------------------------------
    def consultarEstadoSeguro(self, matricula, fechaReferencia=None):
        """
        Devuelve la vigencia del seguro y su estado (Vigente / Vencido /
        Sin vigencia registrada). Sirve para el estado en el perfil y para
        mostrar la fecha de vigencia en el carnet digital.
        """
        try:
            matricula, error = self._validarMatricula(matricula)
            if error:
                return error

            fechaHoy = fechaReferencia or datetime.now().strftime(FORMATO_FECHA)
            seguro = self.referenciaSeguros.child(matricula).get() or {}
            fechaFin = seguro.get("fechaFinVigencia", "")

            return {
                "exito": True,
                "codigo": CODIGO_ESTADO_SEGURO_OBTENIDO,
                "mensaje": "Estado del seguro obtenido correctamente.",
                "matricula": matricula,
                "estadoVigencia": self._calcularEstadoVigencia(fechaFin, fechaHoy),
                "fechaInicioVigencia": seguro.get("fechaInicioVigencia", ""),
                "fechaFinVigencia": fechaFin,
                "fechaUltimaRenovacion": seguro.get("fechaUltimaRenovacion", ""),
            }

        except Exception as error:
            return {
                "exito": False,
                "codigo": CODIGO_ERROR_INESPERADO,
                "mensaje": f"Ocurrió un error inesperado al consultar el seguro: {error}",
            }

    def renovarSeguro(self, matricula, fechaReferencia=None):
        """
        Ejecuta la renovación del seguro. Solo necesita la matrícula.

        fechaReferencia: opcional ("YYYY-MM-DD"), para pruebas. Por defecto, hoy.
        """
        try:
            matricula, error = self._validarMatricula(matricula)
            if error:
                return error

            fechaHoy = fechaReferencia or datetime.now().strftime(FORMATO_FECHA)

            afiliacion = self._obtenerAfiliacionActiva(matricula)
            if afiliacion is None:
                return {
                    "exito": False,
                    "codigo": CODIGO_SIN_AFILIACION_ACTIVA,
                    "mensaje": "El estudiante no tiene una afiliación activa al seguro; debe afiliarse primero.",
                }

            idPeriodo, periodo = self._obtenerPeriodoVigente(fechaHoy)
            if periodo is None:
                return {
                    "exito": False,
                    "codigo": CODIGO_PERIODO_NO_VIGENTE,
                    "mensaje": "No hay un periodo académico vigente en este momento; no se puede renovar.",
                }

            if not self._estaMatriculado(matricula, idPeriodo):
                return {
                    "exito": False,
                    "codigo": CODIGO_NO_MATRICULADO_EN_PERIODO,
                    "mensaje": f"El estudiante no figura como matriculado en el periodo vigente ({idPeriodo}); la renovación fue rechazada.",
                    "idPeriodo": idPeriodo,
                }

            seguroActual = self.referenciaSeguros.child(matricula).get() or {}
            fechaFinAnterior = seguroActual.get("fechaFinVigencia", "")
            if fechaFinAnterior and fechaFinAnterior >= periodo["fechaFin"]:
                return {
                    "exito": False,
                    "codigo": CODIGO_YA_RENOVADO_EN_PERIODO,
                    "mensaje": f"El seguro ya fue renovado para el periodo {idPeriodo}.",
                    "idPeriodo": idPeriodo,
                    "fechaFinVigencia": fechaFinAnterior,
                }

            fechaRenovacion = datetime.now().strftime(FORMATO_FECHA_HORA)
            nuevoSeguro = {
                "matricula": matricula,
                "idPeriodo": idPeriodo,
                "fechaInicioVigencia": periodo["fechaInicio"],
                "fechaFinVigencia": periodo["fechaFin"],
                "fechaUltimaRenovacion": fechaRenovacion,
            }
            registroRenovacion = {
                "matricula": matricula,
                "nombreCompleto": afiliacion.get("nombreCompleto", ""),
                "idPeriodo": idPeriodo,
                "fechaVigenciaAnterior": fechaFinAnterior,
                "fechaVigenciaNueva": periodo["fechaFin"],
                "fechaRenovacion": fechaRenovacion,
            }

            # Escritura atómica en varios nodos a la vez: o se guarda todo o nada.
            self.referenciaRaiz.update(
                {
                    f"{NODO_SEGUROS}/{matricula}": nuevoSeguro,
                    f"{NODO_RENOVACIONES}/{matricula}_{idPeriodo}": registroRenovacion,
                    f"{NODO_ESTUDIANTES}/{matricula}/tieneSeguroActivo": True,
                }
            )

            return {
                "exito": True,
                "codigo": CODIGO_RENOVACION_EXITOSA,
                "mensaje": "La renovación del seguro se realizó con éxito.",
                "matricula": matricula,
                "nombreCompleto": afiliacion.get("nombreCompleto", ""),
                "idPeriodo": idPeriodo,
                "fechaInicioVigencia": periodo["fechaInicio"],
                "fechaFinVigencia": periodo["fechaFin"],
                "fechaRenovacion": fechaRenovacion,
                "estadoVigencia": ESTADO_VIGENTE,
            }

        except Exception as error:
            return {
                "exito": False,
                "codigo": CODIGO_ERROR_INESPERADO,
                "mensaje": f"Ocurrió un error inesperado al renovar el seguro: {error}",
            }
