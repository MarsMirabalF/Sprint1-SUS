from servidorSeguroUniversitario.configuracion.configuracionFirebase import obtenerReferencia

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
        "tieneSeguroActivo": True,
    },
    "20231003": {
        "cedulaIdentidad": "5566778",
        "nombreCompleto": "Ana Lucia Mamani",
        "carrera": "Derecho",
        "tieneSeguroActivo": False,
    },
}


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
]


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


def sembrarEstudiantesDePrueba():
    referenciaEstudiantes = obtenerReferencia("estudiantes")
    referenciaEstudiantes.update(ESTUDIANTES_DE_PRUEBA)
    print("Datos de prueba insertados en el nodo 'estudiantes'.")


def sembrarAfiliadosDePrueba():
    referenciaAfiliados = obtenerReferencia("afiliados")
    for afiliado in AFILIADOS_DE_PRUEBA:
        referenciaAfiliados.push(afiliado)
    print("Datos de prueba insertados en el nodo 'afiliados'.")


def sembrarServiciosMedicosDePrueba():
    referenciaServiciosMedicos = obtenerReferencia("serviciosMedicos")
    referenciaServiciosMedicos.update(SERVICIOS_MEDICOS_DE_PRUEBA)
    print("Datos de prueba insertados en el nodo 'serviciosMedicos'.")


def sembrarDatosDePrueba():
    sembrarEstudiantesDePrueba()
    sembrarAfiliadosDePrueba()
    sembrarServiciosMedicosDePrueba()


if __name__ == "__main__":
    sembrarDatosDePrueba()
