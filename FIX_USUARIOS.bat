@echo off
title Fix Usuarios Bloqueados
chcp 65001 > nul
cd /d "%~dp0"
echo.
echo  Necesitas la External Database URL de Render.
echo  En tu cel: Render -> ventas-db -> Connections -> External Database URL
echo.
.venv\Scripts\python.exe fix_usuarios_bloqueados.py
pause
