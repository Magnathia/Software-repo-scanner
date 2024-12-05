Write-Output "Checking for existing virtual environment..."
if (-Not (Test-Path -Path "./venv")) {
    Write-Output "Creating virtual environment..."
    # Create a virtual environment
    python -m venv venv
} else {
    Write-Output "Virtual environment already exists."
}

Write-Output "Activating virtual environment..."
# Activate the virtual environment
. .\venv\Scripts\Activate  # Note the dot and space before the path

Write-Output "Upgrading pip..."
# Upgrade pip
pip install --upgrade pip

Write-Output "Installing requirements..."
# Install the requirements
pip install -r requirements.txt

Write-Output "Upgrading installed packages..."
# Upgrade installed packages
pip list --outdated --format=freeze | ForEach-Object {
    $package = $_.Split('==')[0]
    pip install --upgrade $package
}

Write-Output "Running main script..."
# Run the main script
python main.py

Write-Output "Deactivating virtual environment..."
# Deactivate the virtual environment
deactivate  # Note the lowercase 'd'

Write-Output "Done."