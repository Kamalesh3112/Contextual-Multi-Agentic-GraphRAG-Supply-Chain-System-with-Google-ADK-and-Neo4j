"""
============================================================================
llm_provider.py

Custom LLM Provider Adapter for Google ADK Workflow Engine.

Responsibilities
----------------
• Abstract model provider backends (Google vs OpenRouter).
• Handle direct OpenRouter payload formatting for Nemotron/Qwen.
• Manage automatic failover mechanics to alternative fallback models.
• Implement standard execution signature interfaces compatible with ADK.
"""

import os
import requests
import logging
import base64
from typing import Any, List, Optional, Dict
from google.adk.agents import Agent

logger = logging.getLogger("ADK.Orchestration.LLMProvider")


class OpenRouterClient:
    """
    Handles API translation layer requests to OpenRouter endpoints.
    Fits seamlessly within custom ADK workflow hooks.
    """
    from google.adk.agents import Agent
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai"
        self.primary_model = os.getenv("LLM_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free")
        self.fallback_model = os.getenv("FALLBACK_MODEL", "qwen/qwen3-7-plus")
        
        if not self.api_key:
            logger.error("Missing OPENROUTER_API_KEY in environment variables.")

    def run_inference(self, prompt: str, system_instruction: str = "", files: Optional[List[Any]] = None) -> str:
        """
        Executes text generation request with built-in primary-to-fallback routing logic.
        """
        try:
            logger.info(f"Dispatching inference task to primary model backend: {self.primary_model}")
            return self._call_api(self.primary_model, prompt, system_instruction, files)
        except Exception as e:
            logger.warning(f"Primary model '{self.primary_model}' failed due to error: {e}. Executing fallback sequence...")
            try:
                logger.info(f"Dispatching inference task to fallback model backend: {self.fallback_model}")
                return self._call_api(self.fallback_model, prompt, system_instruction, files)
            except Exception as critical_error:
                logger.critical(f"Both primary and fallback models failed. Execution terminated: {critical_error}")
                raise RuntimeError("All configured inference endpoint configurations are completely exhausted.")

    def _call_api(self, model_target: str, prompt: str, system_instruction: str, files: Optional[List[Any]] = None) -> str:
        """
        Constructs standard HTTP OpenRouter payloads. Handles file descriptors if present.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com",
            "X-Title": "Google ADK Platform Integration",
            "Content-Type": "application/json",
        }

        def _build_messages() -> List[Dict[str, Any]]:
            msgs: List[Dict[str, Any]] = []
            if system_instruction:
                msgs.append({"role": "system", "content": system_instruction})

            if files:
                content = [{"type": "text", "text": prompt}]
                for file_asset in files:
                    base64_str = None
                    mime_type = getattr(file_asset, "mime_type", "image/jpeg")

                    if hasattr(file_asset, "base64_data"):
                        base64_str = file_asset.base64_data
                    elif hasattr(file_asset, "read"):
                        try:
                            base64_str = base64.b64encode(file_asset.read()).decode("utf-8")
                        except Exception as parse_err:
                            logger.error(f"Failed parsing raw binary stream metadata buffer: {parse_err}")

                    if base64_str:
                        content.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{base64_str}"},
                        })

                msgs.append({"role": "user", "content": content})
            else:
                msgs.append({"role": "user", "content": prompt})

            return msgs

        data = {"model": model_target, "messages": _build_messages(), "temperature": 0.2}

        response = requests.post(self.base_url, headers=headers, json=data, timeout=45)
        response.raise_for_status()

        result_json = response.json()

        choices = result_json.get("choices") or []
        if not choices:
            raise KeyError("Malformed payload returned from inference server endpoint mapping layer.")

        first = choices[0]
        if isinstance(first, dict) and "message" in first and "content" in first["message"]:
            return first["message"]["content"]
        if "text" in first:
            return first["text"]
        raise KeyError("Malformed payload returned from inference server endpoint mapping layer.")


class OpenRouterADKAdapter(Agent):
    """
    Subclasses the native Google ADK Agent structure directly.
    Ensures absolute compliance with strict registry type checkers (isinstance checks).
    """
    def __init__(self, name: str, instruction: str, runner: OpenRouterClient):
        super().__init__(name=name, model="openrouter-custom-pipeline", instruction=instruction)
        self.runner = runner

    def run(self, user_prompt: str, files: Optional[List[Any]] = None, **kwargs: Any) -> Any:
        """
        Overrides the standard execution loop interface.
        Returns a schema container mocking native ADK Response configurations.
        """
        class ADKResponseMock:
            def __init__(self, output_text: str):
                self.text = output_text

        raw_text = self.runner.run_inference(user_prompt, self.instruction, files)
        return ADKResponseMock(raw_text)


class ADKModelFactory:
    """
    Instantiates either native Gemini models or wraps third-party integrations 
    into standard execution facades for cross-agent reuse.
    """
    @staticmethod
    def create_model_runner(agent_name: str, instruction: str) -> Agent:
        """
        Guarantees that the returned object is safely typed as a google.adk.agents.Agent.
        """
        provider = os.getenv("LLM_PROVIDER", "google").lower()
        
        if provider == "openrouter":
            logger.info(f"Wrapping custom OpenRouter adapter around target node: '{agent_name}'")
            client = OpenRouterClient()
            #type assertion checks
            return OpenRouterADKAdapter(name=agent_name, instruction=instruction, runner=client)
            
        else:
            logger.info(f"Instantiating standard native Google ADK Client for: '{agent_name}'")
            return Agent(name=agent_name, model="gemini-2.5-flash", instruction=instruction)