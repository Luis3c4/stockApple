# Script de ayuda para ejecutar Apple Store Scraper
# Uso: .\run.ps1 [comando]

param(
    [Parameter(Position = 0)]
    [ValidateSet("scrape", "visible", "test", "config", "json", "help")]
    [string]$Command = "scrape"
)

$venvActivate = ".\.venv\Scripts\Activate.ps1"

# Verificar si existe entorno virtual
if (!(Test-Path $venvActivate)) {
    Write-Host "❌ No se encontró entorno virtual" -ForegroundColor Red
    Write-Host "💡 Ejecuta primero: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# Activar entorno virtual
& $venvActivate

Write-Host "🍎 Apple Store Scraper" -ForegroundColor Green
Write-Host ""

switch ($Command) {
    "scrape" {
        Write-Host "🔄 Ejecutando scraper (modo headless)..." -ForegroundColor Cyan
        python main.py
    }
    "visible" {
        Write-Host "👀 Ejecutando scraper (navegador visible)..." -ForegroundColor Cyan
        python main.py --headless=false
    }
    "test" {
        Write-Host "🧪 Probando conexión..." -ForegroundColor Cyan
        python main.py --test
    }
    "config" {
        Write-Host "⚙️ Mostrando configuración..." -ForegroundColor Cyan
        python main.py --show-config
    }
    "json" {
        Write-Host "💾 Ejecutando scraper y guardando JSON..." -ForegroundColor Cyan
        python main.py --save-json
    }
    "help" {
        Write-Host "Comandos disponibles:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  .\run.ps1 scrape    " -NoNewline -ForegroundColor Green
        Write-Host "- Ejecutar scraper (modo headless)"
        Write-Host "  .\run.ps1 visible   " -NoNewline -ForegroundColor Green
        Write-Host "- Ver navegador durante scraping"
        Write-Host "  .\run.ps1 test      " -NoNewline -ForegroundColor Green
        Write-Host "- Probar conexión con Apple Store"
        Write-Host "  .\run.ps1 config    " -NoNewline -ForegroundColor Green
        Write-Host "- Mostrar configuración actual"
        Write-Host "  .\run.ps1 json      " -NoNewline -ForegroundColor Green
        Write-Host "- Guardar resultados en JSON"
        Write-Host "  .\run.ps1 help      " -NoNewline -ForegroundColor Green
        Write-Host "- Mostrar esta ayuda"
        Write-Host ""
        Write-Host "Ejemplos:" -ForegroundColor Yellow
        Write-Host "  .\run.ps1           " -NoNewline -ForegroundColor Cyan
        Write-Host "# Ejecuta scraper por defecto"
        Write-Host "  .\run.ps1 visible   " -NoNewline -ForegroundColor Cyan
        Write-Host "# Recomendado para desarrollo"
    }
}
