import sys

from clienteSeguroUniversitario.interfaz.dashboard import dashboard
from clienteSeguroUniversitario.interfaz.login import login


def principal():
    try:
        from tkinter import Tk

        ventanaPrincipal = Tk()
        def abrirAplicacion(resultadoLogin):
            for widget in ventanaPrincipal.winfo_children():
                widget.destroy()
            dashboard(ventanaPrincipal, resultadoLogin)

        login(ventanaPrincipal, alAutenticar=abrirAplicacion)
        ventanaPrincipal.mainloop()
    except Exception as error:
        print(f"Error inesperado al iniciar la aplicación: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    principal()
