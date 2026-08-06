"""
Uses Neo4j's Agent Memory Service (AMS)
 Methods:
  1. save_conversation()
  2. retrieve_memory()
  3. entity_memory()
  4. reasoning_memory()
  5. reflection_memory()
  6. summarize_memory()
  7. clear_memory()
"""

from base_tool import BaseTool

class MemoryTool(BaseTool):
    def __init__(self, ams_client):
        super().__init__("MemoryTool")
        self.ams = ams_client  # Neo4j Agent Memory Service client

    def save_conversation(self, agent_id, conversation):
        return self.ams.save(agent_id, "conversation", conversation)

    def retrieve_memory(self, agent_id):
        return self.ams.retrieve(agent_id)

    def entity_memory(self, agent_id, entity):
        return self.ams.save(agent_id, "entity", entity)

    def reasoning_memory(self, agent_id, reasoning_chain):
        return self.ams.save(agent_id, "reasoning", reasoning_chain)

    def reflection_memory(self, agent_id, reflection):
        return self.ams.save(agent_id, "reflection", reflection)

    def summarize_memory(self, agent_id):
        return self.ams.summarize(agent_id)

    def clear_memory(self, agent_id):
        return self.ams.clear(agent_id)

    def register(self, registry):
        registry["memory"] = self

    def shutdown(self):
        pass