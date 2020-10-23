# Basic connection to database

from sqlalchemy import create_engine


if __name__ == '__main__':
    engine = create_engine(
        'mysql://***REMOVED***')

    with engine.connect() as connection:
        result = connection.execute('SHOW tables FROM student_info')
        for row in result:
            print(row[0])
