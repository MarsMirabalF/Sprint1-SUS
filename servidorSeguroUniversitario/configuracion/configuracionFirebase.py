import os
import sys

import firebase_admin
from firebase_admin import credentials, db

NOMBRE_ARCHIVO_CREDENCIALES = "credencialesFirebase.json"
VARIABLE_ENTORNO_CREDENCIALES = "FIREBASE_CREDENCIALES"
VARIABLE_ENTORNO_URL = "FIREBASE_URL_BASE_DATOS"

URL_BASE_DATOS = "https://seguro-universitario-db-default-rtdb.firebaseio.com/"

URL_NO_CONFIGURADA = "NOMBRE-DEL-PROYECTO"


def _carpetaServicio():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    carpetaConfiguracion = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(carpetaConfiguracion)


def obtenerRutaCredenciales():
    rutaPersonalizada = os.getenv(VARIABLE_ENTORNO_CREDENCIALES)
    if rutaPersonalizada:
        return rutaPersonalizada

    return os.path.join(_carpetaServicio(), "credenciales", NOMBRE_ARCHIVO_CREDENCIALES)


def obtenerUrlBaseDatos():
    urlPersonalizada = os.getenv(VARIABLE_ENTORNO_URL)
    if urlPersonalizada:
        return urlPersonalizada

    return URL_BASE_DATOS


def inicializarFirebase():
    if not firebase_admin._apps:
        rutaCredenciales = obtenerRutaCredenciales()
        urlBaseDatos = obtenerUrlBaseDatos()

        if not os.path.exists(rutaCredenciales):
            raise FileNotFoundError(
                "No se encontro el archivo de credenciales en: "
                f"{rutaCredenciales}\n\n"
                "Descargue la clave privada desde la consola de Firebase "
                "(Configuracion del proyecto -> Cuentas de servicio) y "
                f"guardela con el nombre {NOMBRE_ARCHIVO_CREDENCIALES} en "
                "esa carpeta (servidorSeguroUniversitario/credenciales/)."
            )

        if URL_NO_CONFIGURADA in urlBaseDatos:
            raise ValueError(
                "La URL de la Realtime Database no esta configurada. "
                "Edite URL_BASE_DATOS en configuracionFirebase.py o defina "
                f"la variable de entorno {VARIABLE_ENTORNO_URL}."
            )

        credencial = credentials.Certificate(rutaCredenciales)
        firebase_admin.initialize_app(credencial, {"databaseURL": urlBaseDatos})

    return db.reference("/")


def obtenerReferencia(nodo):
    inicializarFirebase()
    return db.reference(nodo)