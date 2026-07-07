@echo off
title Deploy a Internet - Tablero de Productividad
chcp 65001 > nul
cd /d "%~dp0"

echo.
echo  ================================================================
echo    SUBIR TABLERO A INTERNET - Render.com
echo  ================================================================
echo.
echo  Este proceso sube tu app a internet para que cualquier persona
echo  pueda abrirla sin VPN ni red Walmart.
echo.
echo  Necesitas:
echo    1. Cuenta en GitHub (gratis) - https://github.com/join
echo    2. Cuenta en Render (gratis) - https://render.com
echo.
echo  Si ya las tienes, presiona cualquier tecla para continuar...
echo  Si no las tienes, abre los links de arriba primero.
echo.
pause > nul

.venv\Scripts\python.exe deploy_render.py

echo.
pause
