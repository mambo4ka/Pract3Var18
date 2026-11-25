@echo off
cd /d "%~dp0"
if "%~1"=="" (
    python src\assembler.py tests\data\test.asm output.bin --test
) else (
    python src\assembler.py %*
)

echo.
pause