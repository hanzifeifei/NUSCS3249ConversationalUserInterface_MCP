"""The chatbot's MCP client: one connection to the clinic's MCP server.

The chatbot (the HOST) holds one ClinicClient. The client starts the server as
a subprocess, then:
    discover()        asks the server which tools it offers     (tools/list)
    read_policies()   reads the clinic://policies resource      (resources/read)
    call()            runs one tool and returns its result      (tools/call)

The client does not know the tool names in advance. It asks.
"""
import logging
import sys
from contextlib import AsyncExitStack

from mcp import Client, StdioServerParameters

log = logging.getLogger("mcp_client")

# How to start the server: `python -m backend.clinic_server`, talking over stdio.
CLINIC_SERVER = StdioServerParameters(command=sys.executable, args=["-m", "backend.clinic_server"])
POLICIES_URI = "clinic://policies"
MAX_RESULT_CHARS = 1000


class ClinicClient:
    def __init__(self, server=CLINIC_SERVER):
        self.server = server          # StdioServerParameters, or an MCPServer object in tests
        self.tools = []               # [{"name", "description", "input_schema"}], filled by discover()
        self.policies = ""            # text of clinic://policies, filled by read_policies()
        self.connected = False
        self._client = None
        self._stack = None

    async def connect(self):
        """Start the server and do the MCP handshake. (Given.)"""
        self._stack = AsyncExitStack()
        self._client = await self._stack.enter_async_context(Client(self.server))
        self.connected = True

    async def close(self):
        if self._stack:
            await self._stack.aclose()
        self.connected, self.tools, self.policies = False, [], ""

    # ======================================================================
    # Activity 2: discover, read, call
    # ======================================================================
    async def discover(self):
        """2.1  Ask the server for its tools: result = await self._client.list_tools()
        For each t in result.tools keep {"name": t.name, "description": t.description,
        "input_schema": t.input_schema}. Save the list in self.tools and return it."""
        self.tools = []                                  # TODO
        return self.tools

    async def read_policies(self):
        """2.2  Read the resource: result = await self._client.read_resource(POLICIES_URI)
        The text is result.contents[0].text. Save it in self.policies and return it."""
        self.policies = ""                               # TODO
        return self.policies

    async def call(self, name, arguments):
        """2.3  Run one tool: result = await self._client.call_tool(name, arguments)
        The text is result.content[0].text; result.is_error is True if the tool failed.
        Return (ok, text), with ok = not result.is_error."""
        return False, "NOT_IMPLEMENTED: ClinicClient.call"   # TODO
