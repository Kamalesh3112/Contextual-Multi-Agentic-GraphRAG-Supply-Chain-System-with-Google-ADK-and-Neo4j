from neo4j import GraphDatabase
from typing import Dict, List, Optional

from config.settings import settings

class Neo4jClient:
    def __init__(self):
        self.client = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth = (
                settings.NEO4J_USER,
                settings.NEO4J_PASSWORD,
            )
        )
        
        def close(self):
            self.driver.close()
    
    def execute_read(self, query: str, parameters: Optional[Dict] = None) -> List[Dict]:
        with self.driver.session() as session:
            result = session.run(
                query,
                parameters or {}
            )

            return [record.data() for record in result]
    
    def execute_write(self, query: str, parameters: Optional[Dict] = None) -> List[Dict]:
        with self.driver.session() as session:
            result = session.run(
                query,
                parameters or {}
            )

            return [record.data() for record in result]
    
    def health_check(self) -> bool:
        try:
            with self.driver.session() as session:
                session.run(
                    "RETURN 1"
                )
                return True
        
        except Exception:
            return False