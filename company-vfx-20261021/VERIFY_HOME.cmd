@echo off
cd /d "%~dp0"
"%~dp0.toolchain\msys64\mingw64\bin\python.exe" -X utf8 "%~dp0scripts\verify-home-transfer.py"
if errorlevel 1 pause
