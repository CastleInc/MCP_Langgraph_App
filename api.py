from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn

from graph.workflow import app as workflow_app
from config import settings


# Create FastAPI app
app = FastAPI(
    title="LangGraph MCP FastAPI Application",
    description="FastAPI application with LangGraph for routing between MCP tools and LLM",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    question: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is CVE-2023-52341?"
            }
        }


class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    success: bool
    question: str
    response: str
    route_taken: str
    details: Dict[str, Any] = {}


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "LangGraph MCP FastAPI",
        "version": "1.0.0"
    }


# Main query endpoint
@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a query through the LangGraph workflow.
    
    Args:
        request: Query request containing the user's question
        
    Returns:
        QueryResponse with the processed result
    """
    try:
        print(f"\n{'='*60}")
        print(f"Processing question: {request.question}")
        print(f"{'='*60}\n")
        
        # Initialize state
        initial_state = {
            "question": request.question,
            "documents": [],
            "next_step": "route",
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
            "force_generate": False,
            "messages": []
        }
        
        # Run the workflow async
        final_state = await workflow_app.ainvoke(initial_state)
        
        print(f"\n{'='*60}")
        print(f"Workflow completed")
        print(f"{'='*60}\n")
        
        # Prepare response
        response = QueryResponse(
            success=True,
            question=request.question,
            response=final_state.get("final_response", "No response generated."),
            route_taken=final_state.get("route_decision", "unknown"),
            details={
                "tools_required": final_state.get("tools_required", 0),
                "successful_tools": final_state.get("successful_tools", 0),
                "has_rag_data": final_state.get("has_rag_data", False),
                "template_used": final_state.get("template_used"),
                "tool_responses_count": len(final_state.get("tool_responses", []))
            }
        )
        
        return response
        
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "LangGraph MCP FastAPI Application",
        "version": "1.0.0",
        "endpoints": {
            "POST /query": "Process a query through the LangGraph workflow",
            "GET /health": "Health check endpoint",
            "GET /docs": "API documentation (Swagger UI)",
            "GET /redoc": "API documentation (ReDoc)"
        },
        "example_questions": [
            "What is CVE-2023-52341?",
            "What is the weather in Ireland and also what is CVE-2023-52341?",
            "Tell me about CVE-2024-12345"
        ]
    }


if __name__ == "__main__":
    print(f"""
    {'='*60}
    LangGraph MCP FastAPI Application
    {'='*60}
    
    Starting server on http://{settings.api_host}:{settings.api_port}
    
    API Documentation:
    - Swagger UI: http://{settings.api_host}:{settings.api_port}/docs
    - ReDoc: http://{settings.api_host}:{settings.api_port}/redoc
    
    Example cURL command:
    curl -X POST "http://localhost:{settings.api_port}/query" \\
      -H "Content-Type: application/json" \\
      -d '{{"question": "What is CVE-2023-52341?"}}'
    
    {'='*60}
    """)
    
    uvicorn.run(
        "api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
