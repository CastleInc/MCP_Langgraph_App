import json
import logging
from typing import Any, Dict, List

from graph.state import GraphState, ToolResponse
from services.mcp_client import MultiserverMCPClient, load_mcp_tool
from utils.template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)

# Action constants
GENERATE = "generate"
ROUTE = "route"
END = "end"


def empty_tool_response() -> ToolResponse:
    """
    Return an empty tool response.
    Tool execution should always return a response.
    """
    return ToolResponse(
        data=None,
        success=False,
        metadata={},
        message="tool_executor failed",
        next_action=None,
        has_context=False,
        info="No tools available"
    )


class SimpleMCPAgent:
    """
    A class to manage tools and execute them, with proper initialization.
    Implements singleton pattern for tool management.
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SimpleMCPAgent, cls).__new__(cls)
        return cls._instance

    def __init__(self, server_config: Dict[str, Any], template_dir: str = None):
        if not self._initialized:
            logger.info("Initializing the SimpleMCPAgent with server configuration.")
            self.server_config = server_config
            self.mcp_client = MultiserverMCPClient(server_config)
            self.tools = self.get_tools_for_agent(server_config)
            self.template_renderer = TemplateRenderer(
                templates_dir=template_dir or "templates"
            )
            self._initialized = True
            logger.info("SimpleMCPAgent initialized successfully.")

    async def initialize_tools(self, session_name: str):
        """
        Initialize tools by creating a session and loading tools.
        
        Args:
            session_name: Unique session identifier
        """
        logger.info(f"Initializing tools for session: {session_name}")
        try:
            async with self.mcp_client.session(session_name) as session:
                initialized_tools = []
                for tool_name in self.tools:
                    tool = await load_mcp_tool(tool_name, session)
                    initialized_tools.append(tool)
                self.tools = initialized_tools
            logger.info(f"Successfully initialized {len(self.tools)} tools")
        except Exception as e:
            logger.error(f"Failed to initialize tools: {e}")
            self.tools = []

    async def execute_tools(self, state: GraphState, session_name: str) -> GraphState:
        """
        Execute tools using the provided state and return the updated state.
        
        Args:
            state: Current graph state
            session_name: Session identifier
            
        Returns:
            Updated graph state
        """
        raw_data = []
        
        # Check if all required tools have been executed
        if state.get("tools_required") == state.get("successful_tools"):
            logger.info("All required tools already executed")
            return state
        
        last_stage_data = empty_tool_response()
        
        try:
            async with self.mcp_client.session(session_name) as session:
                # Execute each tool
                for tool in self.tools:
                    logger.info(f"Executing tool: {tool.name}")
                    tool_node = await load_mcp_tool(tool.name, session)
                    tool_result = await tool_node.ainvoke(state.get("tool_input", {}))
                    raw_data.append(tool_result)

                # Initialize state lists if not present
                state["tool_responses"] = []
                state.setdefault("templated_outputs", [])

                # Process each tool result
                for tool_result in raw_data:
                    tool_response = ToolResponse(
                        data=tool_result.get("data"),
                        success=tool_result.get("success", False),
                        metadata={"tool": tool_result.get("tool"), "timestamp": tool_result.get("timestamp")},
                        has_context=tool_result.get("has_context", False),
                        message=tool_result.get("error", "") if not tool_result.get("success") else ""
                    )
                    state["tool_responses"].append(tool_response.to_dict())

                    if tool_response.success and tool_response.data:
                        # Check for template
                        template_name = state.get("template_name")
                        if template_name:
                            try:
                                rendered_output = self.template_renderer.render_template(
                                    template_name, 
                                    tool_response.data
                                )
                                state["templated_outputs"].append(rendered_output)
                                state["template_used"] = template_name
                                logger.info(f"Successfully rendered template {template_name}")
                            except Exception as e:
                                logger.error(f"Error rendering template {template_name}: {e}")
                                state["templated_outputs"].append(f"Error rendering template: {e}")
                        else:
                            # No template, use raw JSON
                            state["templated_outputs"].append(json.dumps(tool_response.data))

                    # Check if tool specified a next action
                    if tool_response.next_action:
                        last_stage_data = tool_response
                        break  # Stop if a next action is determined

        except Exception as e:
            logger.error(f"Error during tool execution (Fallback to vector retrieval): {e}")

        # Determine next step based on results
        if not last_stage_data.next_action and state.get("templated_outputs"):
            next_step = GENERATE
        else:
            next_step = ROUTE
        
        # Update state
        state["next_step"] = next_step
        state["last_stage_data"] = last_stage_data
        state["successful_tools"] = state.get("successful_tools", 0) + len(
            state.get("tool_responses", [])
        )
        state["has_rag_data"] = any(
            tr.get("has_context", False) for tr in state.get("tool_responses", [])
        )

        return state

    async def execute_tools_simple(self, state: GraphState, session_name: str) -> GraphState:
        """
        Simplified tool execution for a single tool without complex branching.
        
        Args:
            state: Current graph state
            session_name: Session identifier
            
        Returns:
            Updated graph state
        """
        tool_input = state.get("tool_input")
        if not tool_input:
            logger.warning("No tool input provided in state.")
            return state

        next_step = ROUTE
        last_stage_data = empty_tool_response()
        templated_outputs = []

        try:
            async with self.mcp_client.session(session_name) as session:
                tool_name = state.get("tool_name")
                if not tool_name:
                    logger.error("No tool name specified for simple execution.")
                    return state

                logger.info(f"Executing single tool: {tool_name}")
                tool_node = await load_mcp_tool(tool_name, session)
                tool_result = await tool_node.ainvoke(tool_input)
                tool_response = ToolResponse(
                    data=tool_result.get("data"),
                    success=tool_result.get("success", False),
                    metadata={"tool": tool_result.get("tool"), "timestamp": tool_result.get("timestamp")},
                    has_context=tool_result.get("has_context", False),
                    message=tool_result.get("error", "") if not tool_result.get("success") else ""
                )

                if tool_response.success and tool_response.data:
                    template_name = state.get("template_name")
                    if template_name:
                        try:
                            rendered_output = self.template_renderer.render_template(
                                template_name, 
                                tool_response.data
                            )
                            templated_outputs.append(rendered_output)
                            state["template_used"] = template_name
                            logger.info(f"Successfully rendered template {template_name}")
                        except Exception as e:
                            logger.error(f"Error rendering template {template_name}: {e}")
                            templated_outputs.append(f"Error rendering template: {e}")
                    else:
                        templated_outputs.append(json.dumps(tool_response.data))

                # Determine next action
                if tool_response.next_action:
                    last_stage_data = tool_response
                    next_step = tool_response.next_action
                elif state.get("force_generate", False):
                    # Multi-part question - need both template and LLM
                    next_step = GENERATE
                elif templated_outputs:
                    # If template was rendered and no force_generate, we're done
                    next_step = "aggregate"
                elif tool_response.success and tool_response.data:
                    # Tool succeeded but no template - send to LLM to process the data
                    next_step = GENERATE
                else:
                    # Tool failed - route back
                    next_step = ROUTE

                # Update state
                state["tool_responses"] = [tool_response.to_dict()]
                state["templated_outputs"] = templated_outputs
                state["last_stage_data"] = last_stage_data
                state["next_step"] = next_step
                state["successful_tools"] = state.get("successful_tools", 0) + 1
                state["has_rag_data"] = tool_response.has_context

        except Exception as e:
            logger.error(f"Error during simple tool execution: {e}")
            state["tool_responses"] = [empty_tool_response().to_dict()]
            state["next_step"] = ROUTE

        return state

    def get_tools_for_agent(self, server_config: Dict[str, Any]) -> List[str]:
        """
        Retrieve the list of tool names from configuration.
        
        Args:
            server_config: Server configuration dictionary
            
        Returns:
            List of tool names
        """
        return server_config.get("tools", [])
