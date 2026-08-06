#Model Registry for ADK Agents
"""
Purpose:
  The registry is the directory of every agent. Central administrative gateway for multi-agent applications using the Google ADK.
  Maintains system status metrics, handles dynamic instantiation, and exposes discovery vectors.

Responsibilities:
  - Register agents
  - Discover agents
  - Spawn workers
  - Agent metadata
  - Health status
  - Capability lookup
"""
# agents/registry.py
"""
Model Registry for ADK Agents (registry.py).

Purpose:
  Central administrative gateway for multi-agent applications using the Google ADK.
  Maintains system status metrics, handles dynamic instantiation, and exposes discovery vectors.
"""

import logging
import threading
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union
from google.adk.agents import Agent  # Core Google ADK structural type abstraction

# Setup production logging
logger = logging.getLogger("ADKRegistry")

class RegistryAgentStatus(Enum):
    """Real-time operation profiles compliant with monitoring platforms."""
    ONLINE = "ONLINE"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    MAINTENANCE = "MAINTENANCE"


class ADKAgentRegistry:
    """Thread-safe ledger and instantiation factory framework for Google ADK Systems."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        
        # Internal registries tracking static metrics, live objects, and lifecycle blueprints
        self._blueprints: Dict[str, Dict[str, Any]] = {}
        self._instances: Dict[str, Agent] = {}
        self._workers: Dict[str, Set[str]] = {}  # Tracks running process IDs against agent targets

    def register_agent(
        self,
        name: str,
        capabilities: Set[str],
        factory_or_instance: Union[Agent, Callable[..., Agent]],
        is_singleton: bool = True,
        version: str = "1.0.0",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Registers an entity into the centralized catalog.
        Accepts either an active Agent object (Singleton) or a constructor function (Factory).
        """
        with self._lock:
            blueprint = {
                "name": name,
                "capabilities": set(capabilities),
                "is_singleton": is_singleton,
                "factory": factory_or_instance if not is_singleton else None,
                "version": version,
                "status": RegistryAgentStatus.ONLINE,
                "metadata": metadata or {},
                "health_errors": []
            }
            
            self._blueprints[name] = blueprint
            self._workers[name] = set()

            # Cache reference immediately if treated as a structural Singleton
            if is_singleton:
                if not isinstance(factory_or_instance, Agent):
                    raise TypeError(f"Singleton target for '{name}' must be an instance of google.adk.agents.Agent")
                self._instances[name] = factory_or_instance
            
            logger.info(f"Successfully registered ADK component '{name}' [Pattern: {'Singleton' if is_singleton else 'Factory'}, Capabilities: {capabilities}]")

    def unregister_agent(self, name: str) -> bool:
        """Removes an agent definition and purges existing active reference targets."""
        with self._lock:
            if name not in self._blueprints:
                logger.warning(f"Unregister failed. Component '{name}' does not exist.")
                return False
                
            del self._blueprints[name]
            self._instances.pop(name, None)
            self._workers.pop(name, None)
            logger.info(f"Purged and unregistered agent component allocation: '{name}'")
            return True

    def get_or_create_instance(self, name: str, *args: Any, **kwargs: Any) -> Optional[Agent]:
        """
        Retrieves or initializes a runtime Agent instance.
        Resolves singletons instantly or invokes factories dynamically with passed parameters.
        """
        with self._lock:
            blueprint = self._blueprints.get(name)
            if not blueprint:
                logger.error(f"Cannot resolve instance. '{name}' is not logged in blueprints.")
                return None

            if blueprint["status"] == RegistryAgentStatus.UNHEALTHY:
                logger.warning(f"Returning instantiation reference for unhealthy node context: '{name}'")

            if blueprint["is_singleton"]:
                return self._instances.get(name)
            
            # Dynamic creation path via factory configuration logic
            try:
                factory_fn = blueprint["factory"]
                if factory_fn:
                    new_agent = factory_fn(*args, **kwargs)
                    if not isinstance(new_agent, Agent):
                        raise TypeError("Factory generation output must adhere to google.adk.agents.Agent specification.")
                    return new_agent
            except Exception as e:
                logger.error(f"Factory failure while executing code generation initialization for '{name}': {e}")
                return None

    def discover_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Returns metadata description map matches directly using structural identity indexes."""
        with self._lock:
            blueprint = self._blueprints.get(name)
            if not blueprint:
                return None
            return self._extract_metadata_summary(blueprint)

    def discover_by_capability(self, required_capability: str) -> List[Dict[str, Any]]:
        """Scans active records for matching capabilities or exposed task tools."""
        with self._lock:
            matched_set = []
            for bp in self._blueprints.values():
                if required_capability in bp["capabilities"] and bp["status"] != RegistryAgentStatus.UNHEALTHY:
                    matched_set.append(self._extract_metadata_summary(bp))
            return matched_set

    def list_agents(self) -> List[Dict[str, Any]]:
        """Compiles a ledger of all tracked entries across the application ecosystem."""
        with self._lock:
            return [self._extract_metadata_summary(bp) for bp in self._blueprints.values()]

    def perform_health_check(self, name: str) -> Dict[str, Any]:
        """
        Validates the configuration properties and instance health of an agent.
        """
        with self._lock:
            blueprint = self._blueprints.get(name)
            if not blueprint:
                return {"status": "UNKNOWN", "error": "Agent registry allocation target missing."}

            errors = []
            
            # 1. Structural evaluation check
            if blueprint["is_singleton"]:
                inst = self._instances.get(name)
                if not inst or not isinstance(inst, Agent):
                    errors.append("Cached structural Singleton instance is corrupted or empty.")
            else:
                if blueprint["factory"] is None or not callable(blueprint["factory"]):
                    errors.append("Dynamic execution blueprint is missing a valid callable factory constructor.")

            # Update health profiles across active dictionaries
            if errors:
                blueprint["status"] = RegistryAgentStatus.UNHEALTHY
                blueprint["health_errors"] = errors
            else:
                blueprint["status"] = RegistryAgentStatus.ONLINE
                blueprint["health_errors"] = []

            return {
                "name": name,
                "status": blueprint["status"].value,
                "healthy": blueprint["status"] in (RegistryAgentStatus.ONLINE, RegistryAgentStatus.DEGRADED),
                "tracked_issues": errors
            }

    def register_worker_trajectory(self, agent_name: str, worker_id: str) -> bool:
        """Dynamically indexes a running processing task context against an agent name."""
        with self._lock:
            if agent_name in self._workers:
                self._workers[agent_name].add(worker_id)
                logger.debug(f"Worker tracking hook '{worker_id}' attached to operational stack '{agent_name}'.")
                return True
            return False

    def decommission_worker_trajectory(self, agent_name: str, worker_id: str) -> None:
        """Removes a finished task thread or task context signature safely from the metrics tracker."""
        with self._lock:
            if agent_name in self._workers:
                self._workers[agent_name].discard(worker_id)
                logger.debug(f"Worker tracking hook '{worker_id}' released from system cluster allocation stack.")

    def discover_active_workers(self, agent_name: str) -> List[str]:
        """Discovers active agent resource footprints or runtime task vectors assigned to a given component."""
        with self._lock:
            return list(self._workers.get(agent_name, set()))

    def _extract_metadata_summary(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """Internal helper to safely map schema parameters into isolated payload packets."""
        return {
            "name": blueprint["name"],
            "version": blueprint["version"],
            "capabilities": list(blueprint["capabilities"]),
            "status": blueprint["status"].value,
            "is_singleton": blueprint["is_singleton"],
            "active_worker_count": len(self._workers.get(blueprint["name"], set())),
            "custom_metadata": blueprint["metadata"],
            "issues": blueprint["health_errors"]
        }


# Instantiated static singleton to guide internal execution modules safely
global_registry = ADKAgentRegistry()     