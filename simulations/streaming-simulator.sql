# Simulating 100 records every 20 seconds
# stop when the # encs hits 1 million
# therefore we will have 100 million clinical observations

# Switch to this database
USE openmrs;

SET SQL_SAFE_UPDATES = 0;
SET @@local.net_read_timeout=360;

drop procedure if exists streamingSim;

DELIMITER //
CREATE PROCEDURE streamingSim()
BEGIN
DECLARE i bigint DEFAULT 1000000;
    WHILE i <= 2000000 DO
         DO SLEEP(20);
		 DROP TEMPORARY TABLE IF EXISTS obs_temp;
		 DROP TEMPORARY TABLE IF EXISTS enc_temp;
  
		 CREATE TEMPORARY TABLE enc_temp SELECT * FROM openmrs.encounter ORDER BY RAND() limit 1;
         UPDATE enc_temp SET uuid=MD5(rand()+rand()*encounter_id*100*rand()*44*i*56);
		 UPDATE enc_temp SET encounter_id = i;
		 INSERT INTO openmrs.encounter SELECT * FROM enc_temp;
         
		 CREATE TEMPORARY TABLE obs_temp SELECT * FROM openmrs.obs ORDER BY RAND() limit 100;
		 UPDATE obs_temp SET uuid=MD5(rand()+rand()*obs_id*rand()*44*i*10000);
         UPDATE obs_temp SET obs_id =0;
		 UPDATE obs_temp SET encounter_id = i;
		 INSERT INTO openmrs.obs SELECT * FROM obs_temp;
    
    SET i = i +1;
    END WHILE;
END
//
  
CALL streamingSim(); 