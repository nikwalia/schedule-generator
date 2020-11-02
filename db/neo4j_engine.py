from neo4j import GraphDatabase


class Neo4JEngine:
    def __init__(self, uri: str, username: str, password: str):
        """
        Initializes engine.

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


    def open(self):
        """
        Opens a connection if it was manually closed.
        """
        if self.__driver is None:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__username, self.__password))
        if self.__session is None:
            self.__session = self.__driver.session()


    def close(self):
        """
        Manually closes a connection. Should be used only in debug when engine is not automatically deleted.
        """
        if self.__session is not None:
            self.__session.close()
            self.__session = None
        if self.__driver is not None:
            self.__driver.close()
            self.__driver = None


    def is_open(self):
        """
        Checks if the connection is already open
        """
        return self.__session is not None and self.__driver is not None


    def raw_operation(self, query: str, return_val = False):
        """
        Runs a raw Neo4J command

        :param query: a string command to execute
        :param return_val: boolean of whether the query will return something.
                            Defaults to False.
        
        :return: list if return_val == True
        """
        if self.__driver is None or self.__session is None:
            raise AttributeError("Driver or session are not initialized")
        if return_val:
            response = list(self.__session.run(query))
            return response
        else:
            self.__session.run(query)


    def wrapped_query(self, query: str):
        """
        Runs a Neo4J search command. Needs to be refined to transform JSON into easy-to-use object

        :param query: a string query to execute
        
        :return: a JSON-style object
        """
        if self.__driver is None or self.__session is None:
            raise AttributeError("Driver or session are not initialized")

        if 'MATCH' not in query.upper() or any(['MERGE', 'SET'] in query.upper()):
            raise ValueError('Command can only be a query')
        response = list(self.__session.run(query))
        return response


    def insert_node(self, query: str):
        """
        Runs a Neo4J command to insert a standalone node. Needs to be refined.

        :param query: a string command to execute
        """
        if self.__driver is None or self.__session is None:
            raise AttributeError("Driver or session are not initialized")

        if 'CREATE' not in query.upper():
            raise ValueError('Command can only be an insert')
        self.__session.run(query)


    def get_potential_classes(self, prereqs: list):
        """
        Runs a Neo4J command to get all the classes a student can take based on an input list.
        
        :param prereqs: a list of all the classes a student has taken
        :return: a list of all classes a student can take the following semester
        """
        if self.__driver is None or self.__session is None:
            raise AttributeError("Driver or session are not initialized")
        prereqs = prereqs + ['NOPREREQS']
        class_command = "MATCH (o: OR)<-[:PREREQ]-(p: Class)\n" \
                + "WHERE p.courseId IN " + str(prereqs) + "\n" \
                + "WITH COLLECT(DISTINCT o) AS or_list\n" \
                + "MATCH (c: Class)<-[:HAS]-(a: AND)<-[:HAS]-(o2: OR)\n" \
                + "WITH or_list, c, a, COLLECT(DISTINCT o2) AS o2_list\n" \
                + "WHERE apoc.coll.containsAll(or_list, o2_list)\n" \
                + "RETURN c.courseId"
        matched_classes = self.__session.run(class_command)
        matched_classes = [record[0] for record in matched_classes]
        return list(set(matched_classes) - set(prereqs))


    def get_class_description(self, class_name: str):
        """
        Gets the description of a class.

        :param class_name: the class to get
        :return: a string representing the class's information
        """
        if self.__driver is None or self.__session is None:
            raise AttributeError("Driver or session are not initialized")
        elif class_name is None:
            raise ValueError("class_name cannot be None")
        description_command = "MATCH (c: Class)\n" \
                                "WHERE c.courseId = '%s'\n" \
                                "RETURN c.description" % class_name
        desc = self.__session.run(description_command)[0]
        return desc
