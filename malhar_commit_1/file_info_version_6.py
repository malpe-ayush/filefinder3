import os
import pandas as pd
import psutil
import mysql.connector
import csv
from datetime import datetime, timedelta
import logging
import xlrd
from dotenv import load_dotenv

load_dotenv()
import time
import socket

# Define the list of file extensions to search for
file_extensions = os.getenv("FILE_EXTENSIONS").split(",")  # Add more extensions as needed

# Define patterns to identify sensitive data in file names
sensitive_patterns = os.getenv("SENSITIVE_PATTERNS").split(",")

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
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    return IPAddr


def get_drives():
    drives = []
    try:
        partitions = psutil.disk_partitions(all=True)  # Include all drives
        for partition in partitions:
            if partition.device:
                drives.append(partition.device)
    except Exception as e:
        # Log the error to the log file
        logging.error(f"Error retrieving drive information: {str(e)}", exc_info=True)
    return drives


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
                if any(filename.lower().endswith(ext) for ext in extensions):
                    file_path = os.path.join(foldername, filename)
                    if is_recently_accessed_or_modified(file_path, n_days) and not is_sensitive_file(file_path,
                                                                                                     sensitive_patterns):
                        found_assets.append(file_path)
    except Exception as e:
        # Log the error to the log file
        logging.error(f"Error scanning files: {str(e)}", exc_info=True)
    return found_assets


def upsert_to_database(file_path, connection,employee_username,start_time):
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
        INSERT INTO file_name_info (machine_info_for_search_fk, ip_address,hostname,file_path, file_size_bytes, file_name, file_extension,file_creation_time, file_modification_time, file_last_access_time, creation_date_time, employee_username_created_by,employee_username_last_updatedby, modification_date_time)
        VALUES ((SELECT machine_info_for_search_pk FROM machine_info_for_search WHERE hostname = %s), %s,%s,%s, %s, %s, %s, %s, %s, %s,FROM_UNIXTIME(%s),%s,%s,FROM_UNIXTIME(%s))
        ON DUPLICATE KEY UPDATE
        file_size_bytes = %s, modification_date_time = FROM_UNIXTIME(%s),employee_username_last_updatedby=%s ;
    ''', (
    hostname, ipaddrs, hostname, file_path, file_size, file_name, file_extension, creation_time,modification_time, access_time, start_time, employee_username,employee_username,start_time,
    file_size, start_time,employee_username, ))
    connection.commit()


# Define the SQL statement for table creation
# create_table_sql = '''
# CREATE TABLE IF NOT EXISTS file_name_info (
#     file_name_info_pk INT AUTO_INCREMENT PRIMARY KEY,
#     file_path VARCHAR(255) UNIQUE,
#     file_size BIGINT,
#     file_name VARCHAR(255),
#     file_extension VARCHAR(10),
#     modification_time DATETIME,
#     access_time DATETIME,
#     creation_time DATETIME
# );
# '''

# def create_dataassets_table(connection):
#     try:
#         cursor = connection.cursor()
#         cursor.execute(create_table_sql)
#         connection.commit()
#         print("file_name_info table created or already exists.")
#     except mysql.connector.Error as err:
#         logging.error(f"Error creating file_name_info table: {err}", exc_info=True)

# Function to create a new table for .xls files
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
        print("Tables for .xls files created and data inserted.")
    except Exception as e:
        logging.error(f"Error creating .xls file tables and inserting data: {str(e)}", exc_info=True)


# Function to create a new table for .xls file rows
def create_xls_file_sheet_row_table(connection, xls_files):
    try:
        cursor = connection.cursor()
        for xls_file in xls_files:
            xls_data = pd.read_excel(xls_file, sheet_name=None)  # Read all sheets

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
                for row_idx in range(min(int(os.getenv("MIN_ROW")), num_rows)):  # Read up to the first 3 rows
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
        print("Tables for .xls file rows created and data inserted.")
    except Exception as e:
        logging.error(f"Error creating .xls file row tables and inserting data: {str(e)}", exc_info=True)


