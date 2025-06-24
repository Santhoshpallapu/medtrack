@echo off

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

:: Install requirements
echo Installing required packages...
pip install -r requirements.txt

:: Start the application
echo Starting MedTrack application...
python app_local.py

pause
