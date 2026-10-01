from servidorSeguroUniversitario.configuracion.configuracionFirebase import obtenerReferencia

# ----------------------------------------------------------------------
# Estudiantes
# ----------------------------------------------------------------------
ESTUDIANTES_DE_PRUEBA = {
    "20231001": {
        "cedulaIdentidad": "9876543",
        "nombreCompleto": "Maria Fernanda Rojas",
        "carrera": "Ingenieria de Sistemas",
        "tieneSeguroActivo": False,
    },
    "20231002": {
        "cedulaIdentidad": "1122334",
        "nombreCompleto": "Juan Pablo Quispe",
        "carrera": "Medicina",
        # Su seguro del periodo 2026-1 ya venció; pasa a True al renovar.
        "tieneSeguroActivo": False,
    },
    "20231003": {
        "cedulaIdentidad": "5566778",
        "nombreCompleto": "Ana Lucia Mamani",
        "carrera": "Derecho",
        "tieneSeguroActivo": False,
    },
    "20231004": {
        "cedulaIdentidad": "3344556",
        "nombreCompleto": "Carlos Andres Villca",
        "carrera": "Arquitectura",
        "tieneSeguroActivo": True,
    },
    "20231005": {
        "cedulaIdentidad": "7788990",
        "nombreCompleto": "Lucia Valeria Choque",
        "carrera": "Enfermeria",
        "tieneSeguroActivo": False,
    },
}


# ----------------------------------------------------------------------
# Afiliados
# ----------------------------------------------------------------------
AFILIADOS_DE_PRUEBA = [
    {
        "matricula": "20231002",
        "cedulaIdentidad": "1122334",
        "nombreCompleto": "Juan Pablo Quispe",
        "carrera": "Medicina",
        "correoElectronico": "juan.quispe@uni.edu.bo",
        "telefono": "70099887",
        "direccion": "Calle Comercio #456",
        "fechaNacimiento": "2000-11-02",
        "fechaAfiliacion": "2026-01-15 09:10:00",
        "estado": "activo",
    },
    {
        "matricula": "20231003",
        "cedulaIdentidad": "5566778",
        "nombreCompleto": "Ana Lucia Mamani",
        "carrera": "Derecho",
        "correoElectronico": "ana.mamani@uni.edu.bo",
        "telefono": "70011223",
        "direccion": "Zona Sopocachi, calle 10",
        "fechaNacimiento": "1999-03-21",
        "fechaAfiliacion": "2024-08-01 08:00:00",
        "estado": "inactivo",
    },
    {
        "matricula": "20231004",
        "cedulaIdentidad": "3344556",
        "nombreCompleto": "Carlos Andres Villca",
        "carrera": "Arquitectura",
        "correoElectronico": "carlos.villca@uni.edu.bo",
        "telefono": "70155667",
        "direccion": "Av. Arce #1020",
        "fechaNacimiento": "2001-05-14",
        "fechaAfiliacion": "2026-01-20 10:30:00",
        "estado": "activo",
    },
    {
        "matricula": "20231005",
        "cedulaIdentidad": "7788990",
        "nombreCompleto": "Lucia Valeria Choque",
        "carrera": "Enfermeria",
        "correoElectronico": "lucia.choque@uni.edu.bo",
        "telefono": "70233445",
        "direccion": "Calle Murillo #88",
        "fechaNacimiento": "2002-09-30",
        "fechaAfiliacion": "2026-02-03 11:15:00",
        "estado": "activo",
    },
]


# ----------------------------------------------------------------------
# Periodos académicos (el id es la clave del nodo)
# El periodo vigente se determina comparando la fecha de hoy con
# fechaInicio y fechaFin.
# ----------------------------------------------------------------------
PERIODOS_ACADEMICOS_DE_PRUEBA = {
    "2026-1": {
        "nombre": "Primer semestre 2026",
        "fechaInicio": "2026-02-01",
        "fechaFin": "2026-06-30",
    },
    "2026-2": {
        "nombre": "Segundo semestre 2026",
        "fechaInicio": "2026-08-01",
        "fechaFin": "2026-12-15",
    },
    "2027-1": {
        "nombre": "Primer semestre 2027",
        "fechaInicio": "2027-02-01",
        "fechaFin": "2027-06-30",
    },
}


