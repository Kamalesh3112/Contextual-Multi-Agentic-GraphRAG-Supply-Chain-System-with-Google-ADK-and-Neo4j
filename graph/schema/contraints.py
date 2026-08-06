CONSTRAINT_CYPHER =[
    "CREATE CONSTRAINT company_id IF NOT EXIST (c:Company) REQUIRE c.company_id IS UNIQUE",
    "CREATE CONSTRAINT country_id IF NOT EXIST (c:Country) REQUIRE c.country_code IS UNIQUE",
    "CREATE CONSTRAINT risk_id IF NOT EXIST (r:Risk) REQUIRE r.risk_id IS UNIQUE"
]