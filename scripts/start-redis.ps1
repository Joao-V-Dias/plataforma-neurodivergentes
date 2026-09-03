# Sobe o Redis local (build portatil, sem servico Windows) na porta padrao
# 6379. Rode este script numa janela de terminal e deixe aberta enquanto
# desenvolve; feche a janela (Ctrl+C) para parar o Redis.
#
# Nota: nao passamos redis.conf como argumento porque o binario (MSYS2)
# tem um bug de resolucao de path absoluto do Windows quando o processo e
# iniciado via Start-Process/PowerShell, tratando o caminho como relativo
# ao cwd. Passamos a configuracao minima via flags de linha de comando.

$redisDir = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\taizod1024.redis-windows-fork_Microsoft.Winget.Source_8wekyb3d8bbwe\Redis-8.10.1-Windows-x64-msys2"
& "$redisDir\redis-server.exe" --port 6379 --daemonize no
