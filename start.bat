@echo off
title TechMate Agent - Iniciando...
cd /d "%~dp0"

echo ================================================
echo   TechMate Agent - Iniciando...
echo ================================================

REM Verifica se o .env existe
if not exist ".env" (
    echo [AVISO] Arquivo .env nao encontrado.
    echo Copiando .env.example para .env...
    copy ".env.example" ".env"
    echo Por favor, edite o arquivo .env com sua GEMINI_API_KEY e execute novamente.
    pause
    start notepad ".env"
    exit /b
)

REM Instala dependencias se necessario
echo [1/3] Verificando dependencias...
pip install -r requirements.txt --quiet

REM Abre a CLI em uma nova janela
echo [2/3] Abrindo CLI...
start "TechMate CLI" cmd /k "cd /d "%~dp0" && python main.py"

REM Aguarda 2 segundos e sobe o servidor web
echo [3/3] Iniciando servidor web...
timeout /t 2 /nobreak >nul
start "TechMate Web" cmd /k "cd /d "%~dp0" && python app.py"

REM Aguarda o Flask subir e abre o navegador
timeout /t 3 /nobreak >nul
echo Abrindo navegador em http://localhost:5000
start http://localhost:5000

echo.
echo Tudo iniciado! Feche as janelas para encerrar.
exit
