@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0OPEN_HOME_EXPLORER.ps1"
if errorlevel 1 pause
