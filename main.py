import os
import platform
import sqlite3
from datetime import datetime
from tqdm import tqdm
import socket
import logging
import hashlib  # Add this import for checksum calculation
from concurrent.futures import ThreadPoolExecutor, as_completed  # Add this import for parallel processing
import re  # Add this import for sanitizing table names

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Remove the get_installer_version function as it's no longer needed

def calculate_checksum(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logging.error(f"Error calculating checksum for {file_path}: {e}")
        return None

def process_file(file_path):
    checksum = calculate_checksum(file_path)
    if checksum:
        last_modified = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        return {'location': file_path, 'checksum': checksum, 'last_modified': last_modified}
    else:
        logging.warning(f"Could not determine checksum for {file_path}")
        return None

def is_network_path_accessible(path, timeout=5):
    try:
        host = path.split('\\')[2]
        socket.setdefaulttimeout(timeout)
        socket.gethostbyname(host)
        return True
    except Exception as e:
        logging.error(f"Network path {path} is not accessible: {e}")
        return False

def sanitize_table_name(name):
    # Replace invalid characters with underscores
    sanitized_name = re.sub(r'\W|^(?=\d)', '_', name)
    return sanitized_name

def inventory_software(directories):
    software_catalog = {}
    for directory in directories:
        if not is_network_path_accessible(directory):
            logging.warning(f"Skipping inaccessible directory: {directory}")
            continue
        logging.info(f'Scanning directory: {directory}')
        try:
            with ThreadPoolExecutor() as executor:
                futures = []
                for root, _, files in os.walk(directory):
                    for file in files:
                        if file.endswith(('.exe', '.msi', '.dmg', '.pkg')):
                            file_path = os.path.join(root, file)
                            futures.append(executor.submit(process_file, file_path))
                for future in tqdm(as_completed(futures), total=len(futures), desc=f"Processing {directory}", unit="file"):
                    result = future.result()
                    if result:
                        software_catalog[os.path.basename(result['location'])] = result
        except Exception as e:
            logging.error(f"Error scanning directory {directory}: {e}")
    return software_catalog

def save_to_database(catalog, directory, db_path='software_inventory.db'):
    table_name = sanitize_table_name(os.path.basename(os.path.normpath(directory)))
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            checksum TEXT,
            last_update TEXT
        )
    ''')
    changes = []
    for software, details in catalog.items():
        cursor.execute(f'''
            SELECT checksum FROM {table_name} WHERE name = ? AND location = ?
        ''', (software, details['location']))
        result = cursor.fetchone()
        if result:
            if result[0] != details['checksum']:
                changes.append((software, details['location'], result[0], details['checksum']))
        cursor.execute(f'''
            INSERT OR REPLACE INTO {table_name} (name, location, checksum, last_update)
            VALUES (?, ?, ?, ?)
        ''', (software, details['location'], details['checksum'], details['last_modified']))
    conn.commit()
    conn.close()
    return changes

def generate_report(changes, report_path='report.html'):
    with open(report_path, 'w') as report_file:
        report_file.write('<html><body><h1>Software Changes Report</h1><ul>')
        for change in changes:
            report_file.write(f'<li>{change[0]} at {change[1]}: Checksum changed from {change[2]} to {change[3]}</li>')
        report_file.write('</ul></body></html>')
    logging.info(f'Report generated: {report_path}')

def main():
    with open('sources.txt', 'r') as file:
        directories = [line.strip() for line in file.readlines() if line.strip()]
    all_changes = []
    for directory in tqdm(directories, desc="Processing directories", unit="directory"):
        catalog = inventory_software([directory])
        for software, details in catalog.items():
            logging.info(f'{software}: Location: {details["location"]}, Checksum: {details["checksum"]}, Last Modified: {details["last_modified"]}')
        changes = save_to_database(catalog, directory)
        all_changes.extend(changes)
    if all_changes:
        generate_report(all_changes)
    else:
        logging.info('No changes detected.')

if __name__ == "__main__":
    main()
