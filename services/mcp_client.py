import json
import logging
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class MultiserverMCPClient:
    """
    MCP Client for managing multiple server connections and sessions.
    Handles tool initialization and execution across different MCP servers.
    """
    
    def __init__(self, server_config: Dict[str, Any]):
        """
        Initialize the MCP client with server configuration.
        
        Args:
            server_config: Configuration for MCP servers and tools
        """
        logger.info("Initializing MultiserverMCPClient")
        self.server_config = server_config
        self.sessions = {}
        self.initialized = False
        
    @asynccontextmanager
    async def session(self, session_name: str):
        """
        Create or retrieve a session context for tool execution.
        
        Args:
            session_name: Unique identifier for the session
            
        Yields:
            Session object for tool execution
        """
        try:
            if session_name not in self.sessions:
                logger.info(f"Creating new session: {session_name}")
                self.sessions[session_name] = MCPSession(session_name, self.server_config)
            
            session = self.sessions[session_name]
            yield session
            
        except Exception as e:
            logger.error(f"Error in session {session_name}: {e}")
            raise
    
    async def close_session(self, session_name: str):
        """Close a specific session."""
        if session_name in self.sessions:
            logger.info(f"Closing session: {session_name}")
            del self.sessions[session_name]
    
    async def close_all_sessions(self):
        """Close all active sessions."""
        logger.info("Closing all MCP sessions")
        self.sessions.clear()


class MCPSession:
    """
    Represents an MCP session for tool execution.
    """
    
    def __init__(self, session_name: str, server_config: Dict[str, Any]):
        """
        Initialize MCP session.
        
        Args:
            session_name: Session identifier
            server_config: Server configuration
        """
        self.session_name = session_name
        self.server_config = server_config
        self.tools_cache = {}
        logger.info(f"MCP Session created: {session_name}")
    
    async def get_tool(self, tool_name: str):
        """
        Retrieve a tool by name.
        
        Args:
            tool_name: Name of the tool to retrieve
            
        Returns:
            Tool instance
        """
        if tool_name in self.tools_cache:
            return self.tools_cache[tool_name]
        
        # Load tool from configuration
        tool = await self._load_tool(tool_name)
        self.tools_cache[tool_name] = tool
        return tool
    
    async def _load_tool(self, tool_name: str):
        """Load tool from configuration."""
        # This is a simplified implementation
        # In production, this would connect to actual MCP servers
        from tools.mcp_tools import get_tool_by_name
        return get_tool_by_name(tool_name)


async def load_mcp_tool(tool_name: str, session: MCPSession):
    """
    Load an MCP tool from a session.
    
    Args:
        tool_name: Name of the tool to load
        session: MCP session
        
    Returns:
        Loaded tool instance
    """
    logger.info(f"Loading MCP tool: {tool_name}")
    return await session.get_tool(tool_name)
