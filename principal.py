"""Punto de entrada de la aplicación este es el archivo que se ejecuta para
correr todo el sistema """

import sys


def principal():
    try:
        print("clienteSeguroUniversitario aún no tiene una ventana principal implementada.")
        print("El backend (servidorSeguroUniversitario) ya está listo para ser usado.")
    except Exception as error:
        print(f"Error inesperado al iniciar la aplicación: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    principal()