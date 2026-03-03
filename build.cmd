@echo off
title Сборка pSiteBot
color 0A
echo ========================================
echo    pSiteBot - Сборщик проекта
echo ========================================
echo.

call :CheckPython
call :InstallRequirements
call :BuildExe
call :ShowResult
pause
exit /b

:CheckPython
echo [1/4] Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    pause
    exit
)
echo ✅ Python найден
goto :eof

:InstallRequirements
echo.
echo [2/4] Установка зависимостей...
pip install -r requirements.txt
echo ✅ Зависимости установлены
goto :eof

:BuildExe
echo.
echo [3/4] Сборка EXE файла...
pyinstaller -F -w main.py
echo ✅ Сборка завершена
goto :eof

:ShowResult
echo.
echo [4/4] Результат:
echo ========================================
if exist dist\main.exe (
    echo ✅ УСПЕХ! Файл создан: dist\main.exe
    for %%I in (dist\main.exe) do echo Размер: %%~zI байт
) else (
    echo ❌ ОШИБКА: Файл не найден!
)
echo ========================================
goto :eof
