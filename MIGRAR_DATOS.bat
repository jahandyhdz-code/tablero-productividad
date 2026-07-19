@echo off
title Migrar Datos a Render
chcp 65001 > nul
cd /d "%~dp0"
echo.
echo  ================================================================
echo    MIGRACION DE DATOS — Local a Render
echo  ================================================================
echo.
echo  Necesitas la URL de PostgreSQL de Render.
echo  En tu celular: Render -> ventas-db -> Connections -> External Database URL
echo.
.venv\Scripts\python.exe migrar_datos.py
echo.
pause
