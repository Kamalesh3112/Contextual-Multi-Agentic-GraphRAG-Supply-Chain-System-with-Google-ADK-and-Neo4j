INDEX_CYPHER = [
    "CREATE INDEX company_name_index IF NOT EXIST FOR (c:company) ON (c.name)",
    "CREATE INDEX country_name_index IF NOT EXIST FOR (c:company) ON (c.name)",
    "CREATE INDEX risk_category_index IF NOT EXIST FOR (c:company) ON (c.name)"
]