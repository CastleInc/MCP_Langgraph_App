"""
LangGraph MCP FastAPI Application

Main entry point for the application.
"""

import uvicorn
from config import settings

if __name__ == "__main__":
    print(f"""
    {'='*60}
    LangGraph MCP FastAPI Application
    {'='*60}
    
    Starting server on http://{settings.api_host}:{settings.api_port}
    
    Configuration:
    - Ollama Model: {settings.ollama_model}
    - Ollama URL: {settings.ollama_base_url}
    - MongoDB URI: {settings.mongodb_uri}
    - MongoDB Database: {settings.mongodb_database}
    
    API Documentation:
    - Swagger UI: http://localhost:{settings.api_port}/docs
    - ReDoc: http://localhost:{settings.api_port}/redoc
    
    Example cURL command:
    curl -X POST "http://localhost:{settings.api_port}/query" \\
      -H "Content-Type: application/json" \\
      -d '{{"query": "What is CVE-2023-52341?"}}'
    
    {'='*60}
    """)
    
    uvicorn.run(
        "api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level="info"
    )
