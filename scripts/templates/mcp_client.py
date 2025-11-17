"""
MCP Client Wrapper

Provides unified interface to MCP servers configured in .mcp.json.
Communicates via JSON-RPC over subprocess stdin/stdout.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class MCPClient:
    """
    Wrapper around Claude Code's MCP infrastructure.

    Spawns MCP server processes and handles JSON-RPC communication.
    Each server is configured in .mcp.json with command and args.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize MCP client.

        Args:
            config_path: Path to .mcp.json. If None, searches for it in parent directories.
        """
        self.config_path = config_path or self._find_mcp_config()
        self.config = self._load_config()
        self.processes: Dict[str, subprocess.Popen] = {}

    def _find_mcp_config(self) -> str:
        """Search for .mcp.json in current and parent directories."""
        current = Path.cwd()
        while current != current.parent:
            config = current / ".mcp.json"
            if config.exists():
                return str(config)
            current = current.parent
        raise FileNotFoundError("Could not find .mcp.json in current or parent directories")

    def _load_config(self) -> Dict:
        """Load MCP server configuration from .mcp.json."""
        with open(self.config_path) as f:
            return json.load(f)

    def _start_server(self, server_name: str) -> subprocess.Popen:
        """
        Start an MCP server process.

        Args:
            server_name: Name of server from .mcp.json (e.g., "fda-mcp", "ct-gov-mcp")

        Returns:
            Subprocess handle for the MCP server
        """
        if server_name not in self.config.get("mcpServers", {}):
            raise ValueError(f"Server '{server_name}' not found in .mcp.json")

        server_config = self.config["mcpServers"][server_name]
        command = server_config["command"]
        args = server_config.get("args", [])
        env = server_config.get("env", {})

        # Merge environment variables
        full_env = {**os.environ.copy(), **env}

        # Start subprocess with stdin/stdout pipes for JSON-RPC
        process = subprocess.Popen(
            [command] + args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=full_env,
            text=True,
            bufsize=1
        )

        return process

    def call_tool(
        self,
        server_name: str,
        tool_name: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call an MCP tool.

        Args:
            server_name: Name of MCP server (e.g., "fda-mcp")
            tool_name: Tool to call (e.g., "mcp__fda-mcp__fda_info")
            params: Tool parameters as dictionary

        Returns:
            Tool result as dictionary

        Example:
            >>> client = MCPClient()
            >>> result = client.call_tool(
            ...     "fda-mcp",
            ...     "mcp__fda-mcp__fda_info",
            ...     {
            ...         "method": "lookup_drug",
            ...         "search_term": "aspirin",
            ...         "search_type": "general",
            ...         "count": "openfda.brand_name.exact",
            ...         "limit": 10
            ...     }
            ... )
        """
        # Start server if not already running
        if server_name not in self.processes:
            self.processes[server_name] = self._start_server(server_name)

        process = self.processes[server_name]

        # Create JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            }
        }

        # Send request
        process.stdin.write(json.dumps(request) + "\n")
        process.stdin.flush()

        # Read response
        response_line = process.stdout.readline()
        response = json.loads(response_line)

        # Handle errors
        if "error" in response:
            raise RuntimeError(f"MCP tool error: {response['error']}")

        return response.get("result", {})

    def close(self):
        """Terminate all MCP server processes."""
        for process in self.processes.values():
            process.terminate()
            process.wait()
        self.processes.clear()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup processes."""
        self.close()


# Convenience function for one-off queries
def query_mcp(server: str, tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a single MCP query with automatic cleanup.

    Args:
        server: MCP server name
        tool: Tool name
        params: Tool parameters

    Returns:
        Tool result

    Example:
        >>> result = query_mcp(
        ...     "fda-mcp",
        ...     "mcp__fda-mcp__fda_info",
        ...     {"method": "lookup_drug", "search_term": "aspirin", ...}
        ... )
    """
    with MCPClient() as client:
        return client.call_tool(server, tool, params)
