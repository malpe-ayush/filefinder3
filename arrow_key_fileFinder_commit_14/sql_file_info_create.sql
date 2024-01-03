CREATE USER IF NOT EXISTS 'arungt'@'%' IDENTIFIED BY 'fi!ef!ndgt!23';
GRANT ALL PRIVILEGES ON *.* TO 'arungt'@'%' WITH GRANT OPTION;
/*GRANT ALL ON mydb.* TO 'arungt'@'%';
#for google cloud only*/
FLUSH PRIVILEGES;


CREATE DATABASE IF NOT EXISTS lisney_files_info3 /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
use lisney_files_info3;


CREATE TABLE IF NOT EXISTS env_info (
  env_info_pk int not null auto_increment,
  env_key  varchar(100) DEFAULT NULL,
  env_value varchar(1500) DEFAULT NULL,
  row_creation_date_time timestamp NULL DEFAULT NULL,
  row_created_by varchar(255) DEFAULT NULL,
  row_modification_date_time timestamp NULL DEFAULT NULL,
  row_modification_by varchar(100) DEFAULT NULL,
  PRIMARY KEY (env_info_pk)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO env_info (env_key, env_value) VALUES 
('ENABLE_FILE_EXT_COUNT_IN_SCAN', 'true'),
('D_FILE_DETAILS_FILE_EXTENSIONS', '.pdf, .xls, .xlsx, .doc, .docx,  .ppt,.pptx, .txt, .rtf, .csv, .tsv, .pst, .sql, .db, .dbf, .mdb,  .bak,  .zip, .gz, .tar, .rar, .7z, .jpg, .png, .gif, .mp3, .mp4, .xml, .html, .htm, .log,  .odt, .ods, .odp, .odg, .odf, .od, .exe, .dll, .avi, .bat, .reg, .css, .js, .lnk, .sys, .ini, .wav, .bmp, .tif, .iso, .dat,  .psd, .ai, .eps'),
('N_DAYS', '0'),
('IS_SENSITIVE_FILE_EXTENSIONS', '.xls,.xlsx,.txt'),
('FILE_PATH_SCAN_SENSITIVE_PATTERNS', 'password,creditcard'),
('ENABLE_EXCEL_FILE_DATA_SCAN', 'false'),
('ENABLE_EXCEL_FILE_DATA_SCAN_MIN_ROW', '3');




CREATE TABLE IF NOT EXISTS f_machine_files_summary_count (
  f_machine_files_summary_count_pk int NOT NULL AUTO_INCREMENT,
  hostname varchar(100) DEFAULT NULL,
  ip_address varchar(50) DEFAULT NULL,
  os_name varchar(100) DEFAULT NULL,
  os_version varchar(100) DEFAULT NULL,
  system_info varchar(1000) DEFAULT NULL,
  number_of_drives int DEFAULT NULL,
  name_of_drives varchar(1000) DEFAULT NULL,
  total_n_files int DEFAULT NULL,
  total_n_xls int DEFAULT NULL,
  total_n_xlsx int DEFAULT NULL,
  total_n_doc int DEFAULT NULL,
  total_n_docx int DEFAULT NULL,
  total_n_pdf int DEFAULT NULL,
  total_n_zip int DEFAULT NULL,
  total_n_sql int DEFAULT NULL,
  total_n_bak int DEFAULT NULL,
  row_creation_date_time timestamp NULL DEFAULT NULL,
  row_created_by varchar(255) DEFAULT NULL,
  row_modification_date_time timestamp NULL DEFAULT NULL,
  row_modification_by varchar(100) DEFAULT NULL,
  PRIMARY KEY (f_machine_files_summary_count_pk ),
  UNIQUE KEY host_key (hostname)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS machine_info_migration_center (
  machine_info_migration_centre_pk int NOT NULL AUTO_INCREMENT,
  name varchar(255) DEFAULT NULL,
  create_time date DEFAULT NULL,
  ip varchar(15) DEFAULT NULL,
  model varchar(255) DEFAULT NULL,
  os_name varchar(255) DEFAULT NULL,
  total_processor int DEFAULT NULL,
  total_memory int DEFAULT NULL,
  free_memory float DEFAULT NULL,
  row_creation_date_time timestamp NULL DEFAULT NULL,
  row_created_by varchar(255) DEFAULT NULL,
  row_modification_date_time timestamp NULL DEFAULT NULL,
  row_modification_by varchar(100) DEFAULT NULL,
  PRIMARY KEY (machine_info_migration_centre_pk),
  UNIQUE KEY idx_name (name),
  KEY idx_pc_data_pk (machine_info_migration_centre_pk)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/* 
  classification_file_data varchar(100) DEFAULT NULL,#GT-data no input
  file_data_domain varchar(100) DEFAULT NULL,#GT-data no input
  file_is_sensitive_data varchar(1) DEFAULT NULL,
  file_lisney_isGPDR varchar(1) DEFAULT NULL, #Below is lisney data
  file_lisney_to_label varchar(100) DEFAULT NULL,
  file_lisney_to_describe varchar(255) DEFAULT NULL,
  file_lisney_to_classify varchar(100) DEFAULT NULL, */

CREATE TABLE IF NOT EXISTS d_file_details (
  d_file_details_pk int NOT NULL AUTO_INCREMENT,
  f_machine_files_summary_count_fk int DEFAULT NULL,
  ip_address varchar(25) DEFAULT NULL,
  hostname varchar(255) DEFAULT NULL,
  file_path varchar(500) DEFAULT NULL,
  file_size_bytes bigint DEFAULT NULL,
  file_name varchar(255) DEFAULT NULL,
  file_extension varchar(255) DEFAULT NULL,
  file_owner varchar(100) DEFAULT NULL,
  file_creation_time datetime DEFAULT NULL,
  file_modification_time datetime DEFAULT NULL,
  file_last_access_time datetime DEFAULT NULL,
  classification_file_data varchar(100) DEFAULT NULL,
  file_data_domain varchar(100) DEFAULT NULL,
  file_is_sensitive_data varchar(1) DEFAULT NULL,
  file_lisney_isGPDR varchar(1) DEFAULT NULL,
  file_lisney_to_label varchar(100) DEFAULT NULL,
  file_lisney_to_describe varchar(255) DEFAULT NULL,
  file_lisney_to_classify varchar(100) DEFAULT NULL,
  row_creation_date_time timestamp NULL DEFAULT NULL,
  row_created_by varchar(255) DEFAULT NULL,
  row_modification_date_time timestamp NULL DEFAULT NULL,
  row_modification_by varchar(100) DEFAULT NULL,
  PRIMARY KEY (d_file_details_pk),
  UNIQUE KEY file_path (f_machine_files_summary_count_fk, file_path),
CONSTRAINT d_file_details_ibfk_1 FOREIGN KEY (f_machine_files_summary_count_fk) REFERENCES f_machine_files_summary_count (f_machine_files_summary_count_pk)
 
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS xls_file_sheet (
  xls_file_sheet_pk int NOT NULL AUTO_INCREMENT,
  d_file_details_fk int DEFAULT NULL,
  sheet_name varchar(255) DEFAULT NULL,
  total_cols int DEFAULT NULL,
  total_rows int DEFAULT NULL,
  row_creation_date_time timestamp NULL DEFAULT NULL,
  row_created_by varchar(255) DEFAULT NULL,
  row_modification_date_time timestamp NULL DEFAULT NULL,
  row_modification_by varchar(100) DEFAULT NULL,
  PRIMARY KEY (xls_file_sheet_pk),
  UNIQUE KEY unique_file_sheet (d_file_details_fk,sheet_name),
  CONSTRAINT xls_file_sheet_ibfk_1 FOREIGN KEY (d_file_details_fk) REFERENCES d_file_details (d_file_details_pk)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS xls_file_sheet_row (
  xls_file_sheet_row_pk int NOT NULL AUTO_INCREMENT,
  xls_file_sheet_fk int DEFAULT NULL,
  sheet_name varchar(255) DEFAULT NULL,
  col_no int DEFAULT NULL,
  row_no int DEFAULT NULL,
  is_row varchar(3) DEFAULT NULL,
  col_data_1 varchar(255) DEFAULT NULL,
  col_data_2 varchar(255) DEFAULT NULL,
  col_data_3 varchar(255) DEFAULT NULL,
  col_data_4 varchar(255) DEFAULT NULL,
  col_data_5 varchar(255) DEFAULT NULL,
  col_data_6 varchar(255) DEFAULT NULL,
  col_data_7 varchar(255) DEFAULT NULL,
  col_data_8 varchar(255) DEFAULT NULL,
  col_data_9 varchar(255) DEFAULT NULL,
  col_data_10 varchar(255) DEFAULT NULL,
  is_truncate varchar(3) DEFAULT NULL,
  row_creation_date_time timestamp NULL DEFAULT NULL,
  row_created_by varchar(255) DEFAULT NULL,
  row_modification_date_time timestamp NULL DEFAULT NULL,
  row_modification_by varchar(100) DEFAULT NULL,
  PRIMARY KEY (xls_file_sheet_row_pk),
  UNIQUE KEY unique_file_sheet (xls_file_sheet_fk,sheet_name,row_no),
  CONSTRAINT xls_file_sheet_row_ibfk_1 FOREIGN KEY (xls_file_sheet_fk) REFERENCES xls_file_sheet (xls_file_sheet_pk)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS audit_info (
  audit_info_pk int not null auto_increment,
  f_machine_files_summary_count_fk int default null,
  pc_ip_address varchar(255) DEFAULT NULL,
  employee_username varchar(255) DEFAULT NULL,
  start_time timestamp NULL DEFAULT NULL,
  end_time timestamp NULL DEFAULT NULL,
  duration text,
  filefinder_activity varchar(255) DEFAULT NULL,
  activity_status varchar(255) DEFAULT ('error'),
  row_creation_date_time timestamp NULL DEFAULT NULL,
  row_created_by varchar(255) DEFAULT NULL,
  row_modification_date_time timestamp NULL DEFAULT NULL,
  row_modification_by varchar(100) DEFAULT NULL,
   PRIMARY KEY (audit_info_pk),
   CONSTRAINT audit_info_ibfk_1 FOREIGN KEY (f_machine_files_summary_count_fk) REFERENCES f_machine_files_summary_count (f_machine_files_summary_count_pk)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS app_log_file(
	app_log_file_pk int not null auto_increment,
	f_machine_files_summary_count_fk int default null,
	ip_address varchar(50) DEFAULT NULL,
	hostname varchar(100) DEFAULT NULL,
	app_log longtext DEFAULT NULL ,
	row_creation_date_time timestamp NULL DEFAULT NULL,
	row_created_by varchar(255) DEFAULT NULL,
	row_modification_date_time timestamp NULL DEFAULT NULL,
	row_modification_by varchar(100) DEFAULT NULL,
	PRIMARY KEY (app_log_file_pk),
	CONSTRAINT app_log_file_ibfk_1 FOREIGN KEY (f_machine_files_summary_count_fk) REFERENCES f_machine_files_summary_count (f_machine_files_summary_count_pk)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE IF NOT EXISTS f_machine_files_count_sp (
  f_machine_files_count_sp_pk int not null auto_increment,
  hostname  varchar(100) DEFAULT NULL,
  file_extension  varchar(100) DEFAULT NULL,
  file_count varchar(100) DEFAULT NULL,
  row_creation_date_time timestamp NULL DEFAULT NULL,
  row_created_by varchar(255) DEFAULT NULL,
  row_modification_date_time timestamp NULL DEFAULT NULL,
  row_modification_by varchar(100) DEFAULT NULL,
  PRIMARY KEY (f_machine_files_count_sp_pk)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DELIMITER //

CREATE PROCEDURE InsertFileCounts()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE hostname_value VARCHAR(255);
    DECLARE file_extension_value VARCHAR(255);
    DECLARE file_count_value INT;

    -- Declare a cursor to select data
    DECLARE file_cursor CURSOR FOR
        SELECT 
            hostname,
            file_extension,
            COUNT(*) AS file_count
        FROM 
            d_file_details
        GROUP BY 
            hostname, 
            file_extension;

    -- Declare continue handler to exit loop
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- Open the cursor
    OPEN file_cursor;

    -- Loop through the data and insert into the table
    file_loop: LOOP
        FETCH file_cursor INTO hostname_value, file_extension_value, file_count_value;
        IF done THEN
            LEAVE file_loop;
        END IF;

        -- Insert into your_table_name with retrieved values, using INSERT IGNORE
        INSERT IGNORE INTO f_machine_files_count_sp (hostname, file_extension, file_count)
        VALUES (hostname_value, file_extension_value, file_count_value);
    END LOOP;

    -- Close the cursor
    CLOSE file_cursor;
END//

DELIMITER ;



