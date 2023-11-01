CREATE DATABASE `malhar` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
CREATE TABLE `dataassets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `FilePath` varchar(255) NOT NULL,
  `FileSize` bigint DEFAULT NULL,
  `FileName` varchar(255) DEFAULT NULL,
  `FileExtension` varchar(10) DEFAULT NULL,
  `ModificationTime` datetime DEFAULT NULL,
  `AccessTime` datetime DEFAULT NULL,
  `CreationTime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `FilePath` (`FilePath`)
) ENGINE=InnoDB AUTO_INCREMENT=330 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
