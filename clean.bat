@echo off
echo Очистка временных файлов...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec
if exist __pycache__ rmdir /s /q __pycache__
echo Готово!
pause
