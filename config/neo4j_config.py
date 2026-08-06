from neo4j import GraphDatabase
from config.settings import settings

driver = GraphDatabase(
    settings.NEO4J_URI,
    auth = (
        settings.NEO4J_USERNAME,
        settings.NEO4J_PASSWORD
    )
)