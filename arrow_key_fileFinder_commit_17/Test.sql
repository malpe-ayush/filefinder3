USE lisney_files_info5;
DELIMITER //
DROP PROCEDURE IF EXISTS sp_InsertOrUpdateFileCounts;

CREATE PROCEDURE sp_InsertOrUpdateFileCounts()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE ip_address_value VARCHAR(50);
    DECLARE hostname_value VARCHAR(100);
    DECLARE file_extension_value VARCHAR(100);
    DECLARE file_count_value INT;
    DECLARE row_creation_date_time_value TIMESTAMP;
    DECLARE row_created_by_value VARCHAR(255);
    DECLARE row_modification_date_time_value TIMESTAMP;
    DECLARE row_modification_by_value VARCHAR(255);

    DECLARE file_cursor CURSOR FOR
        SELECT
            ip_address,
            hostname,
            file_extension,
            COUNT(*) AS file_count,
            CURRENT_TIMESTAMP, 
            'creator', 
            CURRENT_TIMESTAMP, 
            'modifier'
        FROM 
            d_file_details
        GROUP BY 
            ip_address,
            hostname, 
            file_extension;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN file_cursor;

    file_loop: LOOP
        FETCH file_cursor INTO ip_address_value, hostname_value, file_extension_value, file_count_value,
              row_creation_date_time_value, row_created_by_value, row_modification_date_time_value, row_modification_by_value;
        IF done THEN
            LEAVE file_loop;
        END IF;

        INSERT INTO f_machine_files_count_sp (ip_address, hostname, file_extension, file_count, 
                                              row_creation_date_time, row_created_by, row_modification_date_time, row_modification_by)
        VALUES (ip_address_value, hostname_value, file_extension_value, file_count_value,
                row_creation_date_time_value, row_created_by_value, row_modification_date_time_value, row_modification_by_value)
        ON DUPLICATE KEY UPDATE
            file_count = file_count_value,
            row_modification_date_time = row_modification_date_time_value,
            row_modification_by = row_modification_by_value;
            
    END LOOP;

    CLOSE file_cursor;
END//
DELIMITER ;