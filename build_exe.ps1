$ProjectName = "DesktopViewWeight"
$DistDir = "dist"
$BuildDir = "build_exe"

Write-Host "=== $ProjectName - Build Script (PyInstaller) ===" -ForegroundColor Cyan

# 1. Install PyInstaller if not present
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "[1/3] Instalando PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
    if (-not $?) { Write-Host "Error instalando PyInstaller" -ForegroundColor Red; exit 1 }
} else {
    Write-Host "[1/3] PyInstaller ya instalado" -ForegroundColor Green
}

# 2. Build executable (--onefile crea un solo .exe con todo incluido)
Write-Host "[2/3] Compilando $ProjectName.exe ..." -ForegroundColor Yellow
$null = Remove-Item -Recurse -Force $BuildDir, $DistDir, "__pycache__", "*.spec" -ErrorAction SilentlyContinue

pyinstaller --onefile --windowed `
    --name $ProjectName `
    --collect-all PyQt6 `
    --collect-all pyserial `
    --collect-all win32api `
    --hidden-import serial `
    --hidden-import serial.tools.list_ports `
    --hidden-import serial.tools.list_ports_common `
    --hidden-import win32api `
    --hidden-import win32con `
    --add-data "requeriments.txt;." `
    --icon "icon.ico" `
    --paths "C:\Python314" `
    main.py

if (-not $?) { Write-Host "Error en PyInstaller" -ForegroundColor Red; exit 1 }

Write-Host "[3/3] Build completado!" -ForegroundColor Green
Write-Host "Ejecutable: $DistDir\$ProjectName.exe" -ForegroundColor Cyan
Write-Host ""
Write-Host "Copialo a otra PC y ejecutalo directamente (no necesita Python)" -ForegroundColor Green
