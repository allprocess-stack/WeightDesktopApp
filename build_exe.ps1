$ProjectName = "DesktopViewWeight"
$DistDir = "dist"

Write-Host "=== $ProjectName - Build Script ===" -ForegroundColor Cyan

# 1. Install PyInstaller if not present
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "[1/3] Instalando PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
    if (-not $?) { Write-Host "Error instalando PyInstaller" -ForegroundColor Red; exit 1 }
} else {
    Write-Host "[1/3] PyInstaller ya instalado" -ForegroundColor Green
}

# 2. Build executable
Write-Host "[2/3] Compilando $ProjectName.exe ..." -ForegroundColor Yellow
$null = Remove-Item -Recurse -Force $DistDir, "__pycache__", "*.spec" -ErrorAction SilentlyContinue

pyinstaller --onefile --windowed `
    --name $ProjectName `
    --collect-all PyQt6 `
    --hidden-import serial `
    --hidden-import serial.tools.list_ports `
    --hidden-import win32api `
    --add-data "requeriments.txt;." `
    main.py

if (-not $?) { Write-Host "Error en PyInstaller" -ForegroundColor Red; exit 1 }

# 3. Copy config template (optional)
if (Test-Path "config.json") {
    Copy-Item "config.json" "$DistDir\config.json" -ErrorAction SilentlyContinue
}

Write-Host "[3/3] Build completado!" -ForegroundColor Green
Write-Host "Ejecutable en: $DistDir\$ProjectName.exe" -ForegroundColor Green
Write-Host ""
Write-Host "Para crear el instalador .exe:" -ForegroundColor Cyan
Write-Host "  1. Descarga Inno Setup: https://jrsoftware.org/isdl.php" -ForegroundColor Cyan
Write-Host "  2. Abre 'installer.iss' con Inno Setup y compila" -ForegroundColor Cyan
