#Multi-Hop Reasoning
from graph.neo4j_client import Neo4jClient

class GraphTraversal:
    MAX_HOPS = 5

    def __init__(
        self, 
        neo4j_client: Neo4jClient
    ):
        self.neo4j = neo4j_client
    
    #To find neighbors through neighbor search
    def get_neighbor(
        self,
        node_id: str
    ):
        query = """
        MATCH(n)-[r]->[m]
        WHERE n.company_id = $node_id
           OR n.country_code = $node_id
           OR n.risk_id = $node_id
        RETURN m,r
        """

        return self.neo4j.execute_read(
            query,
            {
                "node_id": node_id
            }
        )
    
    #Supplier Chain Traversal
    def supplier_chain_traversal(
        self, 
        company_id: str, 
        hops: int = 5):
        query = f"""
        MATCH path=
        (c:Company)
        [:SUPPLIES*1..{min(hops, self.MAX_HOPS)}]->
        (Supplier)

        WHERE c.company_id = $company_id

        RETURN path
        """

        return self.neo4j.execute_read(
            query,
            {
                "company_id": company_id
            }
        )
    
    #Dependency Traversal
    def dependency_chain_traversal(
        self,
        company_id: str,
        hops: int = 5
    ):
        query = f"""
        MATCH path=
        (c:Company)
        -[:DEPENDS_ON*1..{min(hops,self.MAX_HOPS)}]->
        (dependency)

        WHERE c.company_id=$company_id

        RETURN path
        """

        return self.neo4j.execute_read(
            query,
            {
                "company_id": company_id
            }
        )

    #Risk propagation traversal
    def upstream_risks_traversal(
        self,
        company_id: str
    ):

        query = """
        MATCH path=
        (c:Company)
        -[:DEPENDS_ON|SUPPLIES*1..4]->
        (supplier)

        -[:HAS_RISK]->
        (r:Risk)

        WHERE c.company_id=$company_id
        RETURN path,r
        """

        return self.neo4j.execute_read(
            query,
            {
                "company_id": company_id
            }
        )
    
    #Country Risk Traversal
    def country_risks_traversal(
        self,
        company_id: str
    ):

        query = """
        MATCH
        (c:Company)
        -[:LOCATED_IN]->
        (country:Country)
        -[:HAS_RISK]->
        (risk:Risk)

        WHERE c.company_id=$company_id
        RETURN country,risk
        """

        return self.neo4j.execute_read(
            query,
            {
                "company_id": company_id
            }
        )
    
    #Risk context for Risk Agent
    def full_risk_context(
        self,
        company_id: str
    ):

        return {

            "dependency_risks":
                self.upstream_risks(
                    company_id
                ),

            "country_risks":
                self.country_risks(
                    company_id
                ),

            "supplier_chain":
                self.supplier_chain(
                    company_id
                )
        }