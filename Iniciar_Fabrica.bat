@echo off
echo ===================================================
echo    INICIANDO FABRICA DE LIBROS (Asset Foundry)
echo                  [ MODO DOCKER ]
echo ===================================================
echo.

echo [1/2] Levantando servicios (Nginx, Flask, Dashboard, n8n)...
docker compose up -d

echo.
echo [2/2] Iniciando el tunel Ngrok maestro...
echo (Este tunel servira como punto de entrada unico para todo el ecosistema)
ngrok http 80 --url https://default.internal

echo ===================================================
echo.
pause