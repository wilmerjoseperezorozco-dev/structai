# Instala (o reemplaza) la tarea programada de Windows que lanza el CI nocturno local de StructAI (#178).
# Corre todos los días a las 22:00 si la sesión del usuario está iniciada; si el PC estaba apagado a esa hora, la
# tarea arranca apenas se encienda (StartWhenAvailable). Para quitarla:
#   Unregister-ScheduledTask -TaskName "StructAI-CI-nocturno" -Confirm:$false
param([string]$Hora = "22:00")
$repo   = (Resolve-Path "$PSScriptRoot\..\..").Path
$bash   = "C:\Program Files\Git\bin\bash.exe"
$script = (Join-Path $repo "scripts\nocturno\ci_nocturno.sh") -replace "\\", "/"
$accion = New-ScheduledTaskAction -Execute $bash -Argument "-lc `"'$script'`"" -WorkingDirectory $repo
$disparo = New-ScheduledTaskTrigger -Daily -At $Hora
$ajustes = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun -DontStopIfGoingOnBatteries `
           -AllowStartIfOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 20) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "StructAI-CI-nocturno" -Action $accion -Trigger $disparo -Settings $ajustes `
    -Description "CI nocturno local de StructAI con LLM local (Ollama/WSL): pytest -m llm + sabotaje (#178)" -Force | Out-Null
Get-ScheduledTask -TaskName "StructAI-CI-nocturno" | Select-Object TaskName, State
