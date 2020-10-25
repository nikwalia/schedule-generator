from sqlalchemy import create_engine

def addStudent(netid, password, curr_sem, total_sem):
	s = 'INSERT INTO student_info.student VALUES ("%s", "%s", %i, %i)' % (netid, password, curr_sem, total_sem)
	connection.execute(s)

def addTrack(fieldname, interest, credithrs, netid):
	s = 'INSERT INTO student_info.track VALUES ("%s", "%s", %i, "%s")' % (fieldname, interest, credithrs, netid)
	connection.execute(s)

def addCourse(courseid, credits, interest):
	s = 'INSERT INTO student_info.courses VALUES ("%s", %i, "%s")' % (courseid, credits, interest)
	connection.execute(s)

def addEnrollment(netid, courseid, sem, rating):
	s = 'INSERT INTO student_info.enrollments VALUES ("%s", "%s", "%s", %i)' % (netid, courseid, sem, rating)
	connection.execute(s)

if __name__ == '__main__':
    engine = create_engine('mysql+pymysql://***REMOVED***')

    with engine.connect() as connection:
    	#addStudent("taylorswift", "blahblahbalhahahhaha", 13, 13)
    	#addTrack("CS-Minor", "Business", 200, "bangaru2")
    	#addCourse("CS411", 3, "Big Data")
    	#addEnrollment("bangaru2", "CS233", "FA20", 1)
    	result = connection.execute('SELECT * FROM student_info.enrollments')
    	for row in result:
    		print(row)