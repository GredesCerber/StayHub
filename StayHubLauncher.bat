@echo off
setlocal ENABLEEXTENSIONS
chcp 65001 > nul

set "ROOT_DIR=%~dp0"
set "PACKAGE_DIR=%ROOT_DIR%stayhub_package"
set "CORE_LAUNCHER=%PACKAGE_DIR%\stayhub_launcher.bat"

if not exist "%CORE_LAUNCHER%" (
    echo Не найден файл ^"%CORE_LAUNCHER%^".
    echo Убедитесь, что каталог stayhub_package находится рядом с StayHubLauncher.bat.
    pause
    exit /b 1
)

cd /d "%PACKAGE_DIR%"
call "%CORE_LAUNCHER%" %*
endlocal
