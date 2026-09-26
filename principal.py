"""Punto de entrada de la aplicación."""

import sys

from clienteSeguroUniversitario.interfaz.formularioAfiliacion import formularioAfiliacion


def principal():
    try:
        from tkinter import Tk

        ventanaPrincipal = Tk()
        formularioAfiliacion(ventanaPrincipal)
        ventanaPrincipal.mainloop()
    except Exception as error:
        print(f"Error inesperado al iniciar la aplicación: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    principal()
