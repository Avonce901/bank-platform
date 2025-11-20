@echo off
REM Banking Platform - One-Click Railway Deployment
REM This script automates the full Railway deployment process

setlocal enabledelayedexpansion

echo.
echo ======================================================================
echo BANKING PLATFORM - RAILWAY DEPLOYMENT
echo ======================================================================
echo.
echo This script will deploy your banking API to Railway.app
echo.
echo Prerequisites:
echo   1. Railway.app account (https://railway.app)
echo   2. GitHub connected to Railway
echo   3. Railway CLI installed (optional but recommended)
echo.
echo ======================================================================
echo.

REM Check if Railway CLI is installed
where railway >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Railway CLI not found. You can still deploy manually:
    echo.
    echo Option 1: Use Railway Dashboard (No CLI needed)
    echo   1. Visit https://railway.app
    echo   2. Click "New Project" ^> "Deploy from GitHub"
    echo   3. Select "Avonce901/bank-platform"
    echo   4. Click Deploy
    echo.
    echo Option 2: Install Railway CLI
    echo   npm install -g @railway/cli
    echo.
    echo Then run this script again!
    echo.
    pause
    exit /b 1
)

echo ✅ Railway CLI found!
echo.
echo Step 1: Logging in to Railway...
call railway login

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Railway login failed!
    pause
    exit /b 1
)

echo ✅ Logged in successfully!
echo.
echo Step 2: Creating project...
call railway project create bank-platform --name "Banking Platform API"

if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Project may already exist, continuing...
)

echo.
echo Step 3: Linking GitHub repository...
call railway link Avonce901/bank-platform

if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Repository linking skipped, using current directory...
)

echo.
echo Step 4: Deploying to Railway...
call railway up

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Deployment failed!
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo 🎉 DEPLOYMENT COMPLETE!
echo ======================================================================
echo.
echo Your Banking Platform is now live on Railway!
echo.
echo Next steps:
echo   1. Get your deployment URL:
echo      railway env
echo   2. Test your API:
echo      curl YOUR_URL/health
echo   3. View logs:
echo      railway logs
echo.
echo For more info, visit: https://docs.railway.app
echo.
pause
