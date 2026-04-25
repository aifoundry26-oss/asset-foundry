@echo off
echo ========================================================
echo Instalador del Centro de Control IA - Asset Foundry
echo ========================================================
echo.

echo [1/3] Creando entorno virtual de Python (asset_foundry_env)...
python -m venv asset_foundry_env

echo [2/3] Activando entorno virtual...
call asset_foundry_env\Scripts\activate.bat

echo [3/3] Instalando dependencias necesarias...
python -m pip install --upgrade pip
pip install -r modules\requisitos.txt

echo.
echo ========================================================
echo ¡Instalacion completada con exito!
echo ========================================================
echo.
echo Para iniciar el dashboard en cualquier momento, ejecuta:
echo asset_foundry_env\Scripts\streamlit.exe run modules\dashboard.py
echo.
set /p start_now="¿Deseas iniciar el dashboard ahora mismo? (S/N): "
if /i "%start_now%"=="S" (
    echo Iniciando Dashboard...
    streamlit run modules\dashboard.py
)

pause
