@echo off
echo Install.bat Ready for Module Installation.
echo.

echo [Stage 1]
echo Checking for pip installation...


python -m pip --version > nul 2>&1
if %errorlevel% neq 0 (
    echo pip is not installed.
    echo Continue to install pip...
    pause
    echo Installing pip...
    python -m ensurepip
    echo pip installation complete.
) else (
    echo pip is already installed.
)

echo.
echo.
echo [Stage 3]
echo Installing pip...

for /f "tokens=*" %%i in ('python -c "import sys; print(sys.executable)"') do set PYTHON_PATH=%%i
%PYTHON_PATH% -m pip install --upgrade pip


echo [Stage 4]
echo Installing modules for IDLE...
echo Installing packages using IDLE's Python...
for /f "tokens=*" %%i in ('python -c "import sys; print(sys.executable)"') do set PYTHON_PATH=%%i
%PYTHON_PATH% -m pip install -r requirements.txt 
echo.
echo Installation Complete in IDLE.
pause

echo [Stage 5]
echo Installing packages in CMD Python...
for /f "tokens=*" %%i in ('python -c "import sys; print(sys.executable)"') do set CMD_PYTHON_PATH=%%i
%CMD_PYTHON_PATH% -m pip install -r requirements.txt 
echo Installation Complete in terminal.
pause


