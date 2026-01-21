# ============================================
# Configurador Automatico del Programador de Tareas
# Apple Store Scraper - Horarios Especificos
# ============================================

param(
    [string]$TaskName = "AppleStoreScraper",
    [switch]$Remove
)

# Verificar que se ejecuta como Administrador
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ADVERTENCIA: No se esta ejecutando como Administrador" -ForegroundColor Yellow
    Write-Host "Algunas opciones pueden no estar disponibles" -ForegroundColor Yellow
    Write-Host ""
}

# Configuracion
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RunTaskScript = Join-Path $ScriptDir "run_task.ps1"

# Banner
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  APPLE STORE SCRAPER - TASK SCHEDULER" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Si se solicita eliminar
if ($Remove) {
    Write-Host "Eliminando tarea '$TaskName'..." -ForegroundColor Yellow
    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction Stop
        Write-Host "Tarea eliminada exitosamente" -ForegroundColor Green
    }
    catch {
        Write-Host "Error al eliminar: $_" -ForegroundColor Red
    }
    exit
}

# Verificar que existe run_task.ps1
if (-not (Test-Path $RunTaskScript)) {
    Write-Host "ERROR: No se encuentra run_task.ps1 en $ScriptDir" -ForegroundColor Red
    exit 1
}

Write-Host "Configuracion de la tarea programada" -ForegroundColor White
Write-Host "  Nombre:      $TaskName" -ForegroundColor Cyan
Write-Host "  Script:      $RunTaskScript" -ForegroundColor Cyan
Write-Host "  Horarios:    06:00, 10:00, 14:00, 18:00, 20:00" -ForegroundColor Cyan
Write-Host "  Frecuencia:  5 ejecuciones diarias" -ForegroundColor Cyan
Write-Host ""

# Preguntar confirmacion
$confirm = Read-Host "Deseas continuar? (S/N)"
if ($confirm -notmatch '^[Ss]$') {
    Write-Host "Operacion cancelada" -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "Creando tarea programada..." -ForegroundColor Yellow

try {
    # Eliminar tarea existente si existe
    $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Host "Eliminando tarea existente..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }

    # Crear accion (ejecutar PowerShell con run_task.ps1)
    $action = New-ScheduledTaskAction `
        -Execute "powershell.exe" `
        -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$RunTaskScript`"" `
        -WorkingDirectory $ScriptDir

    # Crear triggers para cada horario
    $triggers = @()
    
    # 06:00 - Primer chequeo
    $trigger1 = New-ScheduledTaskTrigger -Daily -At "06:00"
    $triggers += $trigger1
    
    # 10:00 - Segundo chequeo
    $trigger2 = New-ScheduledTaskTrigger -Daily -At "10:00"
    $triggers += $trigger2
    
    # 14:00 - Tercer chequeo
    $trigger3 = New-ScheduledTaskTrigger -Daily -At "14:00"
    $triggers += $trigger3
    
    # 18:00 - Cuarto chequeo
    $trigger4 = New-ScheduledTaskTrigger -Daily -At "18:00"
    $triggers += $trigger4
    
    # 20:00 - Ultimo chequeo
    $trigger5 = New-ScheduledTaskTrigger -Daily -At "20:00"
    $triggers += $trigger5

    # Configuracion de la tarea
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -RunOnlyIfNetworkAvailable `
        -ExecutionTimeLimit (New-TimeSpan -Hours 1)

    # Principal (usuario actual)
    $principal = New-ScheduledTaskPrincipal `
        -UserId $env:USERNAME `
        -LogonType S4U `
        -RunLevel Limited

    # Registrar la tarea
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Description "Monitoreo automatico de disponibilidad iPhone en Apple Store. Ejecuta 5 veces al dia: 6:00, 10:00, 14:00, 18:00, 20:00" `
        -Action $action `
        -Trigger $triggers `
        -Settings $settings `
        -Principal $principal `
        -ErrorAction Stop | Out-Null

    Write-Host ""
    Write-Host "Tarea creada exitosamente!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Horarios configurados:" -ForegroundColor White
    Write-Host "   06:00 - Primer chequeo (antes de apertura)" -ForegroundColor Cyan
    Write-Host "   10:00 - Segundo chequeo" -ForegroundColor Cyan
    Write-Host "   14:00 - Tercer chequeo" -ForegroundColor Cyan
    Write-Host "   18:00 - Cuarto chequeo" -ForegroundColor Cyan
    Write-Host "   20:00 - Ultimo chequeo del dia" -ForegroundColor Cyan
    Write-Host ""
    
    # Informacion adicional
    Write-Host "Proximos pasos:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Verificar tarea en Programador de Tareas:" -ForegroundColor White
    Write-Host "   taskschd.msc" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Probar ejecucion manual:" -ForegroundColor White
    Write-Host "   Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Ver logs despues de la ejecucion:" -ForegroundColor White
    Write-Host "   Get-Content logs\task_scheduler.log -Tail 50" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Deshabilitar temporalmente:" -ForegroundColor White
    Write-Host "   Disable-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "5. Eliminar tarea:" -ForegroundColor White
    Write-Host "   .\setup_task_scheduler.ps1 -Remove" -ForegroundColor Gray
    Write-Host ""
    
    # Ofrecer ejecutar una prueba
    Write-Host "Deseas ejecutar una prueba ahora? (S/N): " -NoNewline -ForegroundColor Yellow
    $testNow = Read-Host
    
    if ($testNow -match '^[Ss]$') {
        Write-Host ""
        Write-Host "Ejecutando prueba..." -ForegroundColor Cyan
        Start-ScheduledTask -TaskName $TaskName
        Start-Sleep -Seconds 2
        
        Write-Host "Tarea iniciada" -ForegroundColor Green
        Write-Host "Monitoreando logs..." -ForegroundColor Cyan
        Write-Host ""
        
        # Esperar a que se cree el log
        Start-Sleep -Seconds 3
        
        # Mostrar logs si existen
        $logFile = Join-Path $ScriptDir "logs\task_scheduler.log"
        if (Test-Path $logFile) {
            Get-Content $logFile -Tail 20
        }
        else {
            Write-Host "Aun no se ha generado el log. Revisa en unos momentos." -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "Configuracion completada!" -ForegroundColor Green
    Write-Host "El bot se ejecutara automaticamente en los horarios configurados" -ForegroundColor Cyan
    Write-Host ""

}
catch {
    Write-Host ""
    Write-Host "ERROR al crear la tarea: $_" -ForegroundColor Red
    Write-Host ""
    
    if (-not $isAdmin) {
        Write-Host "Intenta ejecutar este script como Administrador:" -ForegroundColor Yellow
        Write-Host "   Click derecho en PowerShell > Ejecutar como administrador" -ForegroundColor Gray
    }
    
    exit 1
}
