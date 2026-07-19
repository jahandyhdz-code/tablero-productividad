@echo off
title Desplegar Tamagotchi a Internet
color 0A
cd /d "%~dp0"

echo.
echo  ================================================
echo   SUBIR TAMAGOTCHI A INTERNET (Render)
echo  ================================================
echo.
echo  Este script sube el codigo nuevo a GitHub
echo  y Render actualiza la liga automaticamente.
echo.
echo  Necesitas tu token de GitHub (ghp_...)
echo  Si no lo tienes, el script abre GitHub para
echo  que generes uno nuevo (gratis, 7 dias).
echo.
echo  Presiona cualquier tecla para continuar...
pause > nul

echo.
uv run python deploy_render.py

echo.
echo  ================================================
echo  Listo! Revisa el navegador para ver el progreso.
echo  ================================================
pause
