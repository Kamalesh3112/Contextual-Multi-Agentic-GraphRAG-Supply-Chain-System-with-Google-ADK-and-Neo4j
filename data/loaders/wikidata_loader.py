from data.ingestion.sparql_extractor import SparqlExtractorClient

class WikidataLoader:
    def __init__(self, endpoint: str = SparqlExtractorClient.DEFAULT_ENDPOINT):
        self.client = SparqlExtractorClient(endpoint)

        def load_entity_data(self, entity_id: str) -> list:
           
            """Fetches basic information for a given Wikidata entity ID."""
            query = f"""
            SELECT ?propertyLabel ?valueLabel WHERE {{
            wd:{entity_id} ?propUrl ?value .
            ?property wikibase:directClaim ?propUrl .
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
            }}
            LIMIT 150
            """

            return self.client.get_results_as_list(query)

        def search_entities(self, search_term: str) -> list:
   
            """Searches for entities by label."""
            query = f"""
            SELECT ?item ?itemLabel ?itemDescription WHERE {{
            ?item rdfs:label ?itemLabel.
            FILTER(CONTAINS(LCASE(?itemLabel), LCASE("{search_term}"))).
            ?item schema:description ?itemDescription.
            FILTER(LANG(?itemLabel) = "en")
            FILTER(LANG(?itemDescription) = "en")
            }}
            LIMIT 15
            """

            return self.client.get_results_as_list(query)