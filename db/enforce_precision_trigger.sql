DROP TRIGGER IF EXISTS enforce_precision;

DELIMITER //

CREATE TRIGGER enforce_precision
	BEFORE INSERT ON student_info.courses
		FOR EACH ROW
		BEGIN
		SET NEW.GPA = ROUND(NEW.GPA, 3);
	
END //

DELIMITER ;