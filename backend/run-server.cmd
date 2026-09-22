@echo off
REM ORBITE — production locale (serveur unique Django + frontend buildé).
REM Lance Waitress sur le port 8000. Executer via : python serve.py
setlocal
cd /d "%~dp0"
set PYTHON="%CD%\.venv\Scripts\python.exe"
if not exist %PYTHON% set PYTHON=python
"%PYTHON%" serve.py