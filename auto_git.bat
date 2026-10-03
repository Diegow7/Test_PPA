@echo off
setlocal EnableExtensions

set "REPO=D:\VS Code\Test_PPA"
set "LOG=%REPO%\git_log.txt"

cd /d "%REPO%"

echo.>>"%LOG%"
echo =====================================>>"%LOG%"
echo INICIO: %date% %time%>>"%LOG%"

echo Esperando conexion con GitHub...>>"%LOG%"

set /a INTENTOS=0

:ESPERAR_RED
nslookup github.com >nul 2>&1

if not errorlevel 1 goto RED_DISPONIBLE

set /a INTENTOS+=1
echo Intento de red %INTENTOS% sin conexion.>>"%LOG%"

if %INTENTOS% GEQ 12 (
    echo ERROR: GitHub no estuvo disponible despues de 12 intentos.>>"%LOG%"
    echo FIN CON ERROR: %date% %time%>>"%LOG%"
    echo =====================================>>"%LOG%"
    exit /b 10
)

timeout /t 10 /nobreak >nul
goto ESPERAR_RED

:RED_DISPONIBLE
echo Conexion con GitHub disponible.>>"%LOG%"

python auto_commit.py >>"%LOG%" 2>&1

if errorlevel 1 (
    echo ERROR: Fallo auto_commit.py.>>"%LOG%"
    exit /b 20
)

git add -A >>"%LOG%" 2>&1

if errorlevel 1 (
    echo ERROR: Fallo git add.>>"%LOG%"
    exit /b 30
)

git diff --cached --quiet

if not errorlevel 1 (
    echo No hay cambios nuevos para crear un commit.>>"%LOG%"
    goto ENVIAR
)

set "MSG="
set /p MSG=<commit_message.txt

if not defined MSG (
    echo ERROR: commit_message.txt esta vacio.>>"%LOG%"
    exit /b 40
)

git commit -m "%MSG%" >>"%LOG%" 2>&1

if errorlevel 1 (
    echo ERROR: Fallo git commit.>>"%LOG%"
    exit /b 50
)

:ENVIAR
set /a PUSH_INTENTOS=0

:REINTENTAR_PUSH
git push origin main >>"%LOG%" 2>&1

if not errorlevel 1 goto PUSH_CORRECTO

set /a PUSH_INTENTOS+=1
echo Fallo git push. Reintento %PUSH_INTENTOS% de 5.>>"%LOG%"

if %PUSH_INTENTOS% GEQ 5 (
    echo ERROR: No fue posible enviar los commits a GitHub.>>"%LOG%"
    echo FIN CON ERROR: %date% %time%>>"%LOG%"
    echo =====================================>>"%LOG%"
    exit /b 60
)

timeout /t 15 /nobreak >nul
goto REINTENTAR_PUSH

:PUSH_CORRECTO
echo Git push completado correctamente.>>"%LOG%"
echo FIN CORRECTO: %date% %time%>>"%LOG%"
echo =====================================>>"%LOG%"

exit /b 0