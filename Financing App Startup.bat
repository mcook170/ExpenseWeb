@echo off
start "" cmd /k "python "C:\Users\cookm\OneDrive\Documents\ExpenseWeb\financingapp.py"
timeout /t 7 >nul
start "" http://localhost:5000