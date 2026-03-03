@echo off
echo ========================================
echo    Сборка pSiteBot в .exe файл
echo ========================================
echo.

echo [1/4] Проверка PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller не найден. Устанавливаю...
    pip install pyinstaller
) else (
    echo PyInstaller уже установлен ✓
)

echo.
echo [2/4] Очистка старых сборок...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.spec del /q *.spec
echo Готово ✓

echo.
echo [3/4] Сборка main.exe...
pyinstaller -F -w main.py
echo Готово ✓

echo.
echo [4/4] Копирование дополнительных файлов...
if exist dist\main.exe (
    echo.
    echo ========================================
    echo    ✅ СБОРКА УСПЕШНО ЗАВЕРШЕНА!
    echo ========================================
    echo.
    echo Файл программы: dist\main.exe
    echo Размер: 
    dir dist\main.exe | find "main.exe"
    echo.
    echo Не забудь скопировать example файлы:
    echo - proxy_primer.txt
    echo - user_agents_primer
    echo.
) else (
    echo.
    echo ❌ ОШИБКА: Файл не создан!
    echo.
)

pause
