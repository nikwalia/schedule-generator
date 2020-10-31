CREATE DEFINER=`admin`@`%` FUNCTION `convert_semester`(
	semester VARCHAR(10)
) RETURNS int
    DETERMINISTIC
BEGIN
	IF semester LIKE 'SP%' THEN
		RETURN CAST(SUBSTRING(semester, 3, 2) AS UNSIGNED) * 2;
	ELSEIF semester LIKE 'FA%' THEN
		RETURN 1 + CAST(SUBSTRING(semester, 3, 2) AS UNSIGNED) * 2;
	ELSEIF semester = 'BEFORE' THEN
		RETURN 0;
	ELSE
		RETURN -1; -- invalid input
	END IF;
END