@echo off
chcp 65001 >nul
REM ============================================================
REM  run.bat - запуск визуализатора графа зависимостей
REM ============================================================
setlocal

REM Переход в папку, где лежит сам bat-файл
cd /d "%~dp0"

REM Проверка, создано ли виртуальное окружение
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Виртуальное окружение .venv не найдено!
    echo Убедитесь, что вы создали его в PyCharm.
    pause
    exit /b 1
)

echo [INFO] Запуск визуализатора зависимостей...
echo.

REM Запускаем скрипт через Python из виртуального окружения
".venv\Scripts\python.exe" -m src.main --config examples\config.toml %*

echo.
echo [INFO] Работа программы завершена.
pause