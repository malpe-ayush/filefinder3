import pandas as pd
import mysql.connector
from datetime import datetime
import os

from dotenv import load_dotenv
load_dotenv()
# Replace with your MySQL database configuration
host = os.getenv("MYSQL_HOST")  # Replace with the MySQL server address
port = os.getenv("MYSQL_PORT")  # Replace with the MySQL server port
database_name = os.getenv("MYSQL_DATABASE")
username = os.getenv("MYSQL_USERNAME")
password = os.getenv("MYSQL_PASSWORD")

# Read the Excel file
df = pd.read_excel('pc_data_info.xlsx')

df_assessment = df[df['groupType'] == 'Assessment']

# Establish a MySQL database connection
connection =  connection = mysql.connector.connect(
                host=host,
                port=port,
                database=database_name,
                user=username,
                password=password
            )
cursor = connection.cursor()


# Loop through the rows of the filtered DataFrame and insert data into the database
for index, row in df_assessment.iterrows():
    name = row['name']
    create_time_str = row['createDate']
    create_time = datetime.strptime(create_time_str, '%d-%b-%Y').strftime('%Y-%m-%d')
    ip = row['collectedIpAddress']
    model = row['model']
    os_name = row['osName']
    total_processor = row['processorCount']
    total_memory = row['memoryInMb']
    free_memory = row['driveTotalFreeInGb']

    # Insert data into your MySQL database
    query = """
        INSERT INTO machine_info(name, create_time, ip, model, os_name, total_processor, total_memory, free_memory)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        create_time = VALUES(create_time),
        ip = VALUES(ip),
        model = VALUES(model),
        os_name = VALUES(os_name),
        total_processor = VALUES(total_processor),
        total_memory = VALUES(total_memory),
        free_memory = VALUES(free_memory)
        """

    values = (name, create_time, ip, model, os_name, total_processor, total_memory, free_memory)

    cursor.execute(query, values)

# Commit the changes and close the database connection
connection.commit()
cursor.close()
connection.close()