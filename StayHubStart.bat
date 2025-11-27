@echo off
setlocal ENABLEEXTENSIONS
chcp 65001 > nul
cd /d "%~dp0"

set "PACKAGE_DIR=%~dp0stayhub_package"
set "CORE_LAUNCHER=%PACKAGE_DIR%\stayhub_launcher.bat"

if not exist "%CORE_LAUNCHER%" (
    echo Не найден основной пакет приложения (%CORE_LAUNCHER%).
    echo Убедитесь, что все файлы распакованы и каталог stayhub_package находится рядом с этим файлом.
    pause
    exit /b 1
)

rem Скрываем служебную папку для красоты (игнорируем ошибки, если права не позволяют).
attrib +h "%PACKAGE_DIR%" > nul 2>&1

if "%~1"=="" (
    echo Запуск StayHub Launcher в новом окне...
    start "StayHub" cmd /k call "%CORE_LAUNCHER%"
) else (
    call "%CORE_LAUNCHER%" %*
)

endlocal
exit /b 0
