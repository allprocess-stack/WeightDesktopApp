import threading
import time
from typing import Callable, Optional

import serial
import serial.tools.list_ports

_INTENTOS_MAX = 10
_DELAY_INICIAL = 1.0
_DELAY_MAX = 8.0


class SerialConnection:
    def __init__(self, on_datos_recibidos: Callable[[str], None]) -> None:
        self._puerto: Optional[serial.Serial] = None
        self._hilo_lectura: Optional[threading.Thread] = None
        self._corriendo = False
        self.on_datos_recibidos = on_datos_recibidos

    @property
    def is_open(self) -> bool:
        return self._puerto is not None and self._puerto.is_open

    def abrir(self, nombre_puerto: str, reintentar: bool = False) -> None:
        """Abre el puerto serie con reintentos opcionales para PermissionError.

        Args:
            nombre_puerto: Puerto COM a abrir (ej. 'COM2').
            reintentar: Si True, reintenta hasta _INTENTOS_MAX veces con
                       backoff exponencial cuando falla con PermissionError.

        Raises:
            serial.SerialException: Si no se pudo abrir tras todos los intentos.
        """
        if reintentar:
            self._abrir_con_reintentos(nombre_puerto)
        else:
            self._abrir_directo(nombre_puerto)

    def _abrir_directo(self, nombre_puerto: str) -> None:
        self.cerrar()
        self._puerto = serial.Serial(
            port=nombre_puerto,
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.5,
        )
        self._puerto.dtr = True
        self._puerto.rts = True
        self._puerto.reset_input_buffer()
        self._iniciar_lectura()

    def _abrir_con_reintentos(self, nombre_puerto: str) -> None:
        delay = _DELAY_INICIAL
        for intento in range(1, _INTENTOS_MAX + 1):
            try:
                self._abrir_directo(nombre_puerto)
                return
            except serial.SerialException as e:
                error_str = str(e).lower()
                es_permission = (
                    isinstance(e, PermissionError)
                    or "access is denied" in error_str
                    or "permissionerror" in error_str
                    or "denied" in error_str
                )
                if not es_permission or intento == _INTENTOS_MAX:
                    raise
                time.sleep(delay)
                delay = min(delay * 1.5, _DELAY_MAX)

    def resetear_puerto(self, nombre_puerto: str) -> None:
        try:
            with serial.Serial(
                port=nombre_puerto,
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1,
            ) as temp:
                temp.dtr = True
                temp.rts = True
                time.sleep(0.05)
                temp.reset_input_buffer()
        except Exception:
            pass

    def cerrar(self) -> None:
        self._corriendo = False
        if self._hilo_lectura is not None and self._hilo_lectura.is_alive():
            self._hilo_lectura.join(timeout=2)
        if self._puerto is not None and self._puerto.is_open:
            self._puerto.dtr = False
            self._puerto.rts = False
            self._puerto.close()
        self._puerto = None

    def _iniciar_lectura(self) -> None:
        self._corriendo = True
        self._hilo_lectura = threading.Thread(target=self._bucle_lectura, daemon=True)
        self._hilo_lectura.start()

    def _bucle_lectura(self) -> None:
        while self._corriendo and self._puerto is not None and self._puerto.is_open:
            try:
                datos = self._puerto.read_all()
                if datos:
                    texto = datos.decode("utf-8", errors="replace")
                    self.on_datos_recibidos(texto)
                else:
                    time.sleep(0.01)
            except Exception:
                break

    @staticmethod
    def listar_puertos() -> list[str]:
        return [p.device for p in serial.tools.list_ports.comports()]
