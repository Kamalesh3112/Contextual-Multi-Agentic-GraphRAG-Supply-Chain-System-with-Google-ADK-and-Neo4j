#Query construction safety layer for Query Agent
from typing import Dict, Any

class QueryDynamicBuilder:
    ALLOWED_GRAPH_NODES = {
        "Company",
        "Country",
        "Port",
        "Risk",
        "Shipment",
        "Product"
    }

    ALLOWED_GRAPH_RELATIONs = {
        "SUPPLIES",
        "LOCATED_IN",
        "HAS_OFFICES",
        "USES_PORT",
        "HAS_RISK",
        "DEPENDS_ON",
        "SHIPS_THROUGH"
    }

    @classmethod
    def build_entity_prompt(
        cls,
        label: str,
        property_name: str,
        value: str
    ):
        if label not in cls.ALLOWED_GRAPH_NODES:
            raise ValueError(
                f"UnSupported label: {label}"
            )
    
        query = f"""
        MATCH (n:{label})

        WHERE n.{property_name} = $value

        RETURN n
        """

        return (
            query,
            {
                "value": value
            }
        )
    
    @classmethod
    def build_traversal_prompt(
        cls,
        start_label: str,
        relationship: str,
        max_hops: int = 3
    ):
    
        if relationship not in cls.ALLOWED_GRAPH_RELATIONs:
            raise ValueError(
                f"Unsupported relation: {relationship}, yet to be configured in the GraphRAG Edge"
            )
        
        max_hops = min(max_hops, 5)

        query = f"""
        MATCH path=(n:{start_label})
        -[:{relationship}*1..{max_hops}]->
        (m)

        RETURN path
        """

        return query