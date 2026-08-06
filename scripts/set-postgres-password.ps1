# Rode este script em um PowerShell "Executar como Administrador".
# Ele reinicia o servico do PostgreSQL para aplicar a autenticacao "trust"
# (ja configurada em pg_hba.conf), define a senha do usuario postgres,
# reverte pg_hba.conf para scram-sha-256 (autenticacao segura) e reinicia
# o servico novamente.

$ErrorActionPreference = "Stop"

$pgBin = "C:\Program Files\PostgreSQL\17\bin"
$pgData = "C:\Program Files\PostgreSQL\17\data"
$hbaFile = "$pgData\pg_hba.conf"
$serviceName = "postgresql-x64-17"
$password = "14122004"

Write-Host "1/4 Reiniciando servico $serviceName para aplicar auth trust..."
Restart-Service -Name $serviceName -Force
Start-Sleep -Seconds 3

Write-Host "2/4 Definindo senha do usuario postgres..."
& "$pgBin\psql.exe" -U postgres -c "ALTER USER postgres PASSWORD '$password';"

Write-Host "3/4 Revertendo pg_hba.conf para scram-sha-256..."
(Get-Content $hbaFile) -replace '\btrust\b', 'scram-sha-256' | Set-Content $hbaFile -Encoding utf8

Write-Host "4/4 Reiniciando servico $serviceName para aplicar auth segura..."
Restart-Service -Name $serviceName -Force
Start-Sleep -Seconds 3

Write-Host "Pronto. Testando conexao com senha..."
$env:PGPASSWORD = $password
& "$pgBin\psql.exe" -U postgres -h 127.0.0.1 -c "SELECT version();"
Remove-Item Env:\PGPASSWORD
