
#!/bin/bash

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the requirements
pip install -r requirements.txt

# Run the main script
python main.py

# Deactivate the virtual environment
deactivate