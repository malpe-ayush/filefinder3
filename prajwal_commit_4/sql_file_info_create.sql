CREATE DATABASE `file_info` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
use file_info;
CREATE TABLE `machine_info` (
  `pc_data_pk` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `create_time` date DEFAULT NULL,
  `ip` varchar(15) DEFAULT NULL,
  `model` varchar(255) DEFAULT NULL,
  `os_name` varchar(255) DEFAULT NULL,
  `total_processor` int DEFAULT NULL,
  `total_memory` int DEFAULT NULL,
  `free_memory` float DEFAULT NULL,
  PRIMARY KEY (`pc_data_pk`),
  UNIQUE KEY `idx_name` (`name`),
  KEY `idx_pc_data_pk` (`pc_data_pk`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `file_name_info` (
  `file_name_info_pk` int NOT NULL AUTO_INCREMENT,
  `file_path` varchar(255) DEFAULT NULL,
  `file_size` bigint DEFAULT NULL,
  `file_name` varchar(255) DEFAULT NULL,
  `file_extension` varchar(10) DEFAULT NULL,
  `modification_time` datetime DEFAULT NULL,
  `access_time` datetime DEFAULT NULL,
  `creation_time` datetime DEFAULT NULL,
  PRIMARY KEY (`file_name_info_pk`),
  UNIQUE KEY `file_path` (`file_path`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE `xls_file_sheet` (
  `xls_file_sheet_pk` int NOT NULL AUTO_INCREMENT,
  `file_name_info_fk` int DEFAULT NULL,
  `sheet_name` varchar(255) DEFAULT NULL,
  `total_cols` int DEFAULT NULL,
  `total_rows` int DEFAULT NULL,
  PRIMARY KEY (`xls_file_sheet_pk`),
  UNIQUE KEY `unique_file_sheet` (`file_name_info_fk`,`sheet_name`),
  CONSTRAINT `xls_file_sheet_ibfk_1` FOREIGN KEY (`file_name_info_fk`) REFERENCES `file_name_info` (`file_name_info_pk`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE `xls_file_sheet_row` (
  `xls_file_sheet_row_pk` int NOT NULL AUTO_INCREMENT,
  `xls_file_sheet_fk` int DEFAULT NULL,
  `sheet_name` varchar(255) DEFAULT NULL,
  `col_no` int DEFAULT NULL,
  `row_no` int DEFAULT NULL,
  `is_row` varchar(3) DEFAULT NULL,
  `col_data_1` varchar(255) DEFAULT NULL,
  `col_data_2` varchar(255) DEFAULT NULL,
  `col_data_3` varchar(255) DEFAULT NULL,
  `col_data_4` varchar(255) DEFAULT NULL,
  `col_data_5` varchar(255) DEFAULT NULL,
  `col_data_6` varchar(255) DEFAULT NULL,
  `col_data_7` varchar(255) DEFAULT NULL,
  `col_data_8` varchar(255) DEFAULT NULL,
  `col_data_9` varchar(255) DEFAULT NULL,
  `col_data_10` varchar(255) DEFAULT NULL,
  `is_truncate` varchar(3) DEFAULT NULL,
  PRIMARY KEY (`xls_file_sheet_row_pk`),
  UNIQUE KEY `unique_file_sheet` (`xls_file_sheet_fk`,`sheet_name`,`row_no`),
  CONSTRAINT `xls_file_sheet_row_ibfk_1` FOREIGN KEY (`xls_file_sheet_fk`) REFERENCES `xls_file_sheet` (`xls_file_sheet_pk`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `audit_info` (
  `pc_ip_address` text,
  `start_time` timestamp NULL DEFAULT NULL,
  `end_time` timestamp NULL DEFAULT NULL,
  `duration` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
