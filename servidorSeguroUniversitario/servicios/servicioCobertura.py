from servidorSeguroUniversitario.configuracion.configuracionFirebase import obtenerReferencia

NODO_SERVICIOS_CUBIERTOS = "serviciosCubiertos"


class servicioCobertura:

    def __init__(self):
        self.referenciaServicios = obtenerReferencia(NODO_SERVICIOS_CUBIERTOS)

    def obtenerServiciosCubiertos(self):
        datos = self.referenciaServicios.get()
        if not datos:
            return []

        servicios = []
        for clave, valor in datos.items():
            if not isinstance(valor, dict):
                continue
            servicios.append(
                {
                    "clave": clave,
                    "nombre": valor.get("nombre", clave),
                    "estado": valor.get("estado", ""),
                }
            )

        servicios.sort(key=lambda servicio: servicio["nombre"])
        return servicios