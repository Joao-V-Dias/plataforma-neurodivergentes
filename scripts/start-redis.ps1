# Sobe o Redis local (build portatil, sem servico Windows) na porta padrao
# 6379. Rode este script numa janela de terminal e deixe aberta enquanto
# desenvolve; feche a janela (Ctrl+C) para parar o Redis.

$redisDir = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\taizod1024.redis-windows-fork_Microsoft.Winget.Source_8wekyb3d8bbwe\Redis-8.8.0-Windows-x64-msys2"
& "$redisDir\redis-server.exe" "$redisDir\redis.conf" --port 6379