# ----------------------------------------------------------------------
# Matriculaciones (clave: "<matricula>_<idPeriodo>")
# ----------------------------------------------------------------------
MATRICULACIONES_DE_PRUEBA = {
    # Maria: matriculada, pero sin afiliación -> SIN_AFILIACION_ACTIVA
    "20231001_2026-2": {
        "matricula": "20231001",
        "idPeriodo": "2026-2",
        "estado": "matriculado",
        "fechaMatriculacion": "2026-07-25",
    },
    # Juan: afiliado activo, matriculado, seguro vencido -> puede renovar
    "20231002_2026-1": {
        "matricula": "20231002",
        "idPeriodo": "2026-1",
        "estado": "matriculado",
        "fechaMatriculacion": "2026-01-20",
    },
    "20231002_2026-2": {
        "matricula": "20231002",
        "idPeriodo": "2026-2",
        "estado": "matriculado",
        "fechaMatriculacion": "2026-07-26",
    },
    # Ana: matriculada, pero su afiliación está inactiva -> SIN_AFILIACION_ACTIVA
    "20231003_2026-2": {
        "matricula": "20231003",
        "idPeriodo": "2026-2",
        "estado": "matriculado",
        "fechaMatriculacion": "2026-07-28",
    },
    # Carlos: matriculado y ya renovado para 2026-2 -> YA_RENOVADO_EN_PERIODO
    "20231004_2026-2": {
        "matricula": "20231004",
        "idPeriodo": "2026-2",
        "estado": "matriculado",
        "fechaMatriculacion": "2026-07-27",
    },
    # Lucia: afiliada activa pero retirada del periodo -> NO_MATRICULADO_EN_PERIODO
    "20231005_2026-1": {
        "matricula": "20231005",
        "idPeriodo": "2026-1",
        "estado": "matriculado",
        "fechaMatriculacion": "2026-02-02",
    },
    "20231005_2026-2": {
        "matricula": "20231005",
        "idPeriodo": "2026-2",
        "estado": "retirado",
        "fechaMatriculacion": "2026-07-29",
    },
}


# ----------------------------------------------------------------------
# Seguros (clave: matrícula)
# Maria y Ana no tienen registro -> "Sin vigencia registrada".
# ----------------------------------------------------------------------
SEGUROS_DE_PRUEBA = {
    # Vencido (terminó el periodo 2026-1)
    "20231002": {
        "matricula": "20231002",
        "idPeriodo": "2026-1",
        "fechaInicioVigencia": "2026-02-01",
        "fechaFinVigencia": "2026-06-30",
        "fechaUltimaRenovacion": "2026-01-22 10:00:00",
    },
    # Vigente (ya renovado para 2026-2)
    "20231004": {
        "matricula": "20231004",
        "idPeriodo": "2026-2",
        "fechaInicioVigencia": "2026-08-01",
        "fechaFinVigencia": "2026-12-15",
        "fechaUltimaRenovacion": "2026-08-03 09:45:00",
    },
    # Vencido (terminó el periodo 2026-1)
    "20231005": {
        "matricula": "20231005",
        "idPeriodo": "2026-1",
        "fechaInicioVigencia": "2026-02-01",
        "fechaFinVigencia": "2026-06-30",
        "fechaUltimaRenovacion": "2026-02-04 12:00:00",
    },
}


# ----------------------------------------------------------------------
# Historial de renovaciones (clave: "<matricula>_<idPeriodo>")
# ----------------------------------------------------------------------
RENOVACIONES_DE_PRUEBA = {
    "20231002_2026-1": {
        "matricula": "20231002",
        "nombreCompleto": "Juan Pablo Quispe",
        "idPeriodo": "2026-1",
        "fechaVigenciaAnterior": "",
        "fechaVigenciaNueva": "2026-06-30",
        "fechaRenovacion": "2026-01-22 10:00:00",
    },
    "20231004_2026-2": {
        "matricula": "20231004",
        "nombreCompleto": "Carlos Andres Villca",
        "idPeriodo": "2026-2",
        "fechaVigenciaAnterior": "2026-06-30",
        "fechaVigenciaNueva": "2026-12-15",
        "fechaRenovacion": "2026-08-03 09:45:00",
    },
    "20231005_2026-1": {
        "matricula": "20231005",
        "nombreCompleto": "Lucia Valeria Choque",
        "idPeriodo": "2026-1",
        "fechaVigenciaAnterior": "",
        "fechaVigenciaNueva": "2026-06-30",
        "fechaRenovacion": "2026-02-04 12:00:00",
    },
}


