
param (
    [string]$RemoteVM,
    [string]$RemotePath = "C:\Path\To\Remote\Scripts"
)

# Copy the necessary files to the remote VM
Write-Output "Copying files to remote VM..."
Copy-Item -Path .\* -Destination "\\$RemoteVM\$RemotePath" -Recurse -Force

# Run the script on the remote VM
Write-Output "Running script on remote VM..."
Invoke-Command -ComputerName $RemoteVM -ScriptBlock {
    param ($RemotePath)
    cd $RemotePath
    Write-Output "Creating virtual environment..."
    python -m venv venv

    Write-Output "Activating virtual environment..."
    .\venv\Scripts\Activate

    Write-Output "Upgrading pip..."
    pip install --upgrade pip

    Write-Output "Installing requirements..."
    pip install -r requirements.txt

    Write-Output "Upgrading installed packages..."
    pip list --outdated --format=freeze | ForEach-Object {
        $package = $_.Split('==')[0]
        pip install --upgrade $package
    }

    Write-Output "Running main script..."
    python main.py

    Write-Output "Deactivating virtual environment..."
    Deactivate

    Write-Output "Done."
} -ArgumentList $RemotePath

Write-Output "Script execution completed on remote VM."