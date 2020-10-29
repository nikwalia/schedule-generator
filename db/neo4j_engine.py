from neo4j import GraphDatabase


class Neo4JEngine:
    def __init__(self, uri: str, username: str, password: str):
        """
        Initializes engine.

        :param self:
        :param uri: location of Neo4J RDMS
        :param username: for auth
        :param password: for auth
        """
        self.__uri = uri
        self.__username = username
        self.__password = password
        self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__username, self.__password))
        self.__session = self.__driver.session()

    
    def __del__(self):
        self.__session.close()
        self.__driver.close()
        del self.__session
        del self.__driver
        del self.__password
        del self.__username
        del self.__uri


    def raw_operation(self, query, return_val = False):
        """
        Runs a raw Neo4J command

        :param self:
        :param query: a string query to execute
        :param return_val: boolean of whether the query will return something.
                            Defaults to False.
        
        :return: list if return_val == True
        """
        if return_val:
            response = list(self.__session.run(query))
            return response
        else:
            self.__session.run(query)


if __name__ == '__main__':
    conn = Neo4JEngine(uri="bolt://ec2-100-25-38-45.compute-1.amazonaws.com:7687", username="neo4j", password="test")
    conn.raw_operation('SHOW DATABASES')