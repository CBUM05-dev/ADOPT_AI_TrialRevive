@echo off
REM Lance le nouveau site TrialRevive et l'ouvre dans le navigateur (double-clic).
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Environnement introuvable : lancez d'abord "python -m venv .venv" puis "pip install -r requirements.txt".
  pause
  exit /b 1
)
start "" http://localhost:8000
echo TrialRevive tourne sur http://localhost:8000  (fermez cette fenetre ou faites Ctrl+C pour arreter)
".venv\Scripts\python.exe" server.py 8000
pause