# function for audit table
def create_audit_table(connection,EmployeeUserName, ip, start_time, end_time, elapsed_time):
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
            INSERT INTO audit_info (machine_info_for_search_fk,pc_ip_address ,employee_username, start_time,end_time, duration)
            VALUES ((SELECT machine_info_for_search_pk FROM machine_info_for_search WHERE ip_address= %s),%s, %s, FROM_UNIXTIME(%s), FROM_UNIXTIME(%s), %s);
        ''', (ip,ip, EmployeeUserName ,start_time, end_time, end_time - start_time))
        connection.commit()
        print("Table for audit created and data inserted.")
    except Exception as e:
        logging.error(f"Error creating audit table and inserting data: {str(e)}", exc_info=True)

def insert_machine_info_for_search(connection,ipaddress,hostname,ops):
    if ops == 'W' or ops == 'w':
        drives = get_drives()
        total_files=0
        total_excel_files=0
        total_pdf_files=0
        total_word_files=0
        total_zip_files=0
        for drive in drives:
            
            total_files+=count_all_files(drive)
            total_excel_files += count_files_with_extension(drive, ".xls") + count_files_with_extension(drive, ".xlsx")
            total_word_files+= count_files_with_extension(drive, ".docx") + count_files_with_extension(drive, ".doc")
            total_pdf_files+= count_files_with_extension(drive, ".pdf")
            total_zip_files += count_files_with_extension(drive, ".zip")

    elif ops == 'L' or ops == 'l':
        directory_path='/'
        total_files=count_all_files(directory_path)
        total_excel_files = count_files_with_extension(directory_path, ".xls") + count_files_with_extension(directory_path, ".xlsx")
        total_word_files = count_files_with_extension(directory_path, ".docx") + count_files_with_extension(directory_path, ".doc")
        total_pdf_files = count_files_with_extension(directory_path, ".pdf")
        total_zip_files = count_files_with_extension(directory_path, ".zip")
    else:
        print("incorrect input")
        return 0
    
    try:
        cursor = connection.cursor()
        cursor.execute('''
                INSERT INTO machine_info_for_search (hostname ,ip_address,total_n_files,total_n_excel,total_n_pdf,total_n_word,total_n_zip)
                VALUES (%s, %s,%s,%s,%s,%s,%s)ON DUPLICATE KEY UPDATE
                       total_n_files=VALUES(total_n_files),
                       total_n_excel=VALUES(total_n_excel),
                       total_n_pdf=VALUES(total_n_pdf),
                       total_n_word=VALUES(total_n_word),
                       total_n_zip=VALUES(total_n_zip);
            ''', (hostname, ipaddress,total_files,total_excel_files,total_pdf_files,total_word_files,total_zip_files))
        connection.commit()
        print("Table for machine_info_for_search created and data inserted.")


    except Exception as e:
        logging.error(f"Error creating audit table and inserting data: {str(e)}", exc_info=True)



def windows():
    drives = get_drives()
    extension = (".xls", ".xlsx")
    if not drives:
        print("No drives found.")
    else:
        print("Drives Detected on this PC:")
        for i, drive in enumerate(drives, start=1):
            print(f"{i}. {drive}")

        scan_option = input("Choose the Search Type: \n1. All Drive Scan\n2. Specific Drive Scan \nEnter the option (A or S): ")

        try:
            if scan_option == 'A' or scan_option == 'a':
                print(f"Performing a full scan for data files modified or accessed in the last {n_days} days:")
                print('***')
                print("Please Wait..... The Tool is now Scanning for Data Files...")

                found_assets = []
                for drive in drives:
                    found_assets.extend(search_files(drive, file_extensions, n_days, sensitive_patterns))
                print("The File Scanning is now complete!!")
            elif scan_option == 'S' or scan_option == 's':
                drive_choice = input(r"Enter the drive letter to scan (e.g., C:\, D:\, E:\, ...) or drive path (e.g., C:\Users\Username): ").upper()

                # if drive_choice in [d[0] for d in drives]:
                # selected_drive = [d for d in drives if d[0] == drive_choice][0]
                print(f"Scanning {drive_choice} for data files modified or accessed in the last {n_days} days:")
                print('***')
                print("Please Wait..... The Tool is now Scanning For Data Files...")

                found_assets = search_files(drive_choice, file_extensions, n_days, sensitive_patterns)
                print("The File Scanning is now complete!!")
                # else:
                #     print("Invalid drive choice.")
                #     found_assets = []
            else:
                print("Invalid option. Please choose A for Full Scan or S for Drive-specific Scan.")
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
            insert_machine_info_for_search(connection,ipaddrs,hostname,ops)

            if found_assets:
                for asset in found_assets:
                    upsert_to_database(asset, connection,EmployeeUserName,start_time)
                print(f"Scan results for the last {n_days} days saved to the MySQL database.")
            else:
                print("No data assets found.")
        except Exception as e:
            # Log the error to the log file
            logging.error(f"Error connecting to the database: {str(e)}")
        finally:
            if connection:
                connection.close()
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
    create_audit_table(connection,EmployeeUserName,  ip, start_time, end_time, elapsed_time)
    connection.close()


def linux():
    
    root_dir = '/'
    scan_option = input("Choose the Search Type:\n1. All Drive Scan\n2. Specefic Path Scan\nEnter the option (F or P): ")
    if scan_option == 'F' or scan_option == 'f':
        print(f"Performing a full scan for data files modified or accessed in the last {n_days} days:")
        print('***')
        print("Please Wait..... The Tool is now Scanning for Data Files...")
        found_assets = []

        found_assets.extend(search_files(root_dir, file_extensions, n_days, sensitive_patterns))
        print("The File Scanning is now complete!!")
    elif scan_option == 'P' or scan_option == 'p':
        path_choice = input("Enter the path (eg: root/home/gg): ").upper()
        # if drive_choice in [d[0] for d in drives]:
        # selected_drive = [d for d in drives if d[0] == drive_choice][0]
        print(f"Scanning {path_choice} for data files modified or accessed in the last {n_days} days:")
        print('***')
        print("Please Wait..... The Tool is now Scanning, For Data Files...")
        found_assets = search_files(path_choice, file_extensions, n_days, sensitive_patterns)
        print('The File Scanning is now Complete!!')
        # else:
        #     print("Invalid drive choice.")
        #     found_assets = []
    else:
        print("Invalid option. Please choose 1 for Full Scan or 2 for Drive-specific Scan.")
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

        if found_assets:
            for asset in found_assets:
                upsert_to_database(asset, connection,EmployeeUserName,start_time)
            print(f"Scan results for the last {n_days} days saved to the MySQL database.")
        else:
            print("No data assets found.")
    except Exception as e:
        # Log the error to the log file
        logging.error(f"Error connecting to the database: {str(e)}")
    finally:
        if connection:
            connection.close()
    if ".xls" in file_extensions or ".xlsx" in file_extensions:
        xls_files = [file for file in found_assets if file.lower().endswith((".xls", ".xlsx"))]
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
            print("No .xls or .xlsx files found.")
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
    create_audit_table(connection,EmployeeUserName, ip, start_time, end_time, elapsed_time)
    connection.close()

def count_all_files(directory):
    total_files = 0

    try:
        for root,_,files in os.walk(directory):
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
    hostname = socket.gethostname()
    ipaddrs = socket.gethostbyname(hostname)
    print("Your IP Address:",ipaddrs)
    print("Your Host Name: ",hostname)
    EmployeeUserName=input("Enter your Employee username: ")
    scan=input("Enter type of scan: \n1.File Count\n2.File Data Scan\nEnter the option (C or S): ")
    ops = input("Choose the type of OS of your Machine:\n1.Windows\n2. Linux\nEnter the option (W or L): ")
    if scan=='C' or scan=='c':
            print('***')
            print("Please Wait..... The Tool is now counting the Data Files...")
            connection = None
            connection = mysql.connector.connect(
                host=host,
                port=port,
                database=database_name,
                user=username,
                password=password
            )
            insert_machine_info_for_search(connection,ipaddrs,hostname,ops)
            end_time=time.time()
            elapsed_time=end_time-start_time
            create_audit_table(connection,EmployeeUserName,  ipaddrs, start_time, end_time, elapsed_time)
            connection.close()
    elif scan=='S'or scan=='s':
        if ops == 'W' or ops == 'w':
            windows()

        elif ops == 'L' or ops == 'l':
            linux()
        else:
            print("Incorrect input")
    else:
        print("Incorrect input")