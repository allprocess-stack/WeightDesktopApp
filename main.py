import os
import sys

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow


def main():
    """Punto de entrada de la aplicación. Inicializa PyQt6, crea la ventana
    principal, carga la configuración guardada e inicia la reconexión automática."""

    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
        plugins = os.path.join(base, "PyQt6", "Qt6", "plugins")
        if os.path.isdir(plugins):
            QCoreApplication.addLibraryPath(plugins)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    wnd = MainWindow()
    wnd.show()

    wnd.enumerar_puertos()
    config = wnd.cargar_configuracion()
    if config is not None:
        wnd.iniciar_reconexion()

    app.aboutToQuit.connect(wnd.cerrar_conexion)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
