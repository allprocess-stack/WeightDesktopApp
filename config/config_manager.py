from pathlib import Path
import json
import os


class ConfigManager:
    def __init__(self) -> None:
        self.tipo_trama: str = ""
        self.com_balanza: str = ""

    @property
    def _ruta_archivo(self) -> Path:
        local_app_data = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return local_app_data / "DesktopViewWeight" / "config.json"

    def guardar(self) -> None:
        ruta = self._ruta_archivo
        ruta.parent.mkdir(parents=True, exist_ok=True)
        data = {"TipoTrama": self.tipo_trama, "COMBalanza": self.com_balanza}
        ruta.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def cargar(cls) -> "ConfigManager | None":
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
