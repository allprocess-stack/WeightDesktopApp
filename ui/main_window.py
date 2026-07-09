from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QMessageBox,
)

from config.config_manager import ConfigManager
from core.serial_connection import SerialConnection
from core.trama_parser import TramaParser
from ui.login_dialog import LoginDialog


class PortOpener(QThread):
    resultado = pyqtSignal(object, str)

    def __init__(self, puerto: str, callback):
        super().__init__()
        self.puerto = puerto
        self.callback = callback

    def run(self):
        conn = SerialConnection(self.callback)
        conn.resetear_puerto(self.puerto)
        try:
            conn.abrir(self.puerto, reintentar=True)
            self.resultado.emit(conn, "")
        except Exception as e:
            conn.cerrar()
            self.resultado.emit(None, str(e))


class MainWindow(QMainWindow):
    peso_listo = pyqtSignal()

    TIPOS_TRAMA = ["XKR", "XK310", "FT11", "Generic"]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DesktopViewWeight")
        self.setGeometry(0, 0, 800, 450)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: black;")

        self._parser = TramaParser()
        self._connection: SerialConnection | None = None
        self._reintentos_apertura = 0
        self._trama_cambiada = False
        self._abriendo = False

        self.peso_listo.connect(self._actualizar_peso)

        self._init_ui()
        self._init_watchdog()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self._peso_label = QLabel("-----")
        self._peso_label.setFixedSize(256, 128)
        self._peso_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._fuente_original = QFont("Segoe UI", 48, QFont.Weight.Bold)
        self._peso_label.setFont(self._fuente_original)
        self._peso_label.setStyleSheet(
            "color: #FF4500; background-color: black; border: none;"
        )
        layout.addWidget(
            self._peso_label,
            alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
        )

        layout.addStretch()

        self._status_bar = QStatusBar()
        self._status_bar.setStyleSheet(
            "QStatusBar { background: #1e1e1e; color: white; }"
            "QStatusBar::item { border: none; }"
        )
        self.setStatusBar(self._status_bar)

        self._btn_login = QPushButton("[Login]")
        self._btn_login.setStyleSheet(
            "QPushButton { background: #333; color: white; padding: 4px 10px; }"
        )
        self._btn_login.clicked.connect(self._on_login)
        self._status_bar.addWidget(self._btn_login)

        self._config_widget = QWidget()
        config_layout = QHBoxLayout(self._config_widget)
        config_layout.setContentsMargins(0, 0, 0, 0)

        self._cbx_tramas = QComboBox()
        self._cbx_tramas.addItems(self.TIPOS_TRAMA)
        self._cbx_tramas.currentTextChanged.connect(self._on_trama_changed)
        self._estilizar_combo(self._cbx_tramas)

        self._cbx_com = QComboBox()
        self._cbx_com.setMinimumWidth(100)
        self._cbx_com.currentTextChanged.connect(self._on_com_changed)
        self._estilizar_combo(self._cbx_com)

        self._btn_abrir = QPushButton("Abrir")
        self._btn_abrir.clicked.connect(self._on_abrir)
        self._estilizar_boton(self._btn_abrir)

        self._btn_cerrar = QPushButton("Cerrar")
        self._btn_cerrar.clicked.connect(self._on_cerrar)
        self._estilizar_boton(self._btn_cerrar)

        self._btn_guardar = QPushButton("Guardar Config")
        self._btn_guardar.clicked.connect(self._on_guardar_config)
        self._estilizar_boton(self._btn_guardar)

        config_layout.addWidget(QLabel("Trama:"))
        config_layout.addWidget(self._cbx_tramas)
        config_layout.addWidget(QLabel("COM:"))
        config_layout.addWidget(self._cbx_com)
        config_layout.addWidget(self._btn_abrir)
        config_layout.addWidget(self._btn_cerrar)
        config_layout.addWidget(self._btn_guardar)

        self._status_bar.addWidget(self._config_widget)
        self._config_widget.setVisible(False)

        self._lbl_conexion = QLabel("Desconectado")
        self._lbl_conexion.setStyleSheet("color: #FF4444; padding: 2px 8px;")
        self._status_bar.addPermanentWidget(self._lbl_conexion)

        self._lbl_trama = QLabel("Trama: ---")
        self._lbl_trama.setStyleSheet("color: #888888; padding: 2px 8px;")
        self._status_bar.addPermanentWidget(self._lbl_trama)

        self._btn_cerrar_app = QPushButton("Cerrar App")
        self._btn_cerrar_app.clicked.connect(self._on_cerrar_app)
        self._estilizar_boton(self._btn_cerrar_app)
        self._status_bar.addPermanentWidget(self._btn_cerrar_app)

    def _estilizar_combo(self, combo: QComboBox):
        combo.setStyleSheet(
            "QComboBox { background: #333; color: white; border: 1px solid #555; "
            "padding: 2px 4px; }"
            "QComboBox QAbstractItemView { background: #333; color: white; "
            "selection-background-color: #555; }"
        )

    def _estilizar_boton(self, btn: QPushButton):
        btn.setStyleSheet(
            "QPushButton { background: #333; color: white; border: 1px solid #555; "
            "padding: 4px 8px; }"
            "QPushButton:hover { background: #444; }"
        )

    def _on_login(self):
        dialog = LoginDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            user, password = dialog.credenciales()
            if user == "root" and password == "systemconfig":
                self._config_widget.setVisible(True)
                self.enumerar_puertos()
                QMessageBox.information(
                    self, "Acceso concedido",
                    "Menú de configuración habilitado."
                )
            else:
                QMessageBox.critical(
                    self, "Acceso denegado",
                    "Usuario o contraseña incorrectos."
                )

    def enumerar_puertos(self):
        seleccionado = self._cbx_com.currentText()
        self._cbx_com.blockSignals(True)
        self._cbx_com.clear()
        self._cbx_com.addItems(SerialConnection.listar_puertos())
        idx = self._cbx_com.findText(seleccionado)
        if idx >= 0:
            self._cbx_com.setCurrentIndex(idx)
        self._cbx_com.blockSignals(False)

    def _on_trama_changed(self, texto: str):
        self._trama_cambiada = True
        self._parser.tipo_trama = texto
        self._parser.limpiar_buffer()

    def _on_com_changed(self, texto: str):
        self._trama_cambiada = True

    def _on_abrir(self):
        puerto = self._cbx_com.currentText()
        if not puerto:
            QMessageBox.warning(self, "Aviso", "Seleccione un puerto COM.")
            return

        self.cerrar_conexion()
        self._parser.tipo_trama = self._cbx_tramas.currentText()
        self._parser.limpiar()

        self._set_controles_habilitados(False)
        self._lbl_conexion.setText("Conectando...")
        self._lbl_conexion.setStyleSheet("color: #FFAA00; padding: 2px 8px;")

        self._opener = PortOpener(puerto, self._on_datos_recibidos)
        self._opener.resultado.connect(self._on_port_open_result)
        self._opener.start()

    def _on_port_open_result(self, conn: object, error: str):
        self._abriendo = False
        self._opener = None
        if conn is not None:
            self._connection = conn
            self._trama_cambiada = False
            self._peso_label.setText("-----")
            self._restaurar_fuente()
            self._actualizar_estado_conexion(True)
        else:
            self._set_controles_habilitados(True)
            self._actualizar_estado_conexion(False, error)

    def _on_watchdog_open_result(self, conn: object, error: str):
        self._abriendo = False
        self._opener = None
        if conn is not None:
            self._connection = conn
            self._watchdog.stop()
            self._set_controles_habilitados(False)
            self._peso_label.setText("-----")
            self._actualizar_estado_conexion(True)
        else:
            self._actualizar_estado_conexion(False, error)
            if self._reintentos_apertura >= 40:
                self._watchdog.stop()
                QMessageBox.warning(
                    self, "Error de conexión",
                    f"No se pudo abrir el puerto tras "
                    f"{self._reintentos_apertura} intentos: {error}"
                )
            else:
                self._watchdog.setInterval(
                    min(2500 + self._reintentos_apertura * 500, 10000)
                )

    def _on_cerrar(self):
        self.cerrar_conexion()
        self._peso_label.setText("-----")
        self._restaurar_fuente()
        self._set_controles_habilitados(True)

    def cerrar_conexion(self):
        if self._connection is not None:
            self._connection.cerrar()
            self._connection = None
            self._actualizar_estado_conexion(False)
            self._lbl_trama.setText("Trama: ---")
            self._lbl_trama.setStyleSheet("color: #888888; padding: 2px 8px;")

    def _actualizar_estado_conexion(self, conectado: bool, error: str = ""):
        if conectado:
            self._lbl_conexion.setText("Conectado")
            self._lbl_conexion.setStyleSheet("color: #44FF44; padding: 2px 8px;")
        elif error:
            # Mostrar el error completo en la label, truncado si es muy largo
            texto = f"Error: {error}" if len(error) < 50 else f"Error: {error[:47]}..."
            self._lbl_conexion.setText(texto)
            self._lbl_conexion.setStyleSheet(
                "color: #FF4444; font-size: 9pt; padding: 2px 8px;"
            )
        else:
            self._lbl_conexion.setText("Desconectado")
            self._lbl_conexion.setStyleSheet("color: #FF4444; padding: 2px 8px;")

    def _on_datos_recibidos(self, datos: str):
        self._parser.alimentar(datos)
        self.peso_listo.emit()

    def _actualizar_peso(self):
        if self._connection is None or not self._connection.is_open:
            return
        self._parser.leer()
        if self._parser.peso_str:
            self._trama_cambiada = False
            self._peso_label.setText(self._parser.peso_str)
            self._ajustar_fuente()
            self._lbl_trama.setText("Trama: Recibiendo")
            self._lbl_trama.setStyleSheet("color: #44FF44; padding: 2px 8px;")
        elif self._trama_cambiada:
            self._peso_label.setText("Trama incorrecta")
            self._restaurar_fuente()
            self._lbl_trama.setText("Trama: Incorrecta")
            self._lbl_trama.setStyleSheet("color: #FFAA00; padding: 2px 8px;")

    def _ajustar_fuente(self):
        largo = len(self._peso_label.text())
        if largo <= 4:
            self._restaurar_fuente()
            return
        nuevo_tamano = max(48 * 6 / largo, 12)
        fuente = self._peso_label.font()
        if abs(fuente.pointSizeF() - nuevo_tamano) > 0.5:
            fuente.setPointSizeF(nuevo_tamano)
            self._peso_label.setFont(fuente)

    def _restaurar_fuente(self):
        fuente = self._peso_label.font()
        if abs(fuente.pointSizeF() - 48) > 0.5:
            self._peso_label.setFont(self._fuente_original)

    def _set_controles_habilitados(self, habilitado: bool):
        self._cbx_com.setEnabled(habilitado)
        self._cbx_tramas.setEnabled(habilitado)
        self._btn_abrir.setEnabled(habilitado)
        self._btn_cerrar.setEnabled(not habilitado)

    def _on_guardar_config(self):
        try:
            config = ConfigManager()
            config.tipo_trama = self._cbx_tramas.currentText()
            config.com_balanza = self._cbx_com.currentText()
            config.guardar()
            QMessageBox.information(self, "Info", "Configuración guardada.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")

    def _on_cerrar_app(self):
        resp = QMessageBox.question(
            self, "Confirmar cierre",
            "¿Está seguro de que desea cerrar el programa?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp == QMessageBox.StandardButton.Yes:
            self.close()

    def _init_watchdog(self):
        self._watchdog = QTimer(self)
        self._watchdog.timeout.connect(self._watchdog_tick)

    def _watchdog_tick(self):
        if self._abriendo:
            return

        self._reintentos_apertura += 1
        puerto = self._cbx_com.currentText()
        if not puerto:
            self._watchdog.stop()
            return

        disponibles = SerialConnection.listar_puertos()
        if puerto not in disponibles:
            if self._reintentos_apertura >= 30:
                self._watchdog.stop()
                QMessageBox.warning(
                    self, "Puerto no encontrado",
                    f"El puerto {puerto} no está disponible tras "
                    f"{self._reintentos_apertura} intentos."
                )
                return
            self._watchdog.setInterval(3000)
            return

        self.cerrar_conexion()
        self._parser.limpiar()
        self._abriendo = True
        self._lbl_conexion.setText("Conectando...")
        self._lbl_conexion.setStyleSheet("color: #FFAA00; padding: 2px 8px;")

        self._opener = PortOpener(puerto, self._on_datos_recibidos)
        self._opener.resultado.connect(self._on_watchdog_open_result)
        self._opener.start()

    def cargar_configuracion(self):
        config = ConfigManager.cargar()
        if config is not None:
            idx_trama = self._cbx_tramas.findText(config.tipo_trama)
            if idx_trama >= 0:
                self._cbx_tramas.setCurrentIndex(idx_trama)
            idx_com = self._cbx_com.findText(config.com_balanza)
            if idx_com >= 0:
                self._cbx_com.setCurrentIndex(idx_com)
            elif config.com_balanza:
                self._cbx_com.setEditText(config.com_balanza)
            return config

    def iniciar_reconexion(self):
        if self._cbx_com.currentText():
            self._reintentos_apertura = 0
            self._watchdog.setInterval(5000)
            self._watchdog.start()

    def closeEvent(self, event):
        self._watchdog.stop()
        self.cerrar_conexion()
        super().closeEvent(event)
