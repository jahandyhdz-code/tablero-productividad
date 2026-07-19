@echo off
title Corregir Deploy - Tablero de Productividad
chcp 65001 > nul
cd /d "%~dp0"
echo.
echo  ================================================================
echo    CORRIGIENDO DEPLOY EN RENDER
echo  ================================================================
echo.
echo  Cuando te pida el token, pega el codigo que empieza con ghp_
echo  y presiona Enter.
echo.
.venv\Scripts\python.exe fix_deploy.py
echo.
pause
