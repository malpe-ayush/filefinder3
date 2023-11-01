import os
import psutil
import mysql.connector  # Use the 'mysql-connector-python' package
import csv

# Define the list of file extensions to search for
file_extensions = [".xlsx", ".xls",".pdf",".exe"]  # Add more extensions as needed

# Define your MySQL database connection details
host = "localhost"  # Replace with the MySQL server address
port = 3306  # Replace with the MySQL server port
database_name = "malhar"
username = "root"
password = "Acc.sql@20"

# Define a function to search for files with specific extensions on the selected drive
def search_files(drive, extensions):
    found_assets = []
    for root, _, files in os.walk(drive):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                found_assets.append(os.path.join(root, file))
    return found_assets

def get_drives():
    drives = []
    partitions = psutil.disk_partitions(all=False)
    for partition in partitions:
        if partition.device:
            drives.append(partition.device)
    return drives

# Modify this function to insert data into a MySQL database
def upsert_to_database(data_assets, connection):
    cursor = connection.cursor()
    for asset in data_assets:
        file_path = asset
        # Perform an upsert (insert or update) based on file_path
        # Replace the query with your MySQL-specific upsert statement
        cursor.execute('''
            INSERT INTO DataAssets (FilePath) VALUES (%s)
            ON DUPLICATE KEY UPDATE FilePath = %s;
        ''', (file_path, file_path))
    connection.commit()

if __name__ == "__main__":
    drives = get_drives()
    if not drives:
        print("No drives found.")
    else:
        print("Available drives:")
        for i, drive in enumerate(drives, start=1):
            print(f"{i}. {drive}")
        
        user_choice = input("Enter the drive number you want to scan (e.g., 1, 2, ...): ")
        
        try:
            user_choice = int(user_choice)
            if 1 <= user_choice <= len(drives):
                selected_drive = drives[user_choice - 1]
                
                print(f"Scanning {selected_drive} for data assets:")
                found_assets = search_files(selected_drive, file_extensions)
                
                # Connect to the MySQL database
                connection = mysql.connector.connect(
                    host=host,
                    port=port,
                    database=database_name,
                    user=username,
                    password=password
                )

                # Create the DataAssets table if it doesn't exist
                cursor = connection.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS DataAssets (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        FilePath VARCHAR(255) NOT NULL,
                        UNIQUE (FilePath)
                    );
                ''')

                # Upsert the data to the database
                upsert_to_database(found_assets, connection)

                print("Scan results saved to MySQL database.")
                connection.close()
            else:
                print("Invalid drive number.")
        except ValueError:
            print("Invalid input. Please enter a valid drive number.")
