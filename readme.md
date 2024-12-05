# Software Inventory

This project inventories software from specified directories, saves the information to a SQLite database, and generates a report of any changes in software checksums. It includes scripts for setting up the environment and running the main inventory script.

## Description

- **main.py**: Scans specified directories for installer files, calculates their checksums, and saves the information to a SQLite database. It also generates a report of any changes in checksums.
- **run.ps1**: Sets up a Python virtual environment, installs required packages, upgrades outdated packages, runs the main Python script, and then deactivates the virtual environment.


## Requirements

- Python 3.x
- PowerShell
- Required Python packages (listed in `requirements.txt`)


## Usage

1. **Prepare the `sources.txt` file**:
    - Create a `sources.txt` file in the project directory.
    - List the directories you want to scan, one per line. For example:
      ```
      C:/Users/rsmith/Downloads
      C:/Users/rsmith/Desktop/Installers
      /Users/rsmith/Applications
      ```

2. **Run the inventory script**:
    ```sh
    .\run.ps1
    ```

3. **Check the generated report**:
    - The report will be generated as `report.html` in the project directory.



## License

This project is licensed under the MIT License.