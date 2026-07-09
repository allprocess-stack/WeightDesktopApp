from pathlib import Path
import json
import os


class ConfigManager:
    """Gestiona la persistencia de la configuración en un archivo JSON.
    Almacena el tipo de trama y el puerto COM de la báscula."""

    def __init__(self) -> None:
        self.tipo_trama: str = ""
        self.com_balanza: str = ""

    @property
    def _ruta_archivo(self) -> Path:
        """Devuelve la ruta completa al archivo de configuración en %LOCALAPPDATA%."""
        local_app_data = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return local_app_data / "DesktopViewWeight" / "config.json"

    def guardar(self) -> None:
        """Guarda la configuración actual (tipo_trama y com_balanza) como JSON."""
        ruta = self._ruta_archivo
        ruta.parent.mkdir(parents=True, exist_ok=True)
        data = {"TipoTrama": self.tipo_trama, "COMBalanza": self.com_balanza}
        ruta.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def cargar(cls) -> "ConfigManager | None":
        """Carga la configuración desde el archivo JSON.
        Devuelve None si el archivo no existe o hay un error de lectura."""
        inst = cls()
        ruta = inst._ruta_archivo
        if not ruta.exists():
            return None
        try:
            data = json.loads(ruta.read_text(encoding="utf-8"))
            inst.tipo_trama = data.get("TipoTrama", "")
            inst.com_balanza = data.get("COMBalanza", "")
            return inst
        except Exception:
            return None
