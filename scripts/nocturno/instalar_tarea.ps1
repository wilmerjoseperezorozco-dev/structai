# Instala (o reemplaza) la tarea programada "StructAI-CI-nocturno" (#178). Uso, en PowerShell normal:
#   powershell -ExecutionPolicy Bypass -File scripts\nocturno\instalar_tarea.ps1
# Para quitarla: Unregister-ScheduledTask -TaskName "StructAI-CI-nocturno" -Confirm:$false
#
# - Corre a las 23:00 con el PC prendido (o suspendido: lo despierta) y la sesión iniciada. Si el PC estaba apagado, esa noche se salta: NO arranca
#   al prender el PC (antes usaba StartWhenAvailable y corría de día hasta que se apagaba el PC).
# - Antes de correr pone el worktree del nocturno en origin/master y lo crea si no existe. Nunca toca el clon principal.
param(
    [string]$Hora = "23:00",
    [string]$Principal = "C:\Users\wilme\dev\structai",
    [string]$Worktree = "C:\Users\wilme\dev\structai-nocturno",
    [string]$Ref = "origin/master"          # solo para probar una rama antes del merge
)
$bash = "C:\Program Files\Git\bin\bash.exe"
$p = $Principal -replace "\\", "/"
$w = $Worktree -replace "\\", "/"
if (-not (Test-Path $Worktree)) {
    git -C $Principal fetch -q origin
    git -C $Principal worktree add --detach $Worktree origin/master
}
$cmd = "git -C '$p' fetch -q origin && git -C '$w' checkout -q --detach $Ref && " +
       "bash '$w/scripts/nocturno/ci_nocturno.sh'"
$accion  = New-ScheduledTaskAction -Execute $bash -Argument "-lc `"$cmd`"" -WorkingDirectory $Worktree
$disparo = New-ScheduledTaskTrigger -Daily -At $Hora
$ajustes = New-ScheduledTaskSettingsSet -WakeToRun -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries `
           -ExecutionTimeLimit (New-TimeSpan -Hours 9) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "StructAI-CI-nocturno" -Action $accion -Trigger $disparo -Settings $ajustes `
    -Description "CI nocturno local de StructAI sobre master: pytest -m llm con Ollama en WSL (#178)" -Force | Out-Null
Get-ScheduledTask -TaskName "StructAI-CI-nocturno" | Select-Object TaskName, State
