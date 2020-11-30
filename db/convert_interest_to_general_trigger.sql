DROP TRIGGER IF EXISTS convert_interest_to_general;

DELIMITER //

CREATE TRIGGER convert_interest_to_general
	BEFORE INSERT ON student_info.track
	FOR EACH ROW
    BEGIN
		IF NEW.interest = "" THEN
			SET NEW.interest = "General";
		END IF;
END//

DELIMITER ;