# ----------------------------------------------------------------------
# Servicios médicos
# ----------------------------------------------------------------------
SERVICIOS_MEDICOS_DE_PRUEBA = {
    "consultaMedicaGeneral": {
        "nombreServicio": "Consulta médica general",
        "categoria": "Consulta",
        "descripcion": "Consulta con médico general en las instalaciones universitarias.",
        "cubierto": True,
    },
    "emergenciasMedicas": {
        "nombreServicio": "Atención de emergencias",
        "categoria": "Emergencia",
        "descripcion": "Atención inmediata ante una emergencia médica.",
        "cubierto": True,
    },
    "laboratorioClinico": {
        "nombreServicio": "Exámenes de laboratorio",
        "categoria": "Laboratorio",
        "descripcion": "Análisis clínicos básicos (sangre, orina, etc.).",
        "cubierto": True,
    },
    "hospitalizacion": {
        "nombreServicio": "Hospitalización",
        "categoria": "Internación",
        "descripcion": "Internación en centro de salud afiliado al convenio.",
        "cubierto": True,
    },
    "odontologia": {
        "nombreServicio": "Atención odontológica",
        "categoria": "Odontología",
        "descripcion": "No incluido en el plan básico del seguro universitario.",
        "cubierto": False,
    },
    "oftalmologia": {
        "nombreServicio": "Consulta oftalmológica",
        "categoria": "Consulta especializada",
        "descripcion": "No incluido en el plan básico del seguro universitario.",
        "cubierto": False,
    },
    "fisioterapia": {
        "nombreServicio": "Sesiones de fisioterapia",
        "categoria": "Rehabilitación",
        "descripcion": "No incluido en el plan básico del seguro universitario.",
        "cubierto": False,
    },
}


# ----------------------------------------------------------------------
# Consultas médicas
# ----------------------------------------------------------------------
CONSULTAS_MEDICAS_DE_PRUEBA = [
    {
        "matricula": "20231001",
        "cedulaIdentidad": "9876543",
        "nombreCompleto": "Maria Fernanda Rojas",
        "idServicioMedico": "consultaMedicaGeneral",
        "nombreServicio": "Consulta médica general",
        "fechaConsulta": "2026-08-10",
        "horaConsulta": "09:30",
        "medicoTratante": "Dr. Carlos Fernandez",
        "observaciones": "Control rutinario.",
    },
    {
        "matricula": "20231001",
        "cedulaIdentidad": "9876543",
        "nombreCompleto": "Maria Fernanda Rojas",
        "idServicioMedico": "laboratorioClinico",
        "nombreServicio": "Exámenes de laboratorio",
        "fechaConsulta": "2026-09-15",
        "horaConsulta": "11:00",
        "medicoTratante": "Dra. Lucia Perez",
        "observaciones": "Examenes de rutina, resultados normales.",
    },
    {
        "matricula": "20231002",
        "cedulaIdentidad": "1122334",
        "nombreCompleto": "Juan Pablo Quispe",
        "idServicioMedico": "consultaMedicaGeneral",
        "nombreServicio": "Consulta médica general",
        "fechaConsulta": "2026-12-01",
        "horaConsulta": "10:00",
        "medicoTratante": "Dr. Carlos Fernandez",
        "observaciones": "Consulta programada (fecha futura), a propósito para pruebas.",
    },
]


# ----------------------------------------------------------------------
# Comprobantes / justificativos médicos (clave: idConsulta)
# Simulan justificativos ya generados antes (HU 17), para probar el
# historial (HU 11). Fechas desordenadas a propósito, para comprobar que
# el servicio las ordena de la más reciente a la más antigua.
# ----------------------------------------------------------------------
COMPROBANTES_MEDICOS_DE_PRUEBA = {
    "consultaPrueba001": {
        "matricula": "20231001",
        "cedulaIdentidad": "9876543",
        "nombreCompleto": "Maria Fernanda Rojas",
        "idConsulta": "consultaPrueba001",
        "nombreServicio": "Consulta médica general",
        "medicoTratante": "Dr. Carlos Fernandez",
        "fechaConsulta": "2026-08-10",
        "fechaGeneracion": "2026-08-10 12:00:00",
        "nombreArchivo": "comprobante_20231001_consultaPrueba001.pdf",
        "contenidoBase64": "",
    },
    "consultaPrueba002": {
        "matricula": "20231001",
        "cedulaIdentidad": "9876543",
        "nombreCompleto": "Maria Fernanda Rojas",
        "idConsulta": "consultaPrueba002",
        "nombreServicio": "Exámenes de laboratorio",
        "medicoTratante": "Dra. Lucia Perez",
        "fechaConsulta": "2026-09-15",
        "fechaGeneracion": "2026-09-15 13:20:00",
        "nombreArchivo": "comprobante_20231001_consultaPrueba002.pdf",
        "contenidoBase64": "",
    },
    "consultaPrueba003": {
        "matricula": "20231001",
        "cedulaIdentidad": "9876543",
        "nombreCompleto": "Maria Fernanda Rojas",
        "idConsulta": "consultaPrueba003",
        "nombreServicio": "Atención de emergencias",
        "medicoTratante": "Dr. Ramiro Salinas",
        "fechaConsulta": "2026-06-02",
        "fechaGeneracion": "2026-06-02 08:45:00",
        "nombreArchivo": "comprobante_20231001_consultaPrueba003.pdf",
        "contenidoBase64": "",
    },
    "consultaPrueba004": {
        "matricula": "20231002",
        "cedulaIdentidad": "1122334",
        "nombreCompleto": "Juan Pablo Quispe",
        "idConsulta": "consultaPrueba004",
        "nombreServicio": "Consulta médica general",
        "medicoTratante": "Dr. Carlos Fernandez",
        "fechaConsulta": "2026-03-05",
        "fechaGeneracion": "2026-03-05 09:00:00",
        "nombreArchivo": "comprobante_20231002_consultaPrueba004.pdf",
        "contenidoBase64": "",
    },
}
# Orden esperado del historial de 20231001: 2026-09-15, 2026-08-10, 2026-06-02.


# ----------------------------------------------------------------------
# Funciones de siembra
# ----------------------------------------------------------------------
def sembrarEstudiantesDePrueba():
    referenciaEstudiantes = obtenerReferencia("estudiantes")
    referenciaEstudiantes.update(ESTUDIANTES_DE_PRUEBA)
    print("Datos de prueba insertados en el nodo 'estudiantes'.")


def sembrarAfiliadosDePrueba():
    referenciaAfiliados = obtenerReferencia("afiliados")
    for afiliado in AFILIADOS_DE_PRUEBA:
        referenciaAfiliados.push(afiliado)
    print("Datos de prueba insertados en el nodo 'afiliados'.")


def sembrarPeriodosAcademicosDePrueba():
    referenciaPeriodos = obtenerReferencia("periodosAcademicos")
    referenciaPeriodos.update(PERIODOS_ACADEMICOS_DE_PRUEBA)
    print("Datos de prueba insertados en el nodo 'periodosAcademicos'.")


def sembrarMatriculacionesDePrueba():
    referenciaMatriculaciones = obtenerReferencia("matriculaciones")
    referenciaMatriculaciones.update(MATRICULACIONES_DE_PRUEBA)
    print("Datos de prueba insertados en el nodo 'matriculaciones'.")


def sembrarSegurosDePrueba():
    referenciaSeguros = obtenerReferencia("seguros")
    referenciaSeguros.update(SEGUROS_DE_PRUEBA)
    print("Datos de prueba insertados en el nodo 'seguros'.")


def sembrarRenovacionesDePrueba():
    referenciaRenovaciones = obtenerReferencia("renovaciones")
    referenciaRenovaciones.update(RENOVACIONES_DE_PRUEBA)
    print("Datos de prueba insertados en el nodo 'renovaciones'.")


def sembrarServiciosMedicosDePrueba():
    referenciaServiciosMedicos = obtenerReferencia("serviciosMedicos")
    referenciaServiciosMedicos.update(SERVICIOS_MEDICOS_DE_PRUEBA)
    print("Datos de prueba insertados en el nodo 'serviciosMedicos'.")


def sembrarConsultasMedicasDePrueba():
    referenciaConsultasMedicas = obtenerReferencia("consultasMedicas")
    for consulta in CONSULTAS_MEDICAS_DE_PRUEBA:
        referenciaConsultasMedicas.push(consulta)
    print("Datos de prueba insertados en el nodo 'consultasMedicas'.")


def sembrarComprobantesMedicosDePrueba():
    referenciaComprobantesMedicos = obtenerReferencia("comprobantesMedicos")
    referenciaComprobantesMedicos.update(COMPROBANTES_MEDICOS_DE_PRUEBA)
    print("Datos de prueba insertados en el nodo 'comprobantesMedicos'.")


def sembrarDatosDePrueba():
    sembrarEstudiantesDePrueba()
    sembrarAfiliadosDePrueba()
    sembrarPeriodosAcademicosDePrueba()
    sembrarMatriculacionesDePrueba()
    sembrarSegurosDePrueba()
    sembrarRenovacionesDePrueba()
    sembrarServiciosMedicosDePrueba()
    sembrarConsultasMedicasDePrueba()
    sembrarComprobantesMedicosDePrueba()


if __name__ == "__main__":
    sembrarDatosDePrueba()