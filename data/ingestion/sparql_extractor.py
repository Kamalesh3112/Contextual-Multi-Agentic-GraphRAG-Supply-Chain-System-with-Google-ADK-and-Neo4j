from SPARQLWrapper import SPARQLWrapper, JSON
from typing import Any
import logging

logger = logging.getlogger(__name__)

class SparqlExtractorClient:
    DEFAULT_ENDPOINT = "https://query.wikidata.org/sparql"

    def __init__(self, DEFAULT_ENDPOINT: str, user_agent: str = "GraphRAG-Agent/1.0"):
        
        self.sparql = SPARQLWrapper(self.DEFAULT_ENDPOINT)
        self.sparql.addCustomHttpHeader("User-Agent", user_agent)

    def execute_query(self, query: str) -> dict[str, Any]:
        
        try:
            self.sparql.setQuery(query)
            self.sparql.setReturnFormat(JSON)

            return self.sparql.query().convert()

        except Exception as e:
            
            logging.error(f"SPARQL Query failed: {e}")
            return {"error": str(e),
                    "results": {"bindings": []}
                   }

    #def validate_query(self, query: str, result: bool) -> dict[str, Any]:


    def get_results_as_list(self, query: str) -> list:
        """Executes query and returns a simplified list of dictionaries."""

        data = self.execute_query(query)

        bindings = data.get("results", {}).get("bindings", [])
        results = []
        for row in bindings:
            item = {key: row[key]["value"] for key in row}
            results.append(item)
        return results