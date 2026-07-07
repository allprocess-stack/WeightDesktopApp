import sys

from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    wnd = MainWindow()
    wnd.show()

    wnd.enumerar_puertos()
    config = wnd.cargar_configuracion()
    if config is not None:
        wnd.iniciar_reconexion()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
