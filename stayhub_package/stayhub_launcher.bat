@echo off
setlocal ENABLEEXTENSIONS
chcp 65001 > nul
cd /d "%~dp0"

set "VENV_PYTHON=%~dp0venv\Scripts\python.exe"
set "PYTHON_CMD=python"
if exist "%VENV_PYTHON%" (
    set "PYTHON_CMD=%VENV_PYTHON%"
)

set "DB_FILE=stayhub.db"

if /I "%~1"=="db" (
    call :open_db
    goto end
)
if /I "%~1"=="seed" (
    call :seed_db
    goto end
)
if /I "%~1"=="reset" (
    call :reset_db
    goto end
)
if /I "%~1"=="server" (
    call :start_server
    goto end
)

:menu
cls
echo ===============================
echo         StayHub Launcher
echo ===============================
echo [1] Запустить сервер (откроется браузер)
echo [2] Заполнить базу демонстрационными данными
echo [3] Открыть базу в консоли SQLite
echo [4] Очистить базу (удалить stayhub.db)
echo [5] Выход
echo.
set /p "CHOICE=Выберите пункт и нажмите Enter: "
if "%CHOICE%"=="1" (
    call :start_server
    goto menu
)
if "%CHOICE%"=="2" (
    call :seed_db
    goto menu
)
if "%CHOICE%"=="3" (
    call :open_db
    goto menu
)
if "%CHOICE%"=="4" (
    call :reset_db
    goto menu
)
if "%CHOICE%"=="5" goto end
goto menu

:start_server
call :ensure_python
if errorlevel 1 exit /b 1
if not exist "%DB_FILE%" (
    echo Файл базы "%DB_FILE%" не найден. Он будет создан автоматически при запуске сервера.
    echo Если нужны демонстрационные данные, воспользуйтесь пунктом 2 меню перед запуском.
)
echo Запуск сервера StayHub...
start "StayHub Server" "%PYTHON_CMD%" -m uvicorn app.main:app --reload
timeout /t 2 > nul
start "" http://localhost:8000
echo Сервер запущен в отдельном окне. Закрыть его можно крестиком или CTRL+C.
pause
exit /b 0

:seed_db
call :ensure_python
if errorlevel 1 exit /b 1
echo Заполнение базы демонстрационными данными...
"%PYTHON_CMD%" seed_data.py
if errorlevel 0 (
    echo Данные загружены успешно.
) else (
    echo Произошла ошибка при заполнении базы.
)
pause
exit /b 0

:open_db
call :ensure_python
if errorlevel 1 exit /b 1
if not exist "%DB_FILE%" (
    echo Файл базы "%DB_FILE%" не найден. Сначала заполните её пунктом 2.
    pause
    exit /b 1
)
echo Открываем SQLite-консоль в новом окне. Для выхода используйте .quit.
start "StayHub SQLite" "%PYTHON_CMD%" -m sqlite3 "%DB_FILE%"
pause
exit /b 0

:reset_db
if not exist "%DB_FILE%" (
    echo Файл базы "%DB_FILE%" уже отсутствует — ничего удалять не нужно.
    pause
    exit /b 0
)
set /p "CONFIRM=Удалить файл %DB_FILE%? Это действие нельзя отменить (y/n): "
if /I not "%CONFIRM%"=="Y" (
    echo Очистка отменена.
    pause
    exit /b 0
)
del /f /q "%DB_FILE%" > nul 2>&1
if exist "%DB_FILE%" (
    echo Не удалось удалить базу. Проверьте, не используется ли файл другим процессом.
    pause
    exit /b 1
)
echo База успешно удалена. Теперь можно заново заполнить демонстрационными данными.
pause
exit /b 0

:ensure_python
if exist "%VENV_PYTHON%" (
    exit /b 0
)
where python > nul 2>&1
if errorlevel 1 (
    echo Не найден интерпретатор Python. Установите Python или создайте виртуальное окружение.
    pause
    exit /b 1
)
exit /b 0

:end
endlocal
exit /b 0
