CREATE PROCEDURE GetTopClassFrequency (
	IN course_id VARCHAR(10),
    OUT best_semester INT
)
BEGIN
	IF NOT EXISTS(SELECT c.course_id FROM student_info.courses c WHERE c.course_id = course_id) THEN
		SET best_semester = -1;
	ELSE
		SELECT e.semester_taken
        INTO best_semester
        FROM student_info.enrollments e
        WHERE e.course_id = course_id
        GROUP BY e.semester_taken
        HAVING COUNT(e.net_id) = MAX(COUNT(e.net_id));
	END IF;
END
