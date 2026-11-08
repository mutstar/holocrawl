@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0PLAY_CITY.ps1" %*
if errorlevel 1 pause
