@echo off
REM =============================================================
REM  build_portable.bat — Crea la versione portable di ATK-Pro
REM  Uso: build_portable.bat [versione]
REM  Esempio: build_portable.bat 3.0.0-rc1
REM =============================================================

SET VERSION=%1
IF "%VERSION%"=="" SET VERSION=3.0.0-rc1

SET DIST_DIR=dist\ATK-Pro
SET ZIP_NAME=ATK-Pro-v%VERSION%-Windows-Portable.zip

echo.
echo [1/3] Compilazione con PyInstaller (--onedir)...
pyinstaller ATK-Pro.spec
IF ERRORLEVEL 1 (
    echo ERRORE: PyInstaller ha fallito.
    exit /b 1
)

echo.
echo [2/3] Aggiunta file portable.txt nella cartella dist...
copy /Y portable.txt "%DIST_DIR%\portable.txt"
IF ERRORLEVEL 1 (
    echo ERRORE: impossibile copiare portable.txt
    exit /b 1
)

echo.
echo [3/3] Creazione archivio ZIP: %ZIP_NAME%...
powershell -Command "Compress-Archive -Path '%DIST_DIR%' -DestinationPath 'dist\%ZIP_NAME%' -Force"
IF ERRORLEVEL 1 (
    echo ERRORE: impossibile creare lo ZIP.
    exit /b 1
)

echo.
echo ============================================================
echo  Portable pronto: dist\%ZIP_NAME%
echo  Contenuto: cartella ATK-Pro\ con portable.txt incluso
echo ============================================================
