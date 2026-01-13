@echo off
title R0uteR - System Initialization
color 0a
cls
echo.
echo    INITIALIZING R0UTER PROTOCOLS...
echo.
cd /d "%~dp0"
python R0uteR.py
pause