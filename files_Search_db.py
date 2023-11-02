import os
import psutil
import mysql.connector
import csv
from datetime import datetime, timedelta
import logging

# Define the list of file extensions to search for
file_extensions = [".docx",".xlsx", ".xls",".pdf"]  # Add more extensions as needed

# Define patterns to identify sensitive data in file names
sensitive_patterns = ["password", "creditcard"]

# Configure logging to a file
log_file = "error.log"
logging.basicConfig(filename=log_file, level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def get_drives():
    drives = []
    try:
        partitions = psutil.disk_partitions(all=True)  # Include all drives
        for partition in partitions:
            if partition.device:
                drives.append(partition.device)
    except Exception as e:
        # Log the error to the log file
        logging.error(f"Error retrieving drive information: {str(e)}")
    return drives

# Define a custom exception class for file-related errors
class FileError(Exception):
    pass

def is_recently_accessed_or_modified(file_path, n_days):
    try:
        now = datetime.now()
        file_info = os.stat(file_path)
        file_mtime = datetime.fromtimestamp(file_info.st_mtime)
        file_atime = datetime.fromtimestamp(file_info.st_atime)
        delta_mtime = now - file_mtime
        delta_atime = now - file_atime
        return delta_mtime.days <= n_days or delta_atime.days <= n_days
    except Exception as e:
        # Log the error to the log file
        logging.error(f"Error checking file modification/access time: {str(e)}")
        return False

def is_sensitive_file(file_path, sensitive_patterns):
    try:
        file_name = os.path.basename(file_path).lower()
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            file_content = file.read().lower()
        for pattern in sensitive_patterns:
            if pattern in file_name or pattern in file_content:
                return True
    except Exception as e:
        # Log the error to the log file
        logging.error(f"Error checking file for sensitive data: {str(e)}")
    return False

def search_files(root_dir, extensions, n_days, sensitive_patterns):
    found_assets = []
    try:
        for foldername, subfolders, filenames in os.walk(root_dir):
            for filename in filenames:
                if any(filename.lower().endswith(ext) for ext in extensions):
                    file_path = os.path.join(foldername, filename)
                    if is_recently_accessed_or_modified(file_path, n_days) and not is_sensitive_file(file_path, sensitive_patterns):
                        found_assets.append(file_path)
    except Exception as e:
        # Log the error to the log file
        logging.error(f"Error scanning files: {str(e)}")
    return found_assets

def upsert_to_database(file_path, connection):
    cursor = connection.cursor()
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)
    file_extension = os.path.splitext(file_name)[1]
    modification_time = datetime.fromtimestamp(os.path.getmtime(file_path))
    access_time = datetime.fromtimestamp(os.path.getatime(file_path))
    creation_time = datetime.fromtimestamp(os.path.getctime(file_path))

    # Perform an upsert based on file_path
    cursor.execute('''
        INSERT INTO DataAssets (FilePath, FileSize, FileName, FileExtension, ModificationTime, AccessTime, CreationTime)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        FileSize = %s, FileName = %s, FileExtension = %s, ModificationTime = %s, AccessTime = %s, CreationTime = %s;
    ''', (file_path, file_size, file_name, file_extension, modification_time, access_time, creation_time,
        file_size, file_name, file_extension, modification_time, access_time, creation_time))
    connection.commit()

# Define the SQL statement for table creation
create_table_sql = '''
CREATE TABLE IF NOT EXISTS DataAssets (
    FilePath VARCHAR(255) PRIMARY KEY,
    FileSize BIGINT,
    FileName VARCHAR(255),
    FileExtension VARCHAR(10),
    ModificationTime DATETIME,
    AccessTime DATETIME,
    CreationTime DATETIME
);
'''

def create_dataassets_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_sql)
        connection.commit()
        print("DataAssets table created or already exists.")
    except mysql.connector.Error as err:
        logging.error(f"Error creating DataAssets table: {err}")

def get_mysql_credentials():
    host = input("Enter the MySQL host (default value: '127.0.0.1' or 'localhost'): ")
    port = input("Enter the MySQL port (default port: 3306): ")
    database_name = input("Enter the database name: ")
    username = input("Enter the MySQL username: ")
    password = input("Enter the MySQL password: ")
    return host, port, database_name, username, password

if __name__ == "__main__":
    drives = get_drives()
    if not drives:
        print("No drives found.")
    else:
        print("Available drives:")
        for i, drive in enumerate(drives, start=1):
            print(f"{i}. {drive}")

        scan_option = input("Choose an option:\n1. Full Scan\n2. Drive-specific Scan\nEnter the option number (1 or 2): ")

        try:
            if scan_option == '1':
                n_days = int(input("Enter the number of days to consider for file modification: "))
                print(f"Performing a full scan for data assets modified or accessed in the last {n_days} days:")
                found_assets = []
                for drive in drives:
                    found_assets.extend(search_files(drive, file_extensions, n_days, sensitive_patterns))
            elif scan_option == '2':
                drive_choice = input("Enter the drive letter to scan (e.g., C, D, E, ...): ").upper()
                if drive_choice in [d[0] for d in drives]:
                    n_days = int(input("Enter the number of days to consider for file modification: "))
                    selected_drive = [d for d in drives if d[0] == drive_choice][0]
                    print(f"Scanning {selected_drive} for data assets modified or accessed in the last {n_days} days:")
                    found_assets = search_files(selected_drive, file_extensions, n_days, sensitive_patterns)
                else:
                    print("Invalid drive choice.")
                    found_assets = []
            else:
                print("Invalid option. Please choose 1 for Full Scan or 2 for Drive-specific Scan.")
                found_assets = []

        except ValueError:
            print("Invalid input. Please enter a valid option or drive letter.")

        # Get MySQL user credentials
        host, port, database_name, username, password = get_mysql_credentials()

        connection = None
        try:
            connection = mysql.connector.connect(
                host=host,
                port=port,
                database=database_name,
                user=username,
                password=password
            )
            # Create the DataAssets table if it doesn't exist
            create_dataassets_table(connection)

            if found_assets:
                for asset in found_assets:
                    upsert_to_database(asset, connection)
                print(f"Scan results for the last {n_days} days saved to the MySQL database.")
            else:
                print("No data assets found.")
        except Exception as e:
            # Log the error to the log file
            logging.error(f"Error connecting to the database: {str(e)}")
        finally:
            if connection:
                connection.close()