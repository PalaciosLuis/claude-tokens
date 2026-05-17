@echo off
setlocal enabledelayedexpansion

set PYTHON=

:: Try py launcher first (installed with official Python)
where py >nul 2>&1
if not errorlevel 1 (
    py -m pip --version >nul 2>&1
    if not errorlevel 1 ( set PYTHON=py & goto :found )
)

:: Try python
where python >nul 2>&1
if not errorlevel 1 (
    python -m pip --version >nul 2>&1
    if not errorlevel 1 ( set PYTHON=python & goto :found )
)

:: Try python3
where python3 >nul 2>&1
if not errorlevel 1 (
    python3 -m pip --version >nul 2>&1
    if not errorlevel 1 ( set PYTHON=python3 & goto :found )
)

:: Try pyenv-win
if exist "%USERPROFILE%\.pyenv\pyenv-win\versions\" (
    for /d %%v in ("%USERPROFILE%\.pyenv\pyenv-win\versions\*") do (
        if exist "%%v\python.exe" (
            "%%v\python.exe" -m pip --version >nul 2>&1
            if not errorlevel 1 ( set PYTHON=%%v\python.exe & goto :found )
        )
    )
)

echo No Python 3 with pip found.
echo Download and install Python from https://python.org
echo Make sure to check "Add Python to PATH" during installation.
pause
exit /b 1

:found
echo Using: !PYTHON!

:: Install rich if missing
!PYTHON! -c "import rich" >nul 2>&1
if errorlevel 1 (
    echo Installing rich...
    !PYTHON! -m pip install rich --quiet
)

!PYTHON! "%~dp0claude-tokens.py"
pause
