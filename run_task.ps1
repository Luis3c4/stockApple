# ============================================
# Ejecutor simple para Programador de Tareas
# ============================================

<#
.SYNOPSIS
    Ejecuta el scraper una sola vez (para usar con Windows Task Scheduler)

.DESCRIPTION
    Script simple que ejecuta main.py una vez
    Diseñado para ser usado con el Programador de Tareas de Windows
#>

# Configuración
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogFile = Join-Path $ScriptDir "logs\task_scheduler.log"

# Función para escribir log
function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] $Message"
    Add-Content -Path $LogFile -Value $LogMessage
}

# Crear directorio de logs si no existe
$LogsDir = Join-Path $ScriptDir "logs"
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir | Out-Null
}

# Cambiar al directorio del script
Set-Location $ScriptDir

Write-Log "============================================"
Write-Log "Iniciando ejecucion programada"

try {
    # Buscar Python en el PATH
    $PythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
    
    if (-not $PythonPath) {
        Write-Log "ERROR: No se encontro Python en el PATH"
        exit 1
    }
    
    Write-Log "Python encontrado: $PythonPath"
    
    # Ejecutar main.py
    $Output = & $PythonPath main.py 2>&1
    $ExitCode = $LASTEXITCODE
    
    if ($ExitCode -eq 0) {
        Write-Log "Ejecucion completada exitosamente"
    }
    else {
        Write-Log "Codigo de salida: $ExitCode"
        Write-Log "Output: $Output"
    }
    
}
catch {
    Write-Log "ERROR: $_"
    exit 1
}

Write-Log "Ejecucion finalizada"
Write-Log ""
exit 0
