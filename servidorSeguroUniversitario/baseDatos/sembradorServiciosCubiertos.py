from servidorSeguroUniversitario.configuracion.configuracionFirebase import obtenerReferencia

SERVICIOS_DE_PRUEBA = {
    "consultaGeneral": {"nombre": "Consulta General", "estado": "cubierto"},
    "odontologia": {"nombre": "Odontología", "estado": "parcial"},
    "oftalmologia": {"nombre": "Oftalmología", "estado": "no cubierto"},
    "emergencias": {"nombre": "Emergencias", "estado": "cubierto"},
    "laboratorio": {"nombre": "Laboratorio clínico", "estado": "cubierto"},
}


def sembrarServiciosCubiertos():
    referencia = obtenerReferencia("serviciosCubiertos")
    referencia.update(SERVICIOS_DE_PRUEBA)
    print("Datos de prueba insertados en el nodo 'serviciosCubiertos'.")


if __name__ == "__main__":
    sembrarServiciosCubiertos()