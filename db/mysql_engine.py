import pandas as pd
import glob, os
from sqlalchemy import create_engine

class MySQLEngine:
    def __init__(self, **kwargs):
        """
        Store connection URL, create interaction instance, and establish connection.
        
        :param kwargs: contains information for connecting to DB
        """
        if 'url' in kwargs:
            self.__url = kwargs['url']
        else:
            self.__url = 'mysql://' + kwargs['username'] + ':' + kwargs['password'] + '@' + kwargs['server']
        self.__engine = create_engine(self.__url)
        self.__connection = self.__engine.connect()


    def __del__(self):
        """
        Destructor. Closes connection, then deletes members.
        """
        self.__connection.close()
        del self.__connection
        del self.__engine
        del self.__url


    def open(self):
        """
        Opens a connection if it was manually closed.
        """
        if self.__engine is None:
            self.__engine = create_engine(self.__url)
        if self.__connection is None:
            self.__connection = self.__engine.connect()


    def close(self):
        """
        Manually closes a connection. Should be used only in debug when engine is not automatically deleted.
        """
        if self.__connection is not None:
            self.__connection.close()
            self.__connection = None
        if self.__engine is not None:
            self.__engine = None


    def is_open(self):
        """
        Checks if the connection is already open
        """
        return self.__connection is not None and self.__engine is not None

    
    def __get_headers(self, table_name: str):
        if self.__engine is None or self.__connection is None:
            raise AttributeError("Engine or connection are not initialized")
        return [row[0] for row in self.__connection.execute('SHOW COLUMNS FROM student_info.%s' % table_name)]

    
    def __get_header_types(self, table_name: str):
        if self.__engine is None or self.__connection is None:
            raise AttributeError("Engine or connection are not initialized")
        return [row[1] for row in self.__connection.execute('SHOW COLUMNS FROM student_info.%s' % table_name)]
    

    def wrapped_query(self, query: str, table_name: str):
        """
        Gets data and returns it in a Pandas dataframe
        
        :param query: string query to execute
        :param table_name: string table name to fetch from
        
        :return: Pandas DataFrame containing query results
        """
        if self.__engine is None or self.__connection is None:
            raise AttributeError("Engine or connection are not initialized")
        if 'SELECT' not in query:
            raise ValueError('Retrieving data only')
        _res = self.__connection.execute(query)
        _table_headers = self.__get_headers(table_name)
        _dat = []
        for _row in _res:
            _dat.append(_row)
        return pd.DataFrame(_dat, columns=_table_headers)


    def raw_operation(self, query: str, return_val=False):
        """
        Executes a raw MySQL command
        
        :param query: string query to execute
        :param return_val: boolean of whether the query will return something.
                            Defaults to False.
        
        :return: Pandas DataFrame if return_val == True
        """
        if self.__engine is None or self.__connection is None:
            raise AttributeError("Engine or connection are not initialized")
        if return_val:
            res = self.__connection.execute(query)
            out = []
            for row in res:
                out.append(row)
            return out
        else:
            self.__connection.execute(query)

    
    def insert_df(self, data: pd.DataFrame, table_name: str):
        """
        Inserts data into an already-existing database table. Validates columns
        to ensure the table being inserted into matches the data types of the
        dataframe.
        
        :param data: pandas DataFrame containing data to insert
        :param table_name: which table to insert to
        """
        if self.__engine is None or self.__connection is None:
            raise AttributeError("Engine or connection are not initialized")
        _table_headers = self.__get_header_types(table_name)
        for df_header, table_header in zip(data.dtypes, _table_headers):
            if df_header in ('float64', 'float') and table_header != 'float':
                raise TypeError('Incompatible data types: %s and %s' % (df_header, table_header))
            elif df_header in ('int64', 'int') and table_header != 'int':
                raise TypeError('Incompatible data types: %s and %s' % (df_header, table_header))
            elif df_header == 'object' and 'varchar' not in table_header and table_header != 'json':
                raise TypeError('Incompatible data types: %s and %s' % (df_header, table_header))
        
        _name = 'student_info.%s' % table_name
        _command = 'INSERT INTO student_info.%s VALUES\n' % table_name
        _values = []
        insert_tuple = []
        for dt in data.dtypes:
            if dt == 'object':
                insert_tuple.append("'%s'") # strings are the only objects allowed
            elif dt == 'float64' or dt == 'float':
                insert_tuple.append('%f')
            elif dt == 'int64' or dt == 'int':
                insert_tuple.append('%d')
        insert_tuple = '(' + ', '.join(insert_tuple) + ')'
        for row in data.to_numpy():
            _values.append(insert_tuple % tuple(row))
        _command += ',\n'.join(_values)
        self.__connection.execute(_command)

    
    def insert_tuple(self, data: tuple, table_name: str):
        """
        Inserts data into an already-existing database table. Validates columns
        to ensure the table being inserted into matches the data types of the
        tuple
        
        :param data: tuple containing data to insert
        :param table_name: which table to insert to
        """
        if self.__engine is None or self.__connection is None:
            raise AttributeError("Engine or connection are not initialized")
        _table_headers = self.__get_header_types(table_name)
        tuple_types = tuple([type(val) for val in data])
        for tuple_dtype, table_header in zip(tuple_types, _table_headers):
            if tuple_dtype in ('float64', 'float') and table_header != 'float':
                raise TypeError('Incompatible data types: %s and %s' % (tuple_dtype, table_header))
            elif tuple_dtype in ('int64', 'int') and table_header != 'int':
                raise TypeError('Incompatible data types: %s and %s' % (tuple_dtype, table_header))
            elif tuple_dtype == 'object' and 'varchar' not in table_header and table_header != 'json':
                raise TypeError('Incompatible data types: %s and %s' % (tuple_dtype, table_header))

        _name = 'student_info.%s' % table_name
        _command = 'INSERT INTO student_info.%s VALUES\n' % table_name
        
        insert_tuple = []
        for dt in data.dtypes:
            if dt == 'object':
                insert_tuple.append("'%s'") # strings are the only objects allowed
            elif dt == 'float64' or dt == 'float':
                insert_tuple.append('%f')
            elif dt == 'int64' or dt == 'int':
                insert_tuple.append('%d')
        insert_tuple = '(' + ', '.join(insert_tuple) + ')'

        _command += (insert_tuple % data)
        self.__connection.execute(_command)

def loadEngine():
    """
    Creates an SQL engine instance.
    """
    url = ''
    server_info_path = ''
    if 'api' in os.getcwd():
        server_info_path += '../'
    if 'server' in os.getcwd():
        server_info_path += '../'
    with open(server_info_path + "server_info", "r") as f:
        url = f.readline().strip()
    e = MySQLEngine(url = 'mysql+py' + url)
    return e


if __name__ == '__main__':
    with open("../server_info", "r") as f:
        e = MySQLEngine(url = f.readline().strip())
        print(e.wrapped_query('SELECT * FROM student_info.courses', 'courses'))
