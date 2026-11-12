@echo off
cd /d %~dp0
title Jarvis
:loop
py bot.py
echo Jarvis upal, perezapusk cherez 10 sek...
timeout /t 10 >nul
goto loop
