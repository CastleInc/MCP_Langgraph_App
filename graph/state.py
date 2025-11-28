from typing import List, Dict, Any, Optional
from langgraph.graph import MessagesState


class ToolResponse:
    """Response from MCP tool execution."""
    
    def __init__(self, data=None, success=False, metadata=None, message="", 
                 next_action=None, has_context=False, info=""):
        self.data = data
        self.success = success
        self.metadata = metadata or {}
        self.message = message
        self.next_action = next_action
        self.has_context = has_context
        self.info = info
    
    def to_dict(self):
        return {
            "data": self.data,
            "success": self.success,
            "metadata": self.metadata,
            "message": self.message,
            "next_action": self.next_action,
            "has_context": self.has_context,
            "info": self.info
        }


class GraphState(MessagesState):
    """
    Represents the state of the LangGraph workflow.
    Extends MessagesState for message handling.
    """
    question: str
    documents: List[str]
    next_step: str
    has_rag_data: bool
    tools_required: int
    successful_tools: int
    metadata_filter: Dict[str, Any]
    generate_prompt_key: str
    last_stage_data: Optional[ToolResponse]
    templated_output: Optional[str]
    template_used: Optional[str]
    tool_responses: List[Dict[str, Any]]
    tool_input: Dict[str, Any]
    tool_name: Optional[str]
    template_name: Optional[str]
    templated_outputs: List[str]
    route_decision: str
    final_response: str
    force_generate: bool  # Flag for multi-part questions requiring both tools and LLM
