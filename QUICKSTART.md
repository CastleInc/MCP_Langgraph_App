# Quick Start Guide

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Ollama** installed and running ([Download](https://ollama.ai))
3. **(Optional)** MongoDB if you want to use database features

## Setup Steps

### 1. Install Dependencies

Run the automated setup script:

```bash
chmod +x setup.sh
./setup.sh
```

Or manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Install and Configure Ollama

```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.ai

# Start Ollama server
ollama serve

# In a new terminal, pull the Llama model
ollama pull llama3.2
```

### 3. Configure Environment

The `.env` file is already created with default values:

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=mcp_database
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
API_HOST=0.0.0.0
API_PORT=8000
```

Modify if needed for your setup.

### 4. Start the Application

```bash
python main.py
```

The server will start at `http://localhost:8000`

### 5. Test the API

In a new terminal:

```bash
python test_api.py
```

Or use cURL:

```bash
# Simple CVE query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is CVE-2023-52341?"}'

# Multiple questions
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather in Ireland and also what is CVE-2023-52341?"}'
```

## API Endpoints

### Health Check
```bash
GET http://localhost:8000/health
```

### Process Query
```bash
POST http://localhost:8000/query
Content-Type: application/json

{
  "query": "Your question here"
}
```

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Example Queries

### 1. Single CVE Lookup (MCP Tool Only)
```json
{
  "query": "What is CVE-2023-52341?"
}
```
**Flow**: Initialize → Route → MCP Tools → Aggregate → END

### 2. General Question (LLM Only)
```json
{
  "query": "Explain what a CVE is"
}
```
**Flow**: Initialize → Route → Generate → Aggregate → END

### 3. Multiple Questions (Both MCP + LLM)
```json
{
  "query": "What is the weather in Ireland and also what is CVE-2023-52341?"
}
```
**Flow**: Initialize → Route → MCP Tools → Generate → Aggregate → END

### 4. Multiple CVEs
```json
{
  "query": "Tell me about CVE-2023-52341 and CVE-2024-12345"
}
```

## Project Structure

```
MCP_LangGraph_APP/
├── main.py                 # Application entry point
├── api.py                  # FastAPI application
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── README.md              # Project documentation
├── ARCHITECTURE.md        # Workflow architecture
├── QUICKSTART.md          # This file
├── setup.sh               # Automated setup script
├── test_api.py            # Test suite
├── graph/                 # LangGraph workflow
│   ├── __init__.py
│   ├── state.py          # State definition
│   ├── nodes.py          # Workflow nodes
│   └── workflow.py       # Workflow graph
├── tools/                 # MCP Tools
│   ├── __init__.py
│   └── mcp_tools.py      # CVE and MongoDB tools
├── utils/                 # Utilities
│   ├── __init__.py
│   ├── template_renderer.py    # Jinja2 renderer
│   └── response_aggregator.py  # Response combiner
└── templates/            # Jinja2 templates
    └── cvedetails_template.html
```

## Workflow Overview

```
User Query
    ↓
Initialize (setup state)
    ↓
Route (analyze query, decide path)
    ↓
┌───────────┬───────────┐
│           │           │
MCP Tools   Both    Generate (LLM)
│           │           │
└───────────┴───────────┘
    ↓
Aggregate (combine responses)
    ↓
Final Response
```

## Customization

### Add New MCP Tool

1. Create tool class in `tools/mcp_tools.py`:
```python
class MyNewTool:
    def __init__(self):
        self.name = "MyNewTool"
    
    def execute(self, params):
        # Tool logic here
        return {"success": True, "data": {...}}
```

2. Initialize in `graph/nodes.py`
3. Add routing logic in `route_node()`
4. Call tool in `mcp_tools_node()`

### Add New Template

1. Create template file in `templates/`:
   - Name format: `{toolname}_template.html`
   - Example: `mynewool_template.html`

2. Template will be automatically detected and used

### Change LLM Model

Update `.env`:
```env
OLLAMA_MODEL=mistral  # or any other Ollama model
```

Then pull the model:
```bash
ollama pull mistral
```

## Troubleshooting

### Ollama Connection Error
- Ensure Ollama is running: `ollama serve`
- Check URL in `.env`: `OLLAMA_BASE_URL=http://localhost:11434`

### Model Not Found
- Pull the model: `ollama pull llama3.2`
- List available models: `ollama list`

### Port Already in Use
- Change port in `.env`: `API_PORT=8001`
- Or kill existing process: `lsof -ti:8000 | xargs kill`

### Import Errors
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

## MongoDB Setup (Optional)

If you want to use MongoDB features:

```bash
# Install MongoDB locally or use Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Update .env with connection string
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=mcp_database
```

## Next Steps

1. ✅ Run the application
2. ✅ Test with example queries
3. ✅ Review the architecture documentation
4. ✅ Add custom MCP tools
5. ✅ Create custom templates
6. ✅ Integrate with your data sources

## Support

For issues or questions:
- Check `ARCHITECTURE.md` for workflow details
- Review `README.md` for project overview
- Examine test cases in `test_api.py`

## License

This project is provided as-is for educational and development purposes.
