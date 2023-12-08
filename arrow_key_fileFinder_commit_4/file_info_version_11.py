import os
import pandas as pd
import psutil
import mysql.connector
import csv
from datetime import datetime, timedelta
import logging
import xlrd
from dotenv import load_dotenv
import platform
load_dotenv()
import time
import socket
from questionary import select
from rich import print
import keyboard
import subprocess
import win32api
import win32con
import win32security

# Define the list of file extensions to search for
file_extensions = os.getenv("FILE_NAME_INFO_FILE_EXTENSIONS").split(",")  # Add more extensions as needed

# Define patterns to identify sensitive data in file names
sensitive_patterns = os.getenv("FILE_PATH_SCAN_SENSITIVE_PATTERNS").split(",")

# Define your MySQL database connection details
host = os.getenv("MYSQL_HOST")  # Replace with the MySQL server address
port = os.getenv("MYSQL_PORT")  # Replace with the MySQL server port
database_name = os.getenv("MYSQL_DATABASE")
username = os.getenv("MYSQL_USERNAME")
password = os.getenv("MYSQL_PASSWORD")
n_days = int(os.getenv("N_DAYS"))

# Configure logging to a file
log_file = "error.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# def operating_system():
#     ops=input("Enter 1 for Windows and 2 for Linux")

def get_ip_address():
    try:
        # Check the operating system
        system_name = platform.system()
        
        if system_name == 'Linux':
            # Run the 'hostname -I' command and capture the output
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
            
            # Extract the IP address from the command output
            ip_addresses = result.stdout.strip().split()
            
            # Return the first IP address in the list
            if ip_addresses:
                return ip_addresses[0]
            else:
                return None
        elif system_name == 'Windows':
            # For Windows, use a different method to get the local IP address
            return socket.gethostbyname(socket.gethostname())
        else:
            print(f"Unsupported operating system: {system_name}")
            return None
    except Exception as e:
        print(f"Error getting IP address: {str(e)}")
        return None

def get_removable_drives():
    removable_drives = []

    for partition in psutil.disk_partitions():
        if 'removable' in partition.opts or 'cdrom' in partition.opts:
            removable_drives.append(partition.device)

    return removable_drives

def get_drives():
    all_drives = []
    try:
        partitions = psutil.disk_partitions(all=True)  # Include all drives
        for partition in partitions:
            if partition.device:
                all_drives.append(partition.device)
    except Exception as e:
        # Log the error to the log file
        logging.error(f"Error retrieving drive information: {str(e)}", exc_info=True)
    return all_drives


# Define a cuhostname = socket.gethostname()  stom exception class for file-related errors
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
        logging.error(f"Error checking file modification/access time: {str(e)}", exc_info=True)
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
        logging.error(f"Error checking file for sensitive data: {str(e)}", exc_info=True)
    return False


def search_files(root_dir, extensions, n_days, sensitive_patterns):
    found_assets = []
    try:
        for foldername, subfolders, filenames in os.walk(root_dir):
            for filename in filenames:
                if os.getenv("FILE_NAME_INFO_FILE_EXTENSIONS").lower()=="all":
                    file_path = os.path.join(foldername, filename)
                    if is_recently_accessed_or_modified(file_path, n_days) and not is_sensitive_file(file_path,
                                                                                                     sensitive_patterns):
                        found_assets.append(file_path)
                else:
                    if any(filename.lower().endswith(ext) for ext in extensions):
                        file_path = os.path.join(foldername, filename)
                        if is_recently_accessed_or_modified(file_path, n_days) and not is_sensitive_file(file_path,
                                                                                                        sensitive_patterns):
                            found_assets.append(file_path)
    except Exception as e:
        # Log the error to the log file
        logging.error(f"Error scanning files: {str(e)}", exc_info=True)
    return found_assets

def get_owner_name_windows(file_path):
  sd = win32security.GetFileSecurity(file_path, win32security.OWNER_SECURITY_INFORMATION)
  owner_sid = sd.GetSecurityDescriptorOwner()
  name, domain, type = win32security.LookupAccountSid(None, owner_sid)
  return f"{domain}\\{name}"

def upsert_to_database(file_path, connection, employee_username, start_time):
    if platform.system()=="Windows":
        get_owner_name = get_owner_name_windows
        owner_name = get_owner_name_windows(file_path)
    elif platform.system()=="Linux":
        import pwd
        stat_info = os.stat(file_path)
        owner_uid = stat_info.st_uid
        owner_name = pwd.getpwuid(owner_uid).pw_name
    
    hostname = socket.gethostname()
    ipaddrs = socket.gethostbyname(hostname)
    cursor = connection.cursor()
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)
    file_extension = os.path.splitext(file_name)[1]
    modification_time = datetime.fromtimestamp(os.path.getmtime(file_path))
    access_time = datetime.fromtimestamp(os.path.getatime(file_path))
    creation_time = datetime.fromtimestamp(os.path.getctime(file_path))

    # Perform an upsert based on file_path
    cursor.execute('''
        INSERT INTO file_name_info (machine_info_for_search_fk, ip_address,hostname,file_path, file_size_bytes, file_name, file_extension,file_owner,file_creation_time, file_modification_time, file_last_access_time, row_creation_date_time, row_created_by,row_modification_date_time,row_modification_by)
        VALUES ((SELECT machine_info_for_search_pk FROM machine_info_for_search WHERE hostname = %s), %s,%s,%s, %s, %s, %s,%s, %s, %s, %s,FROM_UNIXTIME(%s),%s,FROM_UNIXTIME(%s),%s)
        ON DUPLICATE KEY UPDATE
        file_size_bytes = %s, row_modification_date_time = FROM_UNIXTIME(%s),row_modification_by=%s ;
    ''', (
        hostname, ipaddrs, hostname, file_path, file_size, file_name, file_extension,owner_name, creation_time, modification_time,
        access_time, start_time, employee_username, start_time, employee_username,
        file_size, start_time, employee_username))
    connection.commit()


def create_xls_file_sheet_table(connection, xls_files):
    try:
        cursor = connection.cursor()
        for xls_file in xls_files:
            # workbook = xlrd.open_workbook(xls_file)
            xls_data = pd.read_excel(xls_file, sheet_name=None)  # Read all sheets

            for sheet_name, sheet in xls_data.items():
                num_rows, num_cols = sheet.shape

                # Create the xls_file_sheet table
                # cursor.execute(f'''
                #     CREATE TABLE IF NOT EXISTS xls_file_sheet (
                #         xls_file_sheet_pk INT AUTO_INCREMENT PRIMARY KEY,
                #         file_name_info_fk INT ,
                #         sheet_name VARCHAR(255),
                #         total_cols INT,
                #         total_rows INT,
                #         UNIQUE KEY unique_file_sheet (file_name_info_fk, sheet_name),
                #         FOREIGN KEY (file_name_info_fk) REFERENCES file_name_info(file_name_info_pk)
                #     );
                # ''')
                # connection.commit()
                cursor.execute('''
                INSERT INTO xls_file_sheet (file_name_info_fk, sheet_name, total_cols, total_rows)
                VALUES (
                    (SELECT file_name_info_pk FROM file_name_info WHERE file_path = %s),
                    %s, %s, %s
                )ON DUPLICATE KEY UPDATE
                               total_cols=VALUES(total_cols),
                               total_rows=VALUES(total_rows);

                ''', (xls_file, sheet_name, num_cols, num_rows))
                connection.commit()
        print("[bright_green]Data inserted into xls_file_sheet table.[/bright_green]")
    except Exception as e:
        logging.error(f"Error creating .xls file tables and inserting data: {str(e)}", exc_info=True)


# Function to create a new table for .xls file rows
def create_xls_file_sheet_row_table(connection, xls_files):
    try:
        cursor = connection.cursor()
        for xls_file in xls_files:
            xls_data = pd.read_excel(xls_file, sheet_name=None, header=None)  # Read all sheets

            for sheet_name, sheet in xls_data.items():
                num_rows, num_cols = sheet.shape

                # Create the xls_file_sheet_row table
                # cursor.execute(f'''
                #     CREATE TABLE IF NOT EXISTS xls_file_sheet_row (
                #         xls_file_sheet_row_pk INT AUTO_INCREMENT PRIMARY KEY,
                #         xls_file_sheet_fk INT,
                #         sheet_name VARCHAR(255),
                #         col_no INT,
                #         row_no INT,
                #         is_row VARCHAR(3),
                #         col_data_1 VARCHAR(255),
                #         col_data_2 VARCHAR(255),
                #         col_data_3 VARCHAR(255),
                #         col_data_4 VARCHAR(255),
                #         col_data_5 VARCHAR(255),
                #         col_data_6 VARCHAR(255),
                #         col_data_7 VARCHAR(255),
                #         col_data_8 VARCHAR(255),
                #         col_data_9 VARCHAR(255),
                #         col_data_10 VARCHAR(255),
                #         is_truncate VARCHAR(3),
                #         UNIQUE KEY unique_file_sheet (xls_file_sheet_fk, sheet_name,row_no),
                #         FOREIGN KEY (xls_file_sheet_fk) REFERENCES xls_file_sheet(xls_file_sheet_pk)
                #     );
                # ''')
                # connection.commit()

                # Insert the first 10 columns of data into the table, or all if there are fewer than 10 columns
                for row_idx in range(min(int(os.getenv("ENABLE_EXCEL_FILE_DATA_SCAN_MIN_ROW")), num_rows)):  # Read up to the first 3 rows
                    is_row = "no" if row_idx == 0 else "yes"  # First row is a heading, the rest are data
                    col_data = sheet.iloc[row_idx, :10].tolist()  # Take the first 10 columns
                    col_data.extend(["NULL"] * (10 - len(col_data)))  # Fill the remaining columns with "NULL"
                    col_data = [str(data)[:255] for data in col_data]  # Truncate data if necessary
                    # Check for truncation if there are more than 10 columns
                    is_truncate = "yes" if num_cols > 10 else "no"

                    cursor.execute(f'''
                                        INSERT INTO xls_file_sheet_row (xls_file_sheet_fk, sheet_name, col_no, row_no, is_row,
                                        col_data_1, col_data_2, col_data_3, col_data_4, col_data_5,
                                        col_data_6, col_data_7, col_data_8, col_data_9, col_data_10, is_truncate)
                                        VALUES (
                                        (
                                        SELECT xls_file_sheet_pk 
                                        FROM xls_file_sheet 
                                        WHERE sheet_name = %s AND file_name_info_fk = (
                                        SELECT file_name_info_pk
                                        FROM file_name_info 
                                        WHERE file_path = %s LIMIT 1

                                        ) LIMIT 1
                                        ),
                                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                                        )ON DUPLICATE KEY UPDATE
                                                   xls_file_sheet_fk=VALUES(xls_file_sheet_fk),
                                                   sheet_name=VALUES(sheet_name),
                                                   col_no=VALUES(col_no),
                                                   row_no=VALUES(row_no),
                                                   col_data_1=VALUES(col_data_1),
                                                   col_data_2=VALUES(col_data_2),
                                                       col_data_3=VALUES(col_data_3),
                                                       col_data_4=VALUES(col_data_4),
                                                       col_data_5=VALUES(col_data_5),
                                                       col_data_6=VALUES(col_data_6),
                                                       col_data_7=VALUES(col_data_7),
                                                       col_data_8=VALUES(col_data_8),
                                                       col_data_9=VALUES(col_data_9),
                                                       col_data_10=VALUES(col_data_10);
                                        ''', (
                        sheet_name, xls_file, sheet_name, num_cols, row_idx + 1, is_row, *col_data, is_truncate))
                    connection.commit()
        print("[bright_green]Data inserted into xls_file_sheet_row table.[/bright_green]")
    except Exception as e:
        logging.error(f"Error creating .xls file row tables and inserting data: {str(e)}", exc_info=True)


# function for audit table
def create_audit_table(connection, EmployeeUserName, ip, start_time, end_time, elapsed_time, scan):
    if scan == "File Count":
        scan = 'Count'
    activity = 'Completed'
    try:
        cursor = connection.cursor()

        # cursor.execute('''
        #     CREATE TABLE IF NOT EXISTS audit_info (
        #         pc_ip_address TEXT,
        #         start_time TIMESTAMP,
        #         end_time TIMESTAMP,
        #         duration TEXT
        #     );
        # ''')
        # connection.commit()

        cursor.execute('''
            INSERT INTO audit_info (machine_info_for_search_fk,pc_ip_address ,employee_username, start_time,end_time, duration,filefinder_activity,activity_status)
            VALUES ((SELECT machine_info_for_search_pk FROM machine_info_for_search WHERE ip_address= %s),%s, %s, FROM_UNIXTIME(%s), FROM_UNIXTIME(%s), %s,%s,%s);
        ''', (ip, ip, EmployeeUserName, start_time, end_time, end_time - start_time, scan, activity))
        connection.commit()
        print("[bright_green]Data inserted into audit_info table.[/bright_green]")
    except Exception as e:
        logging.error(f"Error creating audit table and inserting data: {str(e)}", exc_info=True)


def insert_machine_info_for_search(connection, ipaddress, hostname, ops, os_name, os_version, system_info):
    if ops == "Windows":
        drives = get_drives()
        drive_names = str(drives)
        total_files = 0
        total_excel_files = 0
        total_pdf_files = 0
        total_word_files = 0
        total_zip_files = 0
        for drive in drives:
            total_files += count_all_files(drive)
            total_excel_files += count_files_with_extension(drive, ".xls") + count_files_with_extension(drive, ".xlsx")
            total_word_files += count_files_with_extension(drive, ".docx") + count_files_with_extension(drive, ".doc")
            total_pdf_files += count_files_with_extension(drive, ".pdf")
            total_zip_files += count_files_with_extension(drive, ".zip")

    elif ops == "Linux":
        # For Linux, set number_of_drives and name_of_drives to NULL
        drives = None
        drive_names = None
        total_files = count_all_files("/")
        total_excel_files = count_files_with_extension("/", ".xls") + count_files_with_extension("/", ".xlsx")
        total_word_files = count_files_with_extension("/", ".docx") + count_files_with_extension("/", ".doc")
        total_pdf_files = count_files_with_extension("/", ".pdf")
        total_zip_files = count_files_with_extension("/", ".zip")
    else:
        print("Incorrect input")
        return 0

    try:
        cursor = connection.cursor()

        # Extract relevant information from system_info
        system_info_str = " ".join(str(info) for info in system_info)
        system_info_str = system_info_str[:255]  # Truncate to fit in VARCHAR(255)

        # Handle the case when drives is None
        if drives is None:
            cursor.execute('''
                    INSERT INTO machine_info_for_search (hostname, ip_address, os_name, os_version, system_info, number_of_drives, name_of_drives, total_n_files, total_n_excel, total_n_pdf, total_n_word, total_n_zip)
                    VALUES (%s, %s, %s, %s, %s, NULL, NULL, %s, %s, %s,%s,%s) ON DUPLICATE KEY UPDATE
                           total_n_files=VALUES(total_n_files),
                           total_n_excel=VALUES(total_n_excel),
                           total_n_pdf=VALUES(total_n_pdf),
                           total_n_word=VALUES(total_n_word),
                           total_n_zip=VALUES(total_n_zip);
                ''', (
                hostname, ipaddress, os_name, os_version, system_info_str, total_files,
                total_excel_files, total_pdf_files, total_word_files, total_zip_files))
        else:
            cursor.execute('''
                    INSERT INTO machine_info_for_search (hostname, ip_address, os_name, os_version, system_info, number_of_drives, name_of_drives, total_n_files, total_n_excel, total_n_pdf, total_n_word, total_n_zip)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s) ON DUPLICATE KEY UPDATE
                           total_n_files=VALUES(total_n_files),
                           total_n_excel=VALUES(total_n_excel),
                           total_n_pdf=VALUES(total_n_pdf),
                           total_n_word=VALUES(total_n_word),
                           total_n_zip=VALUES(total_n_zip);
                ''', (
                hostname, ipaddress, os_name, os_version, system_info_str, len(drives), drive_names, total_files,
                total_excel_files, total_pdf_files, total_word_files, total_zip_files))

        connection.commit()
        print("[bright_green]Data inserted into machine_info_for_search table.[/bright_green]")

    except Exception as e:
        logging.error(f"Error creating audit table and inserting data: {str(e)}", exc_info=True)



def windows():
    drives = get_drives()
    removeable_drives = get_removable_drives()
    extension = (".xls", ".xlsx")
    if not drives:
        print("[bright_yellow]No drives found.[/bright_yellow]")
    else:
        print("Drives Detected on this PC:")
        for i, drive in enumerate(drives, start=1):
            if drive in removeable_drives:
                print(f"{i}. {drive} (removable)")
            else:
                print(f"{i}. {drive}")

        scan_option_choices = ["All Drive Scan", "Specific Drive Scan"]
        scan_option = select("Select the type of scan:", choices=scan_option_choices).ask()

        try:
            if scan_option == "All Drive Scan":
                print(f"Performing a full scan for data files modified or accessed in the last {n_days} days.")
                print('***')
                print("The Tool is now scanning for Data Files. Please Wait...")

                found_assets = []
                for drive in drives:
                    found_assets.extend(search_files(drive, file_extensions, n_days, sensitive_patterns))
                print(
                    "[bright_green]The File Scanning is now complete!! Please wait while we insert the data into the database...[/bright_green]")
            elif scan_option == "Specific Drive Scan":
                drive_choice = input(
                    r"Enter the drive letter to scan (e.g., C:\, D:\, E:\, ...) or drive path (e.g., C:\Users\Username): ").upper()

                # if drive_choice in [d[0] for d in drives]:
                # selected_drive = [d for d in drives if d[0] == drive_choice][0]
                print(f"Scanning {drive_choice} for data files modified or accessed in the last {n_days} days:")
                print('***')
                print("The Tool is now scanning For Data Files. Please Wait...")

                found_assets = search_files(drive_choice, file_extensions, n_days, sensitive_patterns)
                print(
                    "[bright_green]The File Scanning is now complete!! Please wait while we insert the data into the database...[/bright_green]")
                # else:
                #     print("Invalid drive choice.")
                #     found_assets = []
            else:
                print("Invalid option selected.")
                found_assets = []
        except ValueError:
            print("Invalid input. Please enter a valid option or drive letter.")

        connection = None
        try:
            connection = mysql.connector.connect(
                host=host,
                port=port,
                database=database_name,
                user=username,
                password=password
            )
            # Create the file_name_info table if it doesn't exist
            # create_dataassets_table(connection)
            insert_machine_info_for_search(connection, ipaddrs, hostname, ops, os_name, os_version, system_info )

            if found_assets:
                for asset in found_assets:
                    upsert_to_database(asset, connection, EmployeeUserName, start_time)
                print(
                    f"[bright_green]Scan results for the last {n_days} days saved to the MySQL database...[/bright_green]")
            else:
                print("[bright_yellow]No data assets found.[/bright_yellow]")
        except Exception as e:
            # Log the error to the log file
            logging.error(f"Error connecting to the database: {str(e)}")
        finally:
            if connection:
                connection.close()
        if (os.getenv("ENABLE_EXCEL_FILE_DATA_SCAN")).lower()=="true":
            if ".xls" or ".xlsx" in file_extensions:
                # xls_files = [file for file in found_assets if file.lower().endswith(".xls")]
                xls_files = [file for file in found_assets if file.lower().endswith(extension)]
                if xls_files:
                    connection = mysql.connector.connect(
                        host=host,
                        port=port,
                        database=database_name,
                        user=username,
                        password=password
                    )
                    create_xls_file_sheet_table(connection, xls_files)
                    create_xls_file_sheet_row_table(connection, xls_files)
                    connection.close()
                else:
                    print("No .xls files found.")
    end_time = time.time()
    elapsed_time = end_time - start_time
    ip = get_ip_address()
    connection = mysql.connector.connect(
        host=host,
        port=port,
        database=database_name,
        user=username,
        password=password
    )
    scan = 'Scanning'
    create_audit_table(connection, EmployeeUserName, ip, start_time, end_time, elapsed_time, scan)
    connection.close()


