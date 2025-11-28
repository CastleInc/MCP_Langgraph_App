from langgraph.graph import StateGraph, END
from graph.state import GraphState
from graph.nodes import (
    initialize_node,
    route_node,
    mcp_tools_node,
    generate_node,
    aggregate_node,
    route_after_routing
)
from services.tool_executor import GENERATE


def create_workflow() -> StateGraph:
    """
    Create the LangGraph workflow.
    
    Flow:
    - Initialize -> Route
    - Route -> MCP Tools (if needed)
    - Route -> Generate (if needed)
    - MCP Tools -> Check template -> Aggregate or END
    - Generate -> Aggregate or END
    - Aggregate -> END
    
    Returns:
        Compiled StateGraph workflow
    """
    
    # Create the graph
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("initialize", initialize_node)
    workflow.add_node("route", route_node)
    workflow.add_node("mcp_tools", mcp_tools_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("aggregate", aggregate_node)
    
    # Set entry point
    workflow.set_entry_point("initialize")
    
    # Add edges
    workflow.add_edge("initialize", "route")
    
    # Conditional routing after route node
    workflow.add_conditional_edges(
        "route",
        route_after_routing,
        {
            "mcp_tools": "mcp_tools",
            "generate": "generate",
            "both": "mcp_tools"  # If both, start with MCP then generate
        }
    )
    
    # After MCP tools
    def after_mcp(state: GraphState) -> str:
        """Decide what to do after MCP tools."""
        next_step = state.get("next_step", "aggregate")
        print(f"[WORKFLOW] after_mcp - next_step from state: {next_step}")
        
        # If template was rendered, go to aggregate (end workflow)
        # If no template, go to generate (LLM processes tool data)
        if next_step == GENERATE:
            print("[WORKFLOW] No template found - routing to generate")
            return "generate"
        else:
            print("[WORKFLOW] Template rendered - routing to aggregate")
            return "aggregate"
    
    workflow.add_conditional_edges(
        "mcp_tools",
        after_mcp,
        {
            "generate": "generate",
            "aggregate": "aggregate"
        }
    )
    
    # After generate, always aggregate
    workflow.add_edge("generate", "aggregate")
    
    # After aggregate, end
    workflow.add_edge("aggregate", END)
    
    # Compile the graph
    return workflow.compile()


# Create the compiled workflow
app = create_workflow()
