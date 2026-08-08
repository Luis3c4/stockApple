# ============================================
# Verificador de Estado - Task Scheduler
# ============================================

<#
.SYNOPSIS
    Muestra el estado actual de la tarea programada

.DESCRIPTION
    Verifica y muestra información sobre:
    - Estado de la tarea
    - Próximas ejecuciones
    - Historial de ejecuciones recientes
    - Logs más recientes
#>

param(
    [string]$TaskName = "AppleStoreScraper"
)

Write-Host @"

╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   📊 VERIFICADOR DE ESTADO - TASK SCHEDULER              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# Verificar si existe la tarea
try {
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
    
    Write-Host "✅ Tarea encontrada: $TaskName" -ForegroundColor Green
    Write-Host ""
    
    # Estado
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host "📌 ESTADO ACTUAL" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    
    $state = $task.State
    $stateColor = switch ($state) {
        "Ready" { "Green" }
        "Running" { "Cyan" }
        "Disabled" { "Yellow" }
        default { "Red" }
    }
    
    $stateEmoji = switch ($state) {
        "Ready" { "✅" }
        "Running" { "🔄" }
        "Disabled" { "⏸️" }
        default { "❌" }
    }
    
    Write-Host "  Estado:      $stateEmoji $state" -ForegroundColor $stateColor
    
    # Información de la tarea
    $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
    
    if ($null -ne $taskInfo.LastRunTime) {
        $lastRun = $taskInfo.LastRunTime
        $timeSince = (Get-Date) - $lastRun
        Write-Host "  Última ejecución: $($lastRun.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor White
        Write-Host "                    (hace $([Math]::Floor($timeSince.TotalHours))h $($timeSince.Minutes)m)" -ForegroundColor Gray
        
        $lastResult = $taskInfo.LastTaskResult
        if ($lastResult -eq 0) {
            Write-Host "  Resultado:        ✅ Exitoso (código: $lastResult)" -ForegroundColor Green
        }
        else {
            Write-Host "  Resultado:        ⚠️ Código: $lastResult" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "  Última ejecución: Nunca ejecutada" -ForegroundColor Gray
    }
    
    if ($null -ne $taskInfo.NextRunTime) {
        $nextRun = $taskInfo.NextRunTime
        $timeUntil = $nextRun - (Get-Date)
        Write-Host "  Próxima ejecución: $($nextRun.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor White
        Write-Host "                     (en $([Math]::Floor($timeUntil.TotalHours))h $($timeUntil.Minutes)m)" -ForegroundColor Gray
    }
    
    Write-Host ""
    
    # Horarios configurados
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host "⏰ HORARIOS CONFIGURADOS" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    
    $triggers = $task.Triggers
    $now = Get-Date
    
    foreach ($trigger in $triggers | Sort-Object { [datetime]::Parse($_.StartBoundary).ToString('HH:mm') }) {
        if ($trigger.StartBoundary) {
            $startTime = [datetime]::Parse($trigger.StartBoundary)
            $timeStr = $startTime.ToString('HH:mm')
            
            $description = switch ($timeStr) {
                "06:00" { "🌅 Primer chequeo (antes de apertura)" }
                "10:00" { "☀️  Segundo chequeo" }
                "14:00" { "🕐 Tercer chequeo" }
                "18:00" { "🌆 Cuarto chequeo" }
                "20:00" { "🌙 Último chequeo del día" }
                default { "📅 Ejecución programada" }
            }
            
            # Marcar si ya pasó hoy
            $scheduledToday = Get-Date -Hour $startTime.Hour -Minute $startTime.Minute -Second 0
            if ($now -gt $scheduledToday) {
                Write-Host "  $timeStr - $description ✓" -ForegroundColor DarkGray
            }
            else {
                Write-Host "  $timeStr - $description" -ForegroundColor Cyan
            }
        }
    }
    
    Write-Host ""
    
    # Logs recientes
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $logFile = Join-Path $ScriptDir "logs\task_scheduler.log"
    
    if (Test-Path $logFile) {
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
        Write-Host "📝 LOGS RECIENTES (últimas 15 líneas)" -ForegroundColor Yellow
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
        Get-Content $logFile -Tail 15 | ForEach-Object {
            if ($_ -match '✅') {
                Write-Host $_ -ForegroundColor Green
            }
            elseif ($_ -match '❌') {
                Write-Host $_ -ForegroundColor Red
            }
            elseif ($_ -match '⚠️') {
                Write-Host $_ -ForegroundColor Yellow
            }
            else {
                Write-Host $_ -ForegroundColor Gray
            }
        }
    }
    else {
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
        Write-Host "📝 LOGS" -ForegroundColor Yellow
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
        Write-Host "  ⚠️ No se encontraron logs todavía" -ForegroundColor Yellow
        Write-Host "  La tarea aún no se ha ejecutado" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host "🛠️  COMANDOS ÚTILES" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  Ejecutar ahora:" -ForegroundColor White
    Write-Host "    Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Ver logs en tiempo real:" -ForegroundColor White
    Write-Host "    Get-Content logs\task_scheduler.log -Wait" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Deshabilitar:" -ForegroundColor White
    Write-Host "    Disable-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Habilitar:" -ForegroundColor White
    Write-Host "    Enable-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Eliminar:" -ForegroundColor White
    Write-Host "    .\setup_task_scheduler.ps1 -Remove" -ForegroundColor Gray
    Write-Host ""
    
}
catch {
    Write-Host "❌ No se encontró la tarea '$TaskName'" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Para crear la tarea, ejecuta:" -ForegroundColor Yellow
    Write-Host "   .\setup_task_scheduler.ps1" -ForegroundColor Gray
    Write-Host ""
    exit 1
}
