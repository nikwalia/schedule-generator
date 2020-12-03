CREATE DEFINER=`admin`@`%` PROCEDURE `score_classes`(
	IN class_data JSON, -- has format '[{"course_id": "course 1", "score": score_of_neural_network}...]'
    IN credit_limit INT, -- 0 < credit_limit <= 18
    IN user_interest VARCHAR(15), -- EX- CS-ENG-HPC, CS-MINOR
    OUT best_schedule VARCHAR(200), -- has format course_1,course_2...
    OUT best_schedule_rating FLOAT
)
BEGIN
    -- temporary storage for cursor
	DECLARE currSchedule VARCHAR(200);
    DECLARE currSumCredits INT;
    DECLARE currNumClasses INT;
    DECLARE currSumGPA FLOAT;
    DECLARE currSumNetworkScore FLOAT;
    DECLARE currSumMatchInterest INT;
    DECLARE currSumAvgRating INT;
	DECLARE done int default 0;
	DECLARE scheduleCur CURSOR FOR SELECT DISTINCT course_ids FROM results;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

	DROP TABLE IF EXISTS class_data_table;
    DROP TABLE IF EXISTS interest_classes;
    DROP TABLE IF EXISTS results;

	-- converts JSON data into a table
	CREATE TEMPORARY TABLE class_data_table
	SELECT *
	FROM
		JSON_TABLE(
			class_data,
			'$[*]'
			COLUMNS(
				rowid FOR ORDINALITY,
				course_id VARCHAR(10) PATH "$.course_id" ERROR ON ERROR,
				score FLOAT PATH "$.score" ERROR ON ERROR
		)
	) AS T;

    -- compiles all the relevant information for ranking into one table
	CREATE TABLE interest_classes
	SELECT c1.course_id AS course_id,
			c1.credits AS credits,
			c1.gpa AS gpa,
			c2.score AS score,
			1 - CAST(ISNULL(JSON_SEARCH(interest, 'one', user_interest)) AS UNSIGNED) AS match_interest,
			IFNULL(r.avgRating, 5) AS avgRating
	FROM student_info.courses c1
	INNER JOIN
	student_info.class_data_table c2
	ON c1.course_id = c2.course_id
	LEFT JOIN
	student_info.class_rating r
	ON c1.course_id = r.course_id;

    ALTER TABLE interest_classes MODIFY course_id VARCHAR(200);
    
    -- compute all possible schedules within the user-defined credit limit
	CREATE TEMPORARY TABLE results
	WITH RECURSIVE comb (course_id, course_ids, sum_credits, num_classes, sum_gpa, sum_network_score, sum_match_interest, sum_avg_rating)
	AS (
			SELECT
				course_id,
				course_id AS course_ids,
				credits AS sumcredits,
				1,
				gpa AS sum_gpa,
				score AS sum_network_score,
				match_interest AS sum_match_interest,
				avgRating AS sum_avg_rating
			FROM interest_classes
			WHERE credits <= credit_limit
		UNION
			SELECT interest_classes.course_id AS course_id,
				CONCAT(comb.course_ids, ',', interest_classes.course_id) AS course_ids,
				interest_classes.credits + comb.sum_credits AS sum_credits,
				1 + comb.num_classes,
				interest_classes.gpa + comb.sum_gpa AS sum_gpa,
				interest_classes.score + comb.sum_network_score AS sum_network_score,
				interest_classes.match_interest + comb.sum_match_interest AS sum_match_interest,
				interest_classes.avgRating + comb.sum_avg_rating AS sum_avg_rating
			FROM interest_classes JOIN comb ON (comb.course_id < interest_classes.course_id)
			HAVING sum_credits <= credit_limit
	)
	SELECT course_ids, sum_credits, num_classes, sum_gpa, sum_network_score, sum_match_interest, sum_avg_rating FROM comb;

	ALTER TABLE results ADD INDEX (course_ids) USING HASH;
	
    -- calculate ranking
    ALTER TABLE results ADD schedule_ranking FLOAT;
    OPEN scheduleCur;
    
    REPEAT
		FETCH scheduleCur INTO currSchedule;
        SELECT sum_credits, num_classes, sum_gpa, sum_network_score, sum_match_interest, sum_avg_rating
        INTO currSumCredits, currNumClasses, currSumGPA, currSumNetworkScore, currSumMatchInterest, currSumAvgRating
        FROM results
        WHERE results.course_ids = currSchedule;
        
        UPDATE results
        SET results.schedule_ranking = ((currSumGPA / currNumClasses)
											+ (currSumAvgRating / currNumClasses)
                                            + (currSumNetworkScore / currNumClasses))
										/ (ABS(credit_limit - currSumCredits) + 1)
                                        * (currSumMatchInterest / currNumClasses)
                                        
        WHERE results.course_ids = currSchedule;
        
	UNTIL done
    END REPEAT;
        CLOSE scheduleCur;

    -- choose best schedule
    SELECT MAX(results.schedule_ranking)
    INTO best_schedule_rating
    FROM results;
    
    SELECT course_ids
    INTO best_schedule
    FROM results
    WHERE results.schedule_ranking = best_schedule_rating;

	DROP TABLE class_data_table; -- probably won't need to do this
	DROP TABLE interest_classes; -- HAVE TO DO THIS
	DROP TABLE results; -- probably won't need to do this
END
