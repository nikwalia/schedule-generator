# Basic connection to database

from sqlalchemy import create_engine


if __name__ == '__main__':
    with open("../server_info", "r") as f:
        url = f.readline()
    engine = create_engine(url)

    with engine.connect() as connection:
        result = connection.execute('SHOW tables FROM student_info')
        for row in result:
            print(row[0])
