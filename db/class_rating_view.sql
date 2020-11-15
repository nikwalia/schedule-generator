CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `admin`@`%` 
    SQL SECURITY DEFINER
VIEW `class_rating` AS
    SELECT 
        `e`.`course_id` AS `course_id`,
        AVG(`e`.`rating`) AS `avgRating`
    FROM
        `enrollments` `e`
    GROUP BY `e`.`course_id`
    ORDER BY AVG(`e`.`rating`) DESC
