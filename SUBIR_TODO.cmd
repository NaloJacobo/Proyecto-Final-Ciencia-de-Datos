@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0SUBIR_A_GITHUB.ps1"
set "RESULTADO=%ERRORLEVEL%"
echo.
if not "%RESULTADO%"=="0" (
    echo No se completo la subida. Revisa el error mostrado arriba.
) else (
    echo Puedes copiar el enlace de GitHub que aparece arriba.
)
pause
exit /b %RESULTADO%
