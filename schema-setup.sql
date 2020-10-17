DROP TABLE IF EXISTS student_info.student;

CREATE TABLE student_info.student(
	net_id VARCHAR(8) PRIMARY KEY NOT NULL UNIQUE,
    pass_word VARCHAR(30),
    current_semester INT NOT NULL,
    total_semesters INT NOT NULL,
    # require either null password (for data provider ONLY), or all three parameters cannot be null.
    CHECK ((pass_word = NULL AND current_semester = NULL AND total_semesters = NULL) OR
				(pass_word <> NULL AND current_semester <> NULL AND total_semesters <> NULL)),
    CHECK (pass_word = NULL OR (LENGTH(pass_word) > 10)) # requires password of length greater than 10 and less than 30
);

DROP TABLE IF EXISTS student_info.track;
CREATE TABLE student_info.track(
	field_name VARCHAR(30) NOT NULL REFERENCES student_info.courses(field_name), # can't take a track that doesn't exist
    interest VARCHAR(30) NOT NULL REFERENCES student_info.interest(field_name), # can't be interested in something that doesn't exist
    credit_hours INT NOT NULL,
    net_id VARCHAR(8) UNIQUE REFERENCES student_info.student(net_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    PRIMARY KEY(net_id, field_name, interest)
);

DROP TABLE IF EXISTS student_info.courses;
CREATE TABLE student_info.courses(
	course_id VARCHAR(10) PRIMARY KEY NOT NULL UNIQUE,
    credits INT NOT NULL,
    field_name VARCHAR(30) NOT NULL, # ex: CS-ENG, CS-X, CS-Minor, Business
    interest VARCHAR(30) NOT NULL, # ex: HPC, Big Data (analogous to "stream")
    category VARCHAR(20) NOT NULL
);

DROP TABLE IF EXISTS student_info.enrollments;
CREATE TABLE student_info.enrollments(
	net_id VARCHAR(8) NOT NULL REFERENCES student_info.student(net_id),
    course_id VARCHAR(10) NOT NULL REFERENCES student_info.courses(course_id),
    semester INT NOT NULL CHECK (semester > 0), # can't be a negative semester!!
    rating INT NOT NULL CHECK (rating >= 0 AND rating <= 10), # fixed range,
    PRIMARY KEY(net_id, course_id)
);
