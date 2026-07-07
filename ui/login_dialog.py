from PyQt6.QtWidgets import (
    QDialog,
    QLineEdit,
    QFormLayout,
    QDialogButtonBox,
)


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Iniciar sesión")
        self.setFixedSize(280, 140)

        self.usuario_input = QLineEdit()
        self.contrasena_input = QLineEdit()
        self.contrasena_input.setEchoMode(QLineEdit.EchoMode.Password)

        layout = QFormLayout(self)
        layout.addRow("Usuario:", self.usuario_input)
        layout.addRow("Contraseña:", self.contrasena_input)

        botones = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        layout.addRow(botones)

    def credenciales(self):
        return self.usuario_input.text(), self.contrasena_input.text()
