import pandas as pd
import glob, os
from sqlalchemy import create_engine
from sqlalchemy.orm import create_session

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
        self.__connection = None


    def __del__(self):
        """
        Destructor. Closes connection, then deletes members.
        """
        del self.__connection
        del self.__engine
        del self.__url


    def open(self):
        """
        Opens a connection if it was manually closed.
        """
        if self.__engine is None:
            self.__engine = create_engine(self.__url)


    def close(self):
        """
        Manually closes a connection. Should be used only in debug when engine is not automatically deleted.
        """
        if self.__engine is not None:
            self.__engine = None


    def is_open(self):
        """
        Checks if the connection is already open
        """
        return self.__connection is not None and self.__engine is not None


    def __get_header_types(self, table_name: str):
        if self.__engine is None:
            raise AttributeError("Engine is not initialized")
        self.__connection = self.__engine.connect()
        res = [row[1] for row in self.__connection.execute('SHOW COLUMNS FROM student_info.%s' % table_name)]
        self.__connection.close()
        self.__connection = None
        return res
    

    def wrapped_query(self, query: str):
        """
        Gets data and returns it in a Pandas dataframe
        
        :param query: string query to execute
        
        :return: Pandas DataFrame containing query results
        """
        if self.__engine is None:
            raise AttributeError("Engine is not initialized")
        self.__connection = self.__engine.connect()
        if 'SELECT' not in query:
            raise ValueError('Retrieving data only')
        _res = self.__connection.execute(query)
        _table_headers = _res.keys()
        _dat = []
        for _row in _res:
            _dat.append(_row)
        if self.__connection is not None: 
            self.__connection.close()
            self.__connection = None
        return pd.DataFrame(_dat, columns=_table_headers)


    def raw_operation(self, query: str, return_val=False):
        """
        Executes a raw MySQL command
        
        :param query: string query to execute
        :param return_val: boolean of whether the query will return something.
                            Defaults to False.
        
        :return: Pandas DataFrame if return_val == True
        """
        if self.__engine is None:
            raise AttributeError("Engine is not initialized")
        self.__connection = self.__engine.connect()
        if return_val:
            res = self.__connection.execute(query)
            out = []
            for row in res:
                out.append(row)
            return out
        else:
            self.__connection.execute(query)
        self.__connection.close()
        self.__connection = None


    def stored_proc(self, stored_proc: str, input_args: list, output_arg_length: int):
        '''
        Call a stored procedure. Note that this does not support INOUT arguments.

        :param stored_proc: name of stored procedure
        :param input_args: args to pass into stored procedure
        :output_arg_length: number of arguments to return. can be 0.
        :returns: results of the stored procedure
        '''
        if self.__engine is None:
            raise AttributeError("Engine is not initialized")
        self.__connection = self.__engine.connect()
        
        _query_tuple = []
        for elem in input_args:
            if isinstance(elem, str):
                _query_tuple.append("'{}'")
            else:
                _query_tuple.append("{}")

        _output_tuple = []
        for i in range(output_arg_length):
            _output_tuple.append('@res{}'.format(i))

        _query_tuple.extend(_output_tuple)
            
        _command = "CALL {}({});".format(stored_proc, ', '.join(_query_tuple).format(*input_args))
        self.__connection.execute(_command)

        if output_arg_length > 0:
            _output = []
            _res_command = "SELECT " + ', '.join(_output_tuple) + ";"
            _results = self.__connection.execute(_res_command)
            for _res in _results:
                _output.append(_res)
        
        self.__connection.close()
        self.__connection = None
        return _output
        
        
    def drop_rows(self, query: str):
        """
        Drops rows from a table based on some conditions

        :param query: the delete command to execute
        """
        if self.__engine is None:
            raise AttributeError("Engine is not initialized")

        if "DELETE" not in query:
            raise ValueError("Not dropping anything")
        if "WHERE" not in query:
            raise ValueError("Unsafe dropping without WHERE not permitted")

        self.__connection = self.__engine.connect()
        self.__connection.execute(query)
        self.__connection.close()
        self.__connection = None

    
    def insert_df(self, data: pd.DataFrame, table_name: str):
        """
        Inserts data into an already-existing database table. Validates columns
        to ensure the table being inserted into matches the data types of the
        dataframe.
        
        :param data: pandas DataFrame containing data to insert
        :param table_name: which table to insert to
        """
        if self.__engine is None:
            raise AttributeError("Engine is not initialized")
        _table_headers = self.__get_header_types(table_name)
        self.__connection = self.__engine.connect()
        
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
        self.__connection.close()
        self.__connection = None

    
    def insert_tuple(self, data: tuple, table_name: str):
        """
        Inserts data into an already-existing database table. Validates columns
        to ensure the table being inserted into matches the data types of the
        tuple
        
        :param data: tuple containing data to insert
        :param table_name: which table to insert to
        """
        if self.__engine is None:
            raise AttributeError("Engine is not initialized")
        self.__connection = self.__engine.connect()
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
        self.__connection.close()
        self.__connection = None

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
        print(e.wrapped_query('SELECT * FROM student_info.courses'))
