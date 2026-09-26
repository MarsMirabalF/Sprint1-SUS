from servidorSeguroUniversitario.configuracion.configuracionFirebase import obtenerReferencia

NODO_SERVICIOS_MEDICOS = "serviciosMedicos"

ESTADO_CUBIERTO = "Cubierto"
ESTADO_NO_CUBIERTO = "No cubierto"

CODIGO_LISTA_OBTENIDA = "LISTA_OBTENIDA"
CODIGO_CATALOGO_VACIO = "CATALOGO_VACIO"
CODIGO_SERVICIO_NO_ESPECIFICADO = "SERVICIO_NO_ESPECIFICADO"
CODIGO_SERVICIO_INEXISTENTE = "SERVICIO_INEXISTENTE"
CODIGO_COBERTURA_OBTENIDA = "COBERTURA_OBTENIDA"
CODIGO_ERROR_INESPERADO = "ERROR_INESPERADO"


class servicioCobertura:

    def __init__(self):
        self.referenciaServiciosMedicos = obtenerReferencia(NODO_SERVICIOS_MEDICOS)

    def _calcularEstadoCobertura(self, cubierto):
        return ESTADO_CUBIERTO if cubierto is True else ESTADO_NO_CUBIERTO

    def _mapearRegistro(self, idServicio, datos):
        cubierto = datos.get("cubierto", False)
        return {
            "idServicio": idServicio,
            "nombreServicio": datos.get("nombreServicio", ""),
            "categoria": datos.get("categoria", ""),
            "descripcion": datos.get("descripcion", ""),
            "cubierto": cubierto,
            "estadoCobertura": self._calcularEstadoCobertura(cubierto),
        }

    def listarServiciosMedicos(self):
        try:
            registros = self.referenciaServiciosMedicos.get() or {}

            if not registros:
                return {
                    "exito": True,
                    "codigo": CODIGO_CATALOGO_VACIO,
                    "mensaje": "Aún no hay servicios médicos cargados en el catálogo.",
                    "servicios": [],
                }

            listaServicios = [
                self._mapearRegistro(idServicio, datos)
                for idServicio, datos in registros.items()
            ]

            return {
                "exito": True,
                "codigo": CODIGO_LISTA_OBTENIDA,
                "mensaje": f"Se encontraron {len(listaServicios)} servicios médicos.",
                "servicios": listaServicios,
            }

        except Exception as error:
            return {
                "exito": False,
                "codigo": CODIGO_ERROR_INESPERADO,
                "mensaje": f"Ocurrió un error inesperado al obtener el catálogo: {error}",
            }


