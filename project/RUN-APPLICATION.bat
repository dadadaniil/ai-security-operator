@echo off
REM --- Configuration ---
REM The name of the external network your docker-compose.yml file expects.
REM Change this value if your network is named something different.
set "NETWORK_NAME=application_network"


REM --- Script Logic ---
echo Checking for Docker network: %NETWORK_NAME%

REM Check if the network already exists by piping the list to findstr.
REM We redirect the output of findstr to NUL to keep the console clean.
docker network ls | findstr /C:"%NETWORK_NAME%" > NUL

REM Check the result. If findstr finds the string, ERRORLEVEL is 0.
if %ERRORLEVEL% == 0 (
    echo Network '%NETWORK_NAME%' already exists.
) else (
    echo Network '%NETWORK_NAME%' not found. Creating it now...

    REM Create the network
    docker network create "%NETWORK_NAME%"

    REM Optional: Add a check to ensure the network was created successfully
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to create network '%NETWORK_NAME%'. Aborting script.
        goto :eof
    )
    echo Network '%NETWORK_NAME%' created successfully.
)

echo.
echo Starting Docker Compose services...
docker-compose up --build

echo Script finished.