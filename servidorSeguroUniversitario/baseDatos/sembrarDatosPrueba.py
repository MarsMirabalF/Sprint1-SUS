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
}

def sembrarEstudiantesDePrueba():
    referenciaEstudiantes = obtenerReferencia("estudiantes")
    referenciaEstudiantes.update(ESTUDIANTES_DE_PRUEBA)
    print("Datos de prueba insertados en el nodo 'estudiantes'.")

if __name__ == "__main__":
    sembrarEstudiantesDePrueba()