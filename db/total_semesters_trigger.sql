DROP TRIGGER IF EXISTS calculate_end_semester;

DELIMITER //

CREATE TRIGGER calculate_end_semester
	BEFORE INSERT ON student_info.student
    FOR EACH ROW
    BEGIN
		SET @start_semester_num = convert_semester(NEW.start_semester);
        SET @end_semester_num = convert_semester(NEW.expected_graduation);
        SET NEW.total_semesters = @end_semester_num - @start_semester_num + 1;

END//

DELIMITER ;