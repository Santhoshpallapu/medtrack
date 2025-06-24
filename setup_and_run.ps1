Write-Host "Creating virtual environment..."
python -m venv venv

Write-Host "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

Write-Host "Installing required packages..."
pip install -r requirements.txt

Write-Host "Starting MedTrack application..."
python app_local.py

Write-Host "Press any key to exit..."
Read-Host