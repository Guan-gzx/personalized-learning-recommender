@echo off
REM 在与 Spyder 完全隔离的 Python 进程中启动应用，避开 PyQt5 的 DLL 冲突。
cd /d "C:\Users\19355\WorkBuddy\2026-09-07-08-51-35\task16\task16_personalized_learning_recommender"
start "" http://127.0.0.1:5000/
".venv\Scripts\pythonw.exe" app.py
