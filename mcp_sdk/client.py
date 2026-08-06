"""
Client + Retry + Exceptions
 Handles
   - Async httpx.AsyncClient
   - Connection pooling: http and stdio
   - Retry with exponential backoff
   - Timeouts
   - Pydantic request/response models
   - Logging
   - Health checks
   - Tool discovery
   - Tool metadata
   - Authentication hooks
   - Context manager (__aenter__ / __aexit__)
   - Graceful shutdown
   - Structured exceptions
   - Configuration integration
   - Docstrings and type hints
"""
import asyncio
import random
import logging
from fastmcp import Client, MCPError

client = Client("http://localhost:8000/mcp")

# async def custom_tool(name: str):
   # async with client

logger = logging.getLogger(__name__)
logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

class MCPWrapperClient(Client): #Composition

   def wrapper_client_exception(self, exception: Exception | type[Exception], message: str = "") -> None:
        """Raise a provided exception with an optional message.

        Args:
            exception: Exception class or instance to raise.
            message: Optional message for the exception.
        """
        if isinstance(exception, type) and issubclass(exception, Exception):
            raise exception(message)

        if isinstance(exception, Exception):
            if message:
                try:
                    exception.args = (message,)
                except Exception:
                    pass
            raise exception

        if message:
            raise RuntimeError(message)

        raise RuntimeError("An unexpected error occurred")

   def __init__(self, client, base_url: str = "http://localhost:8000/mcp", max_retries = 5, base_delay = 1, max_delay = 30):
       self.client = client(base_url)
       self.logger = logger
       self.logger.info("Initialized the MCP Wrapper Client with baseurl: %s", base_url)
       self._connected = False
       self._session = None
       self.max_retries = max_retries
       self.base_delay = base_delay
       self.max_delay = max_delay

   async def __aenter__(self):
        """
        Async opens a new MCP session
        """
        logger.info("Creating a new MCP context session")
        await self.client.__aenter__()
        self._connected = True
        return self

   async def __aexit__(self, exc_type, exc, tb):
       """
       Exit async context: Terminating the MCP session
       """
       logger.info("Terminating the current MCP session...")
       await self.client.__aexit__(exc_type, exc, tb)
       self._connected = False

   async def connect_stdio(self):
       logger.info("Connecting over standard input/output (stdio) for local agent processes")
       try:
           await self.client.connect_stdio()
           logger.info("Connected through stdio for agents internal i/o")
       except MCPError as e:
           logger.error("Failed stdio connection: %s", e)
           raise

   async def connect_http(self):
       logger.info("Connecting over live streamable HTTP request")
       attempt = 0
       while attempt < self.max_entries:
           try:
                await self.client.connect_http()
                self.logger.info("Connected through connect_http() endpoint")
                return
           except MCPError as e:
                attempt += 1
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                jitter = random.uniform(9, 0.5)
                self.logger.warning(
                    attempt, self.max_entries, e, delay + jitter
                )
                await asyncio.sleep(delay, jitter)
           raise RuntimeError("Failed to connect to the MCP Server after certain retries")

   async def invoke_tool(self, tool_name: str, **kwargs):
       logger.info("Invoking the valid registered tool on the MCP Server")
       try:
           await self.client.invoke_tool(tool_name, **kwargs)
           logger.info("Invoked the registered %s tools successfully", tool_name)
       except MCPError as e:
           logger.error("Tool invocation failed: %s", e)
           raise

   async def read_resource(self, resource_id: str):
       logger.info("Reading a resource provided from the MCP Resource")
       try:
           resource = await self.client.read_resource(resource_id)
           logger.info("Resource %s read successfully", resource_id)
           return resource
       except MCPError as e:
           logger.error("Resource read failed; %s", e)
           raise

   async def handle_notification(self):
        logger.info("Async generator: For handling server notifications")
        try:
            async for notification in self.client.notifications():
                logger.info("Received notifications: %s", notification)

        except MCPError as e:
            logging.error("Notification failed to be streamed: %s", e)
            raise

async def main():
   async with MCPWrapperClient() as client:
        await client.connect_http()
        #await client.connect_stdio()

        notification_task = await client.handle_notification()

        try:
            result = await client.invoke_tool("echo", message = "MCP client notification is active and in sync with Server overal mutual protocol")
            print("Tool result:", result)

            resource = await client.read_resources("resource:example")
            print("Resource:", resource)

            await asyncio.sleep(30)

        finally:
            notification_task.cancel()
            try:
                await notification_task
            except asyncio.cancelledError:
                logger.info("Notification task cancelled cleanly")
 
if __name__ == "__main__":
    asyncio.run(main())