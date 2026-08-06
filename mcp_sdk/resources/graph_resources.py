"""
  Read-only resources: (Exposes metadata for agents from GraphDB through MCP)
  1. ontology
  2. schema
  3. constraints
  4. indexes
  5. node_types
  6. relationship_types
  7. graph_statistics
"""
SUPPLY_CHAIN_SCHEMA = {
    "nodes": ["Country", "Suppliers", "Manufacturer", "Distributor", "Retailer", "Product"],
    "edges": ["supplies", "ships_to", "sells_to", "owns_from", "ships_through"]
}

DATASETS = {
    "SupplyGraph":"https://arxiv.org/html/2401.15299v3",
    "DataCo":"https://www.kaggle.com/datasets/data-co",
    "GSCF_finetune": "https://huggingface.co/datasets/gscf_finetune"
}

RESOURCES = {
    "ontology": "Graph ontology metadata",
    "schema": SUPPLY_CHAIN_SCHEMA,
    "constraints": "Graph constraints metadata",
    "indexes": "Graph indexes metadata",
    "node_types": ["Country","Supplier","Company","Product"],
    "relationship_types": ["supplies","ships_to","sells_to","owns_from","ships_through"],
    "graph_statistics": "Graph statistics metadata"
}

def register(registry):
    registry["resources"] = RESOURCES

def shutdown():
    # No cleanup is required for these read-only resource metadata definitions.
    # This function exists to satisfy the expected module interface.
    pass