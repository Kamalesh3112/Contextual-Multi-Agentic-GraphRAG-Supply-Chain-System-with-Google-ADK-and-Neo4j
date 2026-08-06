"""
Methods such as:
   - get_query_set()
   - execute_tool_query()
   - search_company()
   - search_supplier()
   - search_country()
   - get_node()
   - get_neighbors()
   - execute_cypher()
   - graph_statistics()
   - company_profile()
"""

from base_tool import BaseTool
from neo4j import GraphDatabase
import logging

class Neo4jTool(BaseTool):
    def __init__(self, uri, user, password):
        super().__init__("Neo4jTool")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def get_query_set(self, node_label = None, property_filters = None, limit = 50):
        """
        Dynamically generates the Cypher Query text and its parameters and returns a tuple (cypher_query, string, parameters_dictionary)
        """
        label_clause = f":{node_label}" if node_label is not None else ""
        cypher_query = f"MATCH (n{label_clause})"

        parameters= {}
        where_clauses = []

        if property_filters:
            for key, value in property_filters.items():
                where_clauses.append(f"n.{key} = ${key}")
                parameters[key] = value

        if where_clauses:
            cypher_query += "WHERE" + "AND".join(where_clauses) + " "

        else:
            property_filters()
            logging.error("There is something wrong in cypher query set, please check the neo4j__tool.py script")

        cypher_query += "RETURN n"
        if limit:
            cypher_query += f"LIMIT {limit}"
        return cypher_query, parameters

    def execute_tool_query(self, node_label = None, property_filters = None, limit = 20):
        """
        Uses get_query_set() to generate the payload then stores it into Neo4j DB
        """
        query, params = self.get_query_set(node_label = node_label, property_filters = property_filters, limit = limit)
        records = self.driver.execute_query(query, parameters_=params, database_ = "neo4j")
        return [record.data() for record in records]

    def search_company(self, name):
        return self.execute_cypher("MATCH (c:Company {name:$name}) RETURN c", {"name": name})

    def search_supplier(self, name):
        return self.execute_cypher("MATCH (s:Supplier {name:$name}) RETURN s", {"name": name})

    def search_country(self, name):
        return self.execute_cypher("MATCH (c:Country {name:$name}) RETURN c", {"name": name})

    def get_node(self, node_id):
        return self.execute_cypher("MATCH (n) WHERE id(n)=$id RETURN n", {"id": node_id})

    def get_neighbors(self, node_id):
        return self.execute_cypher("MATCH (n)-[r]->(m) WHERE id(n)=$id RETURN m,r", {"id": node_id})

    def execute_cypher(self, query, params=None, validation=True):
        with self.driver.session() as session:
            return session.run(query, params).data()

    def graph_statistics(self):
        return self.execute_cypher("CALL db.stats.retrieve()")

    def company_profile(self, name):
        return self.execute_cypher("""
        MATCH (c:Company {name:$name})-[r]->(n)
        RETURN c, collect({rel:type(r), neighbor:n}) AS profile
        """, {"name": name})

    def register(self, registry):
        registry["neo4j"] = self

    def shutdown(self):
        self.driver.close()