# DesktopViewWeight

Aplicación de escritorio para leer y mostrar el peso de una báscula a través de puerto serie (COM). Desarrollada en Python con PyQt6, ocupa toda la pantalla sin bordes y se posiciona automáticamente en la esquina superior izquierda al iniciar.

## Requisitos

- Python 3.12+
- Windows (PyQt6, pyserial, pywin32)
- Puerto COM con báscula o simulador serie

## Instalación

```bash
pip install -r requeriments.txt
```

## Estructura del proyecto

```
DesktopViewWeight/
├── main.py                       # Punto de entrada
├── requeriments.txt              # Dependencias
├── config/
│   ├── __init__.py
│   └── config_manager.py         # Persistencia JSON de configuración
├── core/
│   ├── __init__.py
│   ├── serial_connection.py      # Conexión serie con hilo de lectura
│   └── trama_parser.py           # Parser de tramas con buffer thread-safe
├── ui/
│   ├── __init__.py
│   └── main_window.py            # Ventana principal (PyQt6)
├── utils/
│   └── __init__.py
└── data/
    └── __init__.py
```

## Flujo de la aplicación

```
main()
  └─> MainWindow() — constructor
        ├─> Configura ventana: 800x450, (0,0), sin bordes, fondo negro
        └─> Inicializa UI y watchdog de reconexión
  └─> main() continúa
        ├─> EnumerarPuertos() — lista COM disponibles
        ├─> CargarConfiguracion() — lee config.json
        └─> IniciarReconexion() — watchdog automático si hay puerto guardado
  └─> Watchdog_Tick (QTimer)
        ├─> Fase 1: puerto no existe → reintenta cada 3s (máx 30)
        └─> Fase 2: puerto existe pero falla → backoff 2.5s→10s (máx 40)
  └─> SerialConnection (hilo daemon)
        ├─> read_all() → datos crudos
        └─> callback → TramaParser.Alimentar()
  └─> ActualizarPeso (vía callback)
        └─> TramaParser.Leer() → QLabel.setText(peso)
  └─> [Login] → user: root / pass: systemconfig → muestra panel configuración
  └─> [Cerrar App] → confirmación → closeEvent → cerrar puerto
```

## Tipos de trama soportados

### XKR (predeterminado)
- Inicia con STX (`\x02`)
- Siguiente byte: signo (`+` / `-`)
- Dígitos de peso consecutivos de longitud variable

### XK310
- Misma estructura que XKR; comparten el mismo parser

### FT11
- Inicia con STX (`\x02`)
- Bytes 1-2: codec (bit 1 del byte 2 indica signo negativo)
- Bytes 4-9: 6 dígitos de peso fijos
- Longitud mínima desde STX: 10 bytes

### Generic
- Busca el primer número con signo mediante regex `(-?\d+)`
- Útil para básculas que envían texto plano

## Características

### Ventana
- Sin bordes ni botones de cerrar/minimizar/maximizar (`FramelessWindowHint`)
- Posición fija en la esquina superior izquierda (0, 0)
- Fondo negro con texto naranja/rojo en negrita

### Conexión serie
- 9600 baudios, 8 bits, sin paridad, 1 stop bit
- DTR y RTS habilitados para resetear buffer del chip USB-serial
- Descartado de buffer basura al abrir el puerto
- Reconexión automática con watchdog de 2 fases
- Detección de conexión: muestra "-----" cuando no hay datos

### Seguridad
- Botón Login en la barra de estado
- Usuario: `root` / Contraseña: `systemconfig`
- Panel de configuración visible solo tras login exitoso

### UI
- Ajuste dinámico de fuente: si el peso tiene más de 4 caracteres, reduce la fuente proporcionalmente (mínimo 12pt)
- Controles deshabilitados mientras el puerto está abierto
- Indicador "Trama incorrecta" al cambiar de formato
- "Valor negativo excedido" si el peso baja de -999

### Persistencia
- Configuración guardada en `%LOCALAPPDATA%\DesktopViewWeight\config.json`
- Campos: `TipoTrama` y `COMBalanza`

## Uso

1. Conecta la báscula al puerto COM
2. Ejecuta `python main.py`
3. Si hay configuración guardada, intentará la conexión automáticamente
4. Si no, haz clic en **Login** → ingresa credenciales → panel de configuración
5. Selecciona el puerto COM y el tipo de trama
6. Presiona **Abrir** para conectar
7. El peso se muestra en la pantalla en tiempo real
8. Presiona **Cerrar** para desconectar
9. Usa **Guardar Config** para persistir la configuración
10. Presiona **Cerrar App** para salir

## Configuración

```json
{
  "TipoTrama": "XKR",
  "COMBalanza": "COM3"
}
```

Al iniciar la aplicación, si existe el archivo en `%LOCALAPPDATA%\DesktopViewWeight\config.json`, se carga automáticamente y se intenta abrir el puerto COM configurado con reintentos.

---

Todos los derechos reservados - **All Process**  
Desarrollado por: **Anthony Josue Laura Perez**  
GitHub: https://github.com/anthony2004lp
