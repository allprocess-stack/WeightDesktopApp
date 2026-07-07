import re
import threading


class TramaParser:
    """Interpreta tramas de peso desde un buffer acumulado thread-safe.
    Los datos se insertan vía alimentar() desde el hilo de lectura del serial
    y se parsean desde el hilo de UI en leer()."""

    def __init__(self) -> None:
        self.trama: str = ""
        self.peso_str: str = ""
        self.tipo_trama: str = "XKR"

        self._buffer: list[str] = []
        self._lock = threading.Lock()

    def alimentar(self, datos: str) -> None:
        """Acumula datos crudos en el buffer interno. Thread-safe."""
        if not datos:
            return
        with self._lock:
            self._buffer.append(datos)

    def limpiar_buffer(self) -> None:
        """Limpia el buffer acumulado. Se usa al cambiar el tipo de trama."""
        with self._lock:
            self._buffer.clear()

    def limpiar(self) -> None:
        """Limpia todos los datos: trama parseada, peso y buffer interno."""
        self.trama = ""
        self.peso_str = ""
        self.limpiar_buffer()

    def leer(self) -> None:
        """Parsea el buffer según el tipo de trama activo.
        Si encuentra una trama válida, actualiza peso_str y consume del buffer."""
        with self._lock:
            buffer = "".join(self._buffer)

        if not buffer:
            self.peso_str = ""
            return

        match self.tipo_trama:
            case "XK310":
                self._parsear_xk310(buffer)
            case "FT11":
                self._parsear_ft11(buffer)
            case "Generic":
                self._parsear_generic(buffer)
            case _:
                self._parsear_xkr(buffer)

    def _consumir_buffer(self, cantidad: int) -> None:
        """Remueve los primeros `cantidad` caracteres del buffer. Thread-safe."""
        if cantidad <= 0:
            return
        with self._lock:
            texto = "".join(self._buffer)
            if cantidad >= len(texto):
                self._buffer.clear()
            else:
                self._buffer = [texto[cantidad:]]

    def _parsear_xkr(self, buffer: str) -> None:
        """Formato XKR: STX (\\x02) + signo (+/-) + dígitos de peso variables."""
        stx_idx = buffer.find("\x02")
        if stx_idx < 0:
            return
        if len(buffer) < stx_idx + 3:
            return

        signo = buffer[stx_idx + 1]
        idx = stx_idx + 2
        while idx < len(buffer) and buffer[idx].isdigit():
            idx += 1

        if idx == stx_idx + 2:
            return

        raw_peso = buffer[stx_idx + 2 : idx]

        try:
            peso = int(raw_peso)
            if signo != "+":
                peso = -peso

            if peso < -999:
                self.peso_str = "Valor negativo excedido"
                self._consumir_buffer(idx)
                return

            self.trama = buffer[stx_idx:idx]
            self.peso_str = str(peso)
            self._consumir_buffer(idx)
        except ValueError:
            pass

    def _parsear_xk310(self, buffer: str) -> None:
        """XK310 tiene la misma estructura que XKR."""
        self._parsear_xkr(buffer)

    def _parsear_ft11(self, buffer: str) -> None:
        """FT11: STX (\\x02) + codec (2 bytes) + 6 dígitos de peso fijos.
        Requiere al menos 10 bytes desde STX."""
        stx_idx = buffer.find("\x02")
        if stx_idx < 0:
            return
        if len(buffer) < stx_idx + 10:
            return

        raw_peso = buffer[stx_idx + 4 : stx_idx + 10]
        codec_str = buffer[stx_idx + 1 : stx_idx + 3]

        signo = -1 if (ord(codec_str[1]) & 0x02) == 2 else 1

        try:
            peso = int(raw_peso) * signo

            if peso < -999:
                self.peso_str = "Valor negativo excedido"
                self._consumir_buffer(stx_idx + 10)
                return

            self.trama = buffer[stx_idx : stx_idx + 10]
            self.peso_str = str(peso)
            self._consumir_buffer(stx_idx + 10)
        except ValueError:
            pass

    def _parsear_generic(self, buffer: str) -> None:
        """Generic: busca el primer número con signo opcional mediante regex."""
        try:
            match = re.search(r"(-?\d+)", buffer)
            if not match:
                return

            peso = int(match.group(1))

            if peso < -999:
                self.peso_str = "Valor negativo excedido"
                self._consumir_buffer(len(buffer))
                return

            self.trama = match.group(0)
            self.peso_str = str(peso)
            self._consumir_buffer(match.end())
        except ValueError:
            pass
