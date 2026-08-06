"""
Graph Operations through Queue:
   - multi_hop_traversal()
   - dependency_chain()
   - shortest_path()
   - supply_chain()
   - upstream()
   - downstream()
   - risk_propagation()
   - neighborhood()
   - GraphRAG Query
"""

from base_tool import BaseTool
from collections import deque

class TraversalTool(BaseTool):
    def __init__(self, neo4j_tool=None, memory_tool=None):
        super().__init__("TraversalTool")
        self.neo4j = neo4j_tool
        self.memory = memory_tool

    def depth_first(self, graph, start_node):
        visited, stack = set(), [start_node]
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                stack.extend(graph.get(node, []))
        return visited

    def breadth_first(self, graph, start_node):
        visited, queue = set(), [start_node]
        while queue:
            node = queue.pop(0)
            if node not in visited:
                visited.add(node)
                queue.extend(graph.get(node, []))
        return visited

    # --- Business Methods ---
    def multi_hop_traversal(self, graph, start_node, hops=2):
        """Traverse outward from start_node for N hops."""
        frontier, visited = [start_node], {start_node}
        for _ in range(hops):
            next_frontier = []
            for node in frontier:
                for neighbor in graph.get(node, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        next_frontier.append(neighbor)
            frontier = next_frontier
        return visited

    def dependency_chain(self, graph, node):
        """Return ordered chain of dependencies upstream."""
        chain, stack = [], [node]
        while stack:
            current = stack.pop()
            deps = graph.get(current, [])
            chain.extend(deps)
            stack.extend(deps)
        return chain

    def shortest_path(self, graph, start, end):
        """Breadth-first shortest path between two nodes."""
        queue = deque([(start, [start])])
        visited = {start}
        while queue:
            node, path = queue.popleft()
            if node == end:
                return path
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None

    def supply_chain(self, graph, supplier):
        """Return all downstream entities from a supplier."""
        return self.breadth_first(graph, supplier)

    def upstream(self, graph, node):
        """Find all upstream nodes (reverse edges assumed)."""
        upstream_nodes = set()
        for src, targets in graph.items():
            if node in targets:
                upstream_nodes.add(src)
                upstream_nodes |= self.upstream(graph, src)
        return upstream_nodes

    def downstream(self, graph, node):
        """Find all downstream nodes."""
        return self.breadth_first(graph, node)

    def risk_propagation(self, graph, node, depth=3):
        """Propagate risk outward from node up to depth hops."""
        return self.multi_hop_traversal(graph, node, hops=depth)

    def neighborhood(self, graph, node, radius=1):
        """Return nodes within N hops of node."""
        return self.multi_hop_traversal(graph, node, hops=radius)

    def build_risk_subgraph(self, graph, product, country, company, risk_tool):
        sub_nodes = {product, country, company}
        sub_edges = []

        if graph[product].get("delay", {}).get(country, 0) > 5:
            sub_edges.append((product, "ships_to", country))

        demand = graph[product].get("demand", {}).get(country, 0)
        supply = graph[product].get("supply", {}).get(country, 0)
        if demand > supply:
            sub_edges.append((product, "demand_in", country))

        offices = graph[company].get("offices", {}).get(country, 0)
        if offices < 2:
            sub_edges.append((company, "operates_in", country))

        subgraph = {"nodes": sub_nodes, "edges": sub_edges}

        risk_score = risk_tool.assess_node(product, {
            "delay": graph[product].get("delay", {}).get(country, 0),
            "demand_gap": max(0, demand - supply),
            "office_gap": max(0, 2 - offices)
        })

        if self.neo4j:
            for n in sub_nodes:
                self.neo4j.create_node("Entity", {"name": n})
            for src, rel, dst in sub_edges:
                self.neo4j.create_relationship_by_name(src, dst, rel)

        if self.memory:
            self.memory.save_context(product, {"product": product, "country": country, "risk_score": risk_score})

        return {"subgraph": subgraph, "risk_score": risk_score}

    # --- GraphRAG Query Interface ---
    def get_risk_clusters(self, country):
        """Query Neo4j for all risk clusters related to a given country."""
        if not self.neo4j:
            return []

        query = """
        MATCH (c:Entity {name:$country})<-[:ships_to|demand_in|operates_in]-(p:Entity)
        OPTIONAL MATCH (p)-[r]->(c)
        RETURN p.name AS product, c.name AS country, type(r) AS relation
        """
        results = self.neo4j.run_query(query, {"country": country})

        clusters = []
        for record in results:
            clusters.append({
                "product": record["product"],
                "country": record["country"],
                "relation": record["relation"]
            })

        return clusters

    def register(self, registry):
        registry["traversal"] = self

    def shutdown(self):
        # No resources to release for TraversalTool.
        # This placeholder keeps the tool lifecycle consistent.
        pass