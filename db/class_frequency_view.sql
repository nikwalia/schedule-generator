CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `admin`@`%` 
    SQL SECURITY DEFINER
VIEW `class_frequency` AS
    SELECT 
        `e`.`course_id` AS `course_id`,
        `e`.`semester_taken` AS `semester_taken`,
        AVG(`e`.`rating`) AS `avgRating`
    FROM
        `enrollments` `e`
    GROUP BY `e`.`course_id` , `e`.`semester_taken`
    ORDER BY AVG(`e`.`rating`) DESC