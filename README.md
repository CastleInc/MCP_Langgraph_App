# LangGraph MCP FastAPI Application

A production-ready FastAPI application using LangGraph for intelligent routing between MCP tools and LLM generation. Built with enterprise architecture patterns including proper state management, MCP client integration, and async tool execution.

## ✨ Features

- **Enterprise State Management**: GraphState extends MessagesState with comprehensive state tracking
- **MCP Client Integration**: MultiserverMCPClient with async session management
- **Tool Executor**: SimpleMCPAgent with singleton pattern for tool orchestration
- **LangGraph Workflow**: Initialize → Route → (MCP Tools | Generate) → Aggregate
- **MCP Tools**: CVEDetails and MongoDB tools with async execution
- **Jinja2 Templates**: Automatic template rendering for structured responses
- **Llama Integration**: Uses Ollama with Llama model for LLM generation
- **Response Aggregator**: Intelligently combines outputs from multiple sources

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start Ollama (if not running):
```bash
ollama serve
ollama pull llama3.2
```

4. Run the application:
```bash
python main.py
```

## API Endpoints

- `POST /query` - Process a query through the LangGraph workflow
- `GET /health` - Health check endpoint

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide with setup instructions
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed workflow architecture and flow diagrams  
- **[ENTERPRISE_ARCHITECTURE.md](ENTERPRISE_ARCHITECTURE.md)** - Enterprise patterns and refactoring details
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete project overview

## Example Usage

```bash
# Single CVE query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is CVE-2023-52341?"}'
```

```bash
# Multiple questions (MCP + LLM)
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the weather in Ireland and also what is CVE-2023-52341?"}'
```
