"""
  Methods:
   - execute_query()
   - lookup_entity()
   - wikidata_search()
   - enrich_node()
   - ontology_lookup()
"""

from base_tool import BaseTool
from SPARQLWrapper import SPARQLWrapper, JSON

class SparqlTool(BaseTool):
    def __init__(self, endpoint_url):
        super().__init__("SparqlTool")
        self.sparql = SPARQLWrapper(endpoint_url)

    def execute_query(self, query):
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        return self.sparql.query().convert()["results"]["bindings"]

    def lookup_entity(self, entity_uri):
        return self.execute_query(f"SELECT ?p ?o WHERE {{ <{entity_uri}> ?p ?o }}")

    def wikidata_search(self, label):
        return self.execute_query(f"""
        SELECT ?item WHERE {{
            ?item rdfs:label "{label}"@en
        }}
        """)

    def enrich_node(self, entity_uri):
        return self.execute_query(f"""
        SELECT ?property ?value WHERE {{
            <{entity_uri}> ?property ?value
        }}
        """)

    def ontology_lookup(self, class_uri):
        return self.execute_query(f"SELECT ?s WHERE {{ ?s a <{class_uri}> }}")

    def register(self, registry):
        registry["sparql"] = self

    def shutdown(self):
        pass