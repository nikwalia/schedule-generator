-- calculates the semester offset on insert

DROP TRIGGER IF EXISTS calculate_semester;
DELIMITER //

CREATE TRIGGER calculate_semester
	BEFORE INSERT ON student_info.enrollments
    FOR EACH ROW
    BEGIN
		SET @class_semester = convert_semester(NEW.semester);
        SET @start_semester = convert_semester((SELECT s.start_semester FROM student_info.student s WHERE s.net_id = NEW.net_id));
        IF @class_semester = 0 THEN
			SET NEW.semester_taken = 0; -- class was taken before being a student at the university
		ELSE
			SET NEW.semester_taken = @class_semester - @start_semester + 1; -- semester should start at 1
        END IF;
END//

DELIMITER ;