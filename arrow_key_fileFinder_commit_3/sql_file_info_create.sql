CREATE USER IF NOT EXISTS 'arungt'@'%' IDENTIFIED BY 'fi!ef!ndgt!23';
GRANT ALL PRIVILEGES ON *.* TO 'arungt'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;


CREATE DATABASE file_info /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
use file_info;

CREATE TABLE machine_info_for_search (
  machine_info_for_search_pk int NOT NULL AUTO_INCREMENT,
  hostname varchar(100) DEFAULT NULL,
  ip_address varchar(50) DEFAULT NULL,
  os_name varchar(100) DEFAULT NULL,
  os_version varchar(100) DEFAULT NULL,
  system_info varchar(1000) DEFAULT NULL,
  number_of_drives int DEFAULT NULL,
  name_of_drives varchar(1000) DEFAULT NULL,
  total_n_files int DEFAULT NULL,
  total_n_excel int DEFAULT NULL,
  total_n_pdf int DEFAULT NULL,
  total_n_word int DEFAULT NULL,
  total_n_zip int DEFAULT NULL,

  PRIMARY KEY (machine_info_for_search_pk),
  UNIQUE KEY host_key (hostname)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE machine_info_migration_centre (
  machine_info_migration_centre_pk int NOT NULL AUTO_INCREMENT,
  name varchar(255) DEFAULT NULL,
  create_time date DEFAULT NULL,
  ip varchar(15) DEFAULT NULL,
  model varchar(255) DEFAULT NULL,
  os_name varchar(255) DEFAULT NULL,
  total_processor int DEFAULT NULL,
  total_memory int DEFAULT NULL,
  free_memory float DEFAULT NULL,
  PRIMARY KEY (machine_info_migration_centre_pk),
  UNIQUE KEY idx_name (name),
  KEY idx_pc_data_pk (machine_info_migration_centre_pk)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE file_name_info (
  file_name_info_pk int NOT NULL AUTO_INCREMENT,
  machine_info_for_search_fk int DEFAULT NULL,
  ip_address varchar(25) DEFAULT NULL,
  hostname varchar(255) DEFAULT NULL,
  file_name varchar(255) DEFAULT NULL,
  file_path varchar(255) DEFAULT NULL,
  file_size_bytes bigint DEFAULT NULL,
  file_extension varchar(10) DEFAULT NULL,
  file_creation_time datetime DEFAULT NULL,
  file_modification_time datetime DEFAULT NULL,
  file_last_access_time datetime DEFAULT NULL,
  classification_file_data varchar(100) DEFAULT NULL,
  file_data_domain varchar(100) DEFAULT NULL,
  file_GPDR_data varchar(1) DEFAULT NULL,
  file_lisney_to_label varchar(100) DEFAULT NULL,
  file_lisney_to_describe varchar(255) DEFAULT NULL,
  file_lisney_to_classify varchar(100) DEFAULT NULL,
  creation_date_time timestamp NULL DEFAULT NULL,
  employee_username_created_by varchar(255) DEFAULT NULL,
  `modification_date_time`timestamp NULL DEFAULT NULL,
  employee_username_last_updatedby varchar(100) DEFAULT NULL,
  PRIMARY KEY (file_name_info_pk),
  UNIQUE KEY file_path (machine_info_for_search_fk, file_path),
  CONSTRAINT file_name_info_ibfk_1 FOREIGN KEY (machine_info_for_search_fk) REFERENCES machine_info_for_search (machine_info_for_search_pk)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE xls_file_sheet (
  xls_file_sheet_pk int NOT NULL AUTO_INCREMENT,
  file_name_info_fk int DEFAULT NULL,
  sheet_name varchar(255) DEFAULT NULL,
  total_cols int DEFAULT NULL,
  total_rows int DEFAULT NULL,
  PRIMARY KEY (xls_file_sheet_pk),
  UNIQUE KEY unique_file_sheet (file_name_info_fk,sheet_name),
  CONSTRAINT xls_file_sheet_ibfk_1 FOREIGN KEY (file_name_info_fk) REFERENCES file_name_info (file_name_info_pk)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE xls_file_sheet_row (
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
  PRIMARY KEY (xls_file_sheet_row_pk),
  UNIQUE KEY unique_file_sheet (xls_file_sheet_fk,sheet_name,row_no),
  CONSTRAINT xls_file_sheet_row_ibfk_1 FOREIGN KEY (xls_file_sheet_fk) REFERENCES xls_file_sheet (xls_file_sheet_pk)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE audit_info (
  audit_info_pk int not null auto_increment,
  machine_info_for_search_fk int default null,
  pc_ip_address text,
  employee_username text,
  start_time timestamp NULL DEFAULT NULL,
  end_time timestamp NULL DEFAULT NULL,
  duration text,
  filefinder_activity text,
  activity_status text default ('error'),
   PRIMARY KEY (audit_info_pk),
   CONSTRAINT audit_info_ibfk_1 FOREIGN KEY (machine_info_for_search_fk) REFERENCES machine_info_for_search (machine_info_for_search_pk)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;