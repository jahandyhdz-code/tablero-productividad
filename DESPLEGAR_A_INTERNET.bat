@echo off
title Desplegar a Internet
color 0A
cd /d "%~dp0"

echo.
echo  ================================================
echo   SUBIENDO CAMBIOS A INTERNET...
echo  ================================================
echo.

uv run python quick_deploy.py

echo.
echo  ================================================
echo  Listo! En 3 minutos la liga esta actualizada:
echo  https://tablero-productividad-bodega.onrender.com
echo  ================================================
echo.
pause
