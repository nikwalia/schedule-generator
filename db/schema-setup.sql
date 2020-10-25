DROP TABLE IF EXISTS student_info.student;

CREATE TABLE student_info.student(
	net_id VARCHAR(8) PRIMARY KEY NOT NULL UNIQUE, -- ex: nikashw2
    pass_word VARCHAR(30), -- you don't get to know
    start_semester VARCHAR(10) NOT NULL, -- ex: FA19
    current_semester VARCHAR(10) NOT NULL, -- ex: FA20
    total_semesters INT NOT NULL, -- 8
    CHECK (pass_word = NULL OR (LENGTH(pass_word) > 10)) -- requires password of length greater than 10 and less than 30
);

DROP TABLE IF EXISTS student_info.track;
CREATE TABLE student_info.track(
	field_name VARCHAR(30) NOT NULL, -- ex. CS-ENG, CS-Minor, CS-X, ACC
    -- field helps us determine which neural network to run and which Neo4J network to query
    interest VARCHAR(30) NOT NULL, -- ex. HPC, Big Data
    -- interest helps us filter out classes post-network stage
    credit_hours INT NOT NULL, -- the number of credit hours a student allocates to that track
    net_id VARCHAR(8) UNIQUE REFERENCES student_info.student(net_id) -- ex. nikashw2
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    PRIMARY KEY(net_id, field_name, interest)
    -- to guarantee field/interest validity, make a drop-down in the front-end
);

DROP TABLE IF EXISTS student_info.courses;
CREATE TABLE student_info.courses(
	course_id VARCHAR(10) PRIMARY KEY NOT NULL UNIQUE, -- ex. CS126, CS498-DL
    credits INT NOT NULL, -- ex. 3 or 4 (for CS411)
    interest VARCHAR(30) NOT NULL -- ex: HPC, Big Data (analogous to "stream")
);

DROP TABLE IF EXISTS student_info.enrollments;
CREATE TABLE student_info.enrollments(
	net_id VARCHAR(8) NOT NULL REFERENCES student_info.student(net_id), -- ex. nikashw2
    course_id VARCHAR(10) NOT NULL REFERENCES student_info.courses(course_id), -- ex. CS126, CS498-DL
    semester VARCHAR(10) NOT NULL, -- ex. FA20. Any credits before college are labeled as "BEFORE".
    -- to guarantee semester validity, make a drop-down in the front-end
    rating INT NOT NULL CHECK (rating >= 0 AND rating <= 10), -- fixed range
    PRIMARY KEY(net_id, course_id)
);
