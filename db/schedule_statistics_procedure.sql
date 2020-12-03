CREATE DEFINER=`admin`@`%` PROCEDURE `schedule_statistics`(
	IN rowid INT,
    OUT average_rating FLOAT,
    OUT average_GPA FLOAT,
    OUT total_credits INT,
    OUT desired_credits INT,
    OUT num_classes INT,
    OUT num_interest_match_classes INT
)
BEGIN
	SET @schedule_arr = 
	(SELECT schedule
	FROM student_info.schedules
	WHERE schedules.rowid = rowid);
    
    SET @interest = 
    (SELECT CONCAT(schedules.field_name, '-', schedules.interest)
    FROM student_info.schedules
    WHERE schedules.rowid = rowid);
    
    SET desired_credits = 
    (SELECT credit_hours
    FROM student_info.track NATURAL JOIN student_info.schedules
    WHERE schedules.rowid = rowid);

	DROP TABLE IF EXISTS student_info.schedule_data;
	CREATE TABLE student_info.schedule_data
	SELECT * FROM
		JSON_TABLE(
			@schedule_arr,
			"$[*]"
			COLUMNS(
				rowid FOR ORDINALITY,
				course_id VARCHAR(10) PATH "$" ERROR ON ERROR
			)
		) dat;
    
    SELECT AVG(e2.avgRating), AVG(courses.GPA), SUM(courses.credits), SUM(c.match_interest)
    INTO average_rating, average_GPA, total_credits, num_interest_match_classes
    FROM (SELECT enrollments.course_id, AVG(enrollments.rating) AS avgRating
    FROM student_info.enrollments NATURAL JOIN student_info.schedule_data) AS e2
    NATURAL JOIN
    (SELECT c2.course_id, 1 - CAST(ISNULL(JSON_SEARCH(interest, 'one', @interest)) AS UNSIGNED) AS match_interest
	FROM student_info.courses c2 NATURAL JOIN student_info.schedule_data) AS c;
	
    SELECT COUNT(course_id)
    INTO num_classes
    FROM student_info.schedule_data;
    
    DROP TABLE IF EXISTS schedule_data;
    
END