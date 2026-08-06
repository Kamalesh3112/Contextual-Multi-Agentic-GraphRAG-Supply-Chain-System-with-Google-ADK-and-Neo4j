from graph.neo4j_client import Neo4jClient


class GraphLoader:

    def __init__(self):

        self.neo4j = Neo4jClient()


    def load_company(self, company: dict):

        query = """
        MERGE (c:Company {company_id:$company_id})

        SET
            c.name = $name
        """

        self.neo4j.execute_query(query, company)


    def load_country(self, country: dict):

        query = """
        MERGE (c:Country {country_code:$country_code})

        SET
            c.name = $name
        """

        self.neo4j.execute_query(query, country)


    def load_risk(self, risk: dict):

        query = """
        MERGE (r:Risk {risk_id:$risk_id})

        SET
            r.risk_type = $risk_type,
            r.severity = $severity,
            r.description = $description
        """

        self.neo4j.execute_query(query, risk)


    def load_company_country_relationship(
        self,
        company_id: str,
        country_code: str
    ):

        query = """
        MATCH (company:Company {company_id:$company_id})

        MATCH (country:Country {country_code:$country_code})

        MERGE (company)-[:LOCATED_IN]->(country)
        """

        self.neo4j.execute_query(
            query,
            {
                "company_id": company_id,
                "country_code": country_code
            }
        )


    def load_country_risk_relationship(
        self,
        country_code: str,
        risk_id: str
    ):

        query = """
        MATCH (country:Country {country_code:$country_code})

        MATCH (risk:Risk {risk_id:$risk_id})

        MERGE (country)-[:HAS_RISK]->(risk)
        """

        self.neo4j.execute_query(
            query,
            {
                "country_code": country_code,
                "risk_id": risk_id
            }
        )


    def load_supplier_relationship(
        self,
        supplier_id: str,
        company_id: str
    ):

        query = """
        MATCH (supplier:Company {company_id:$supplier_id})

        MATCH (company:Company {company_id:$company_id})

        MERGE (supplier)-[:SUPPLIES]->(company)
        """

        self.neo4j.execute_query(
            query,
            {
                "supplier_id": supplier_id,
                "company_id": company_id
            }
        )