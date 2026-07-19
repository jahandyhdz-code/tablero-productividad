@echo off
title Guardar Token de GitHub
color 0A
cd /d "%~dp0"

echo.
echo  ================================================
echo   GUARDAR TOKEN DE GITHUB
echo   (Solo necesitas hacer esto UNA vez)
echo  ================================================
echo.
echo  Ve a esta pagina en tu navegador:
echo  https://github.com/settings/tokens/new
echo.
echo  Configuracion del token:
echo    Nombre:     tablero-productividad
echo    Expiracion: No expiration (sin limite)
echo    Scope:      marca solo "repo"
echo    Clic en:    Generate token
echo.
echo  Copia el token que empieza con ghp_...
echo.
start "" "https://github.com/settings/tokens/new?scopes=repo&description=tablero-productividad"
echo.
set /p TOKEN="  Pega tu token aqui y presiona Enter: "

if "%TOKEN%"=="" (
    echo  ERROR: No pegaste ningun token.
    pause
    exit /b 1
)

echo GITHUB_TOKEN=%TOKEN%> .env
echo.
echo  ================================================
echo  Token guardado! Desde ahora DESPLEGAR_A_INTERNET
echo  funciona sin pedirte nada.
echo  ================================================
echo.
pause
