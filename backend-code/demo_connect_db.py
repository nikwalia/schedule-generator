# Basic connection to database
# author: Nikash Walia

from sqlalchemy import create_engine


if __name__ == '__main__':
    engine = create_engine(
        'mysql://admin:S8sLjq2ZJoZIRqy5@student-information-mysql.cwmmlvorulh4.us-east-1.rds.amazonaws.com')

    with engine.connect() as connection:
        result = connection.execute('SHOW tables FROM student_info')
        for row in result:
            print(row[0])
