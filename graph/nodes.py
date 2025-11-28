from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from typing import Dict, Any
import re
import logging

from graph.state import GraphState, ToolResponse
from services.tool_executor import SimpleMCPAgent, GENERATE, ROUTE, END
from utils.response_aggregator import ResponseAggregator
from config import settings

logger = logging.getLogger(__name__)

# Initialize MCP Agent with server configuration
SERVER_CONFIG = {
    "tools": ["CVEDetails", "MongoDBTool"],
    "servers": {}
}

mcp_agent = SimpleMCPAgent(SERVER_CONFIG)


def initialize_node(state: GraphState) -> GraphState:
    """Initialize the workflow."""
    question = state.get("question", "")
    logger.info(f"[INITIALIZE] Processing question: {question}")
    
    return {
        **state,
        "question": question,
        "documents": [],
        "next_step": ROUTE,
        "has_rag_data": False,
        "tools_required": 0,
        "successful_tools": 0,
        "metadata_filter": {},
        "generate_prompt_key": "default",
        "last_stage_data": None,
        "templated_output": None,
        "template_used": None,
        "tool_responses": [],
        "tool_input": {},
        "tool_name": None,
        "template_name": None,
        "templated_outputs": [],
        "route_decision": "",
        "final_response": "",
        "force_generate": False
    }


def route_node(state: GraphState) -> GraphState:
    """Route the query to appropriate handlers."""
    question = state.get("question", "").lower()
    print(f"[ROUTE] Analyzing question: {question}")
    logger.info(f"[ROUTE] Analyzing question for routing...")
    
    cve_pattern = r'cve[-\s]?\d{4}[-\s]?\d{4,7}'
    cve_matches = re.findall(cve_pattern, question, re.IGNORECASE)
    has_cve = bool(cve_matches)
    
    has_data_query = any(keyword in question for keyword in 
                         ['data', 'database', 'mongo', 'collection', 'query'])
    
    has_general_query = any(keyword in question for keyword in 
                           ['what', 'how', 'why', 'explain', 'tell', 'describe'])
    
    needs_mcp = has_cve or has_data_query
    
    # Check if it's a multi-part question (tool + general)
    has_both = needs_mcp and has_general_query and any(sep in question for sep in [' and ', ' also ', ','])
    
    if needs_mcp:
        route_decision = "mcp_tools"
    else:
        route_decision = "generate"
    
    tool_input = {}
    tool_name = None
    template_name = None
    force_generate = has_both  # Force LLM generation even with template
    
    if has_cve and cve_matches:
        cve_id = cve_matches[0].upper().replace(' ', '-')
        if not cve_id.startswith('CVE-'):
            cve_id = 'CVE-' + cve_id[3:]
        
        tool_input = {"cve_id": cve_id}
        tool_name = "CVEDetails"
        template_name = "cvedetails_template.html"
        state["tools_required"] = 1
    
    print(f"[ROUTE] Decision: {route_decision}, needs_mcp: {needs_mcp}, force_generate: {force_generate}")
    logger.info(f"[ROUTE] Decision: {route_decision}")
    
    return {
        **state,
        "route_decision": route_decision,
        "tool_input": tool_input,
        "tool_name": tool_name,
        "template_name": template_name,
        "force_generate": force_generate,
        "next_step": "mcp_tools" if needs_mcp else GENERATE
    }


async def mcp_tools_node(state: GraphState) -> GraphState:
    """Execute MCP tools."""
    logger.info("[MCP_TOOLS] Executing MCP tools...")
    
    session_name = "langgraph_session"
    
    try:
        if state.get("tool_name"):
            state = await mcp_agent.execute_tools_simple(state, session_name)
        else:
            state = await mcp_agent.execute_tools(state, session_name)
        
        logger.info(f"[MCP_TOOLS] Completed")
        
    except Exception as e:
        logger.error(f"[MCP_TOOLS] Error: {e}")
        state["next_step"] = GENERATE
    
    return state


def generate_node(state: GraphState) -> GraphState:
    """Generate response using LLM."""
    logger.info("[GENERATE] Generating LLM response...")
    
    try:
        llm = ChatOllama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=0.7
        )
        
        context = ""
        if state.get("tool_responses"):
            context = "\n\nContext from tools:\n"
            for tool_response in state["tool_responses"]:
                if tool_response.get("success") and tool_response.get("data"):
                    context += f"\nTool: {tool_response.get('tool', 'Unknown')}\n"
                    context += f"Data: {tool_response.get('data')}\n"
        
        system_msg = SystemMessage(content="""You are a helpful AI assistant. 
        Answer user questions clearly and concisely.""")
        
        user_msg = HumanMessage(content=state.get("question", "") + context)
        
        response = llm.invoke([system_msg, user_msg])
        
        logger.info("[GENERATE] LLM response generated")
        
        state["final_response"] = response.content
        state["next_step"] = "aggregate"
        
    except Exception as e:
        logger.error(f"[GENERATE] Error: {str(e)}")
        state["final_response"] = "Sorry, I couldn't generate a response."
        state["next_step"] = "aggregate"
    
    return state


def aggregate_node(state: GraphState) -> GraphState:
    """Aggregate responses."""
    logger.info("[AGGREGATE] Aggregating responses...")
    
    aggregator = ResponseAggregator()
    
    if state.get("templated_outputs"):
        for idx, templated_output in enumerate(state["templated_outputs"]):
            aggregator.add_response(f"Tool_{idx+1}_Template", templated_output)
    elif state.get("tool_responses"):
        for tool_response in state["tool_responses"]:
            tool_name = tool_response.get("tool", "Unknown")
            aggregator.add_response(tool_name, tool_response)
    
    if state.get("final_response"):
        aggregator.add_response("llm", {"content": state["final_response"]})
    
    final_result = aggregator.aggregate()
    
    logger.info("[AGGREGATE] Complete")
    
    return {
        **state,
        "final_response": final_result["combined_output"],
        "next_step": END
    }


def route_after_routing(state: GraphState) -> str:
    """Determine next step after routing."""
    next_step = state.get("next_step", ROUTE)
    
    if next_step == "mcp_tools":
        return "mcp_tools"
    elif next_step == GENERATE:
        return "generate"
    else:
        return "aggregate"