def linux():
    extension = (".xls", ".xlsx")
    root_dir = '/'
    scan_option_choices = ["All Drive Scan", "Specific Path Scan"]
    scan_option = select("Select the type of scan:", choices=scan_option_choices).ask()
    if scan_option == "All Drive Scan":
        print(f"Performing a full scan for data files modified or accessed in the last {n_days} days: ")
        print('***')
        print("The Tool is now scanning for Data Files. Please Wait...")
        found_assets = []

        found_assets.extend(search_files(root_dir, file_extensions, n_days, sensitive_patterns))
        print(
            "[bright_green]The File Scanning is now complete!! Please wait while we insert the data into the database...[/bright_green]")
    elif scan_option == "Specific Path Scan":
        path_choice = input("Enter the path (eg: root/home/gg): ").upper()
        # if drive_choice in [d[0] for d in drives]:
        # selected_drive = [d for d in drives if d[0] == drive_choice][0]
        print(f"Scanning {path_choice} for data files modified or accessed in the last {n_days} days:")
        print('***')
        print("The Tool is now scanning for Data Files. Please Wait...")
        found_assets = search_files(path_choice, file_extensions, n_days, sensitive_patterns)
        print(
            "[bright_green]The File Scanning is now complete!! Please wait while we insert the data into the database...[/bright_green]")
        # else:
        #     print("Invalid drive choice.")
        #     found_assets = []
    else:
        print("Invalid option selected.")
        found_assets = []

    # On Linux, specify the root directory to scan

    # Change this line to scan the root directory
    # found_assets = search_files(root_dir, file_extensions, n_days, sensitive_patterns)

    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            database=database_name,
            user=username,
            password=password
        )
        # Create the file_name_info table if it doesn't exist
        # create_dataassets_table(connection)
        insert_machine_info_for_search(connection, ipaddrs, hostname, ops, os_name, os_version, system_info )

        if found_assets:
            for asset in found_assets:
                upsert_to_database(asset, connection, EmployeeUserName, start_time)
            print(f"Scan results for the last {n_days} days saved to the MySQL database.")
        else:
            print("No data assets found.")
    except Exception as e:
        # Log the error to the log file
        logging.error(f"Error connecting to the database: {str(e)}")
    finally:
        if connection:
            connection.close()
    if (os.getenv("ENABLE_EXCEL_FILE_DATA_SCAN")).lower()=="true":
        if ".xls" or ".xlsx" in file_extensions:
            # xls_files = [file for file in found_assets if file.lower().endswith(".xls")]
            xls_files = [file for file in found_assets if file.lower().endswith(extension)]
            if xls_files:
                connection = mysql.connector.connect(
                    host=host,
                    port=port,
                    database=database_name,
                    user=username,
                    password=password
                )
                create_xls_file_sheet_table(connection, xls_files)
                create_xls_file_sheet_row_table(connection, xls_files)
                connection.close()
            else:
                print("No .xls files found.")
    end_time = time.time()
    elapsed_time = end_time - start_time
    ip = get_ip_address()
    connection = mysql.connector.connect(
        host=host,
        port=port,
        database=database_name,
        user=username,
        password=password
    )
    scan = 'Scanning'
    create_audit_table(connection, EmployeeUserName, ip, start_time, end_time, elapsed_time, scan)
    connection.close()


def count_all_files(directory):
    total_files = 0

    try:
        for root, _, files in os.walk(directory):
            total_files += len(files)
    except Exception as e:
        print(f"Error counting files: {e}")

    return total_files


def count_files_with_extension(directory, extension):
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(extension.lower()):
                count += 1
    return count


if __name__ == "__main__":
    start_time = time.time()
    import platform
    # Get the operating system name
    os_name = platform.system()
    # Get the OS release version
    os_version = platform.release()
    # Get more detailed system information
    system_info = platform.uname()
    hostname = socket.gethostname()
    ipaddrs = get_ip_address()
    print("Your IP Address:", ipaddrs)
    print("Your Host Name: ", hostname)
    print(f"Operating System: {os_name}")
    print(f"OS Version: {os_version}")
    print(f"System Information: {system_info}")
    EmployeeUserName = input("Enter your Employee username: ")
    scan_choices = ["File Count", "File Data Scan"]
    scan = select("Select the type of scan:", choices=scan_choices).ask()

    ops_choices = ["Windows", "Linux"]
    ops = select("Select the Operating System:", choices=ops_choices).ask()

    if scan == "File Count":
        print('***')
        print("The tool is now counting the Data Files. Please Wait...")
        connection = None
        connection = mysql.connector.connect(
            host=host,
            port=port,
            database=database_name,
            user=username,
            password=password
        )
        insert_machine_info_for_search(connection, ipaddrs, hostname, ops, os_name, os_version, system_info )
        end_time = time.time()
        elapsed_time = end_time - start_time
        create_audit_table(connection, EmployeeUserName, ipaddrs, start_time, end_time, elapsed_time, scan)
        connection.close()
        print('[bright_green]The File Counting is now complete.[/bright_green]')
    elif scan == "File Data Scan":
        if ops == "Windows":
            windows()

        elif ops == "Linux":
            linux()
        else:
            print("Incorrect input")
    else:
        print("Incorrect input")

    print("Press Esc to exit...")
    while keyboard.is_pressed('Esc') == False:
        pass