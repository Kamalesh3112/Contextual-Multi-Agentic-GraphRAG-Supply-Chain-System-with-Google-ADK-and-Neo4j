QUERY_TEMPLATES = {
    "company_by_name":"""
        MATCH(c:Company)
        WHERE toLower(c.name)   
        CONTAINS ToLower($name)
        RETURN c
        LIMIT 20
    """,

    "country_by_name": """
        MATCH(c:Country)
        WHERE toLower(c:name)
        CONTAINS toLower($name)
        RETURN c
        LIMIT 20
    """,

    "company_risks": """
        MATCH (c:Company)-[:HAS_RISK]->[r:Risk]
        WHERE c.company_id = $companyid
        RETURN r
    """,

    "country_risks": """
        MATCH (C:Country)-[:HAS_RISK]->[r:Risk]
        WHERE c.company_code = $companycode
        RETURN r
    """,

    "company_dependencies": """
        MATCH path=

        (c:Company)
        -[:DEPENDS_ON*1..5]->
        (dependency)

        WHERE c.company_id=$company_id

        RETURN path
    """,

    "supplier_chain": """
        MATCH path=

        (c:Company)
        -[:SUPPLIES*1..5]->
        (supplier)

        WHERE c.company_id=$company_id

        RETURN path
    """,

    "port_usage": """
        MATCH

        (c:Company)
        -[:USES_PORT]->
        (p:Port)

        WHERE c.company_id=$company_id

        RETURN p
    """,

    "shipment_paths": """
        MATCH path=

        (s:Shipment)
        -[:SHIPS_THROUGH]->
        (p:Port)

        RETURN path
    """
}