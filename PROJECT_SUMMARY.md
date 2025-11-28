# LangGraph MCP FastAPI Application - Project Summary

## 🎯 Project Overview

A sophisticated Python FastAPI application that uses **LangGraph** to intelligently route user queries between **MCP (Model Context Protocol) tools** and **LLM generation** (using Llama model via Ollama).

## ✨ Key Features

### 1. **Intelligent Routing**
- Analyzes user queries to determine the best processing path
- Routes to MCP tools, LLM, or both based on query content
- Detects CVE IDs, database queries, and general questions

### 2. **MCP Tools**
- **CVEDetailsTool**: Fetches and formats CVE vulnerability information
- **MongoDBTool**: Queries MongoDB collections (extensible for your data)
- Automatic template rendering for structured responses

### 3. **Jinja2 Template Rendering**
- Beautiful HTML templates for CVE cards
- Automatic detection and rendering when templates exist
- Easy to extend with new templates

### 4. **LLM Integration**
- Uses **Llama model** via Ollama
- Contextual responses incorporating MCP tool data
- Natural language generation for complex queries

### 5. **Response Aggregation**
- Intelligently combines outputs from multiple sources
- Formats responses with clear sections
- Handles both structured data and natural language

## 📁 Project Structure

```
MCP_LangGraph_APP/
├── 📄 main.py                      # Application entry point
├── 📄 api.py                       # FastAPI routes and endpoints
├── 📄 config.py                    # Configuration management
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env                         # Environment variables
├── 📄 .env.example                 # Example environment config
├── 📄 .gitignore                   # Git ignore rules
│
├── 📖 README.md                    # Project documentation
├── 📖 ARCHITECTURE.md              # Detailed workflow architecture
├── 📖 QUICKSTART.md                # Quick start guide
│
├── 🧪 test_api.py                  # API test suite
├── 🚀 setup.sh                     # Automated setup script
├── 📮 postman_collection.json      # Postman API collection
│
├── 🧠 graph/                       # LangGraph Workflow
│   ├── __init__.py
│   ├── state.py                    # State definition
│   ├── nodes.py                    # Workflow nodes (Initialize, Route, MCP, Generate, Aggregate)
│   └── workflow.py                 # Graph compilation
│
├── 🔧 tools/                       # MCP Tools
│   ├── __init__.py
│   └── mcp_tools.py                # CVE and MongoDB tools
│
├── 🛠️ utils/                       # Utilities
│   ├── __init__.py
│   ├── template_renderer.py        # Jinja2 template rendering
│   └── response_aggregator.py      # Response combination
│
└── 🎨 templates/                   # Jinja2 Templates
    └── cvedetails_template.html    # CVE card template
```

## 🔄 Workflow Architecture

### Complete Flow
```
User Query
    ↓
[Initialize Node]
    ├─ Set up initial state
    └─ Create message history
    ↓
[Route Node]
    ├─ Analyze query content
    ├─ Detect CVE patterns
    ├─ Detect database queries
    ├─ Detect general questions
    └─ Decide: MCP | LLM | BOTH
    ↓
┌─────────────┬─────────────┬─────────────┐
│             │             │             │
[MCP Tools]   [BOTH Path]  [LLM Only]
│             │             │
├─ CVE Tool   ├─ MCP Tools  └─ Generate
├─ Mongo Tool │      ↓          Response
└─ Template   └─ Generate
   Render        Response
    ↓              ↓             ↓
    └──────────────┴─────────────┘
                   ↓
         [Aggregate Node]
         ├─ Collect MCP results
         ├─ Collect LLM responses
         └─ Format combined output
                   ↓
            [Final Response]
```

### Routing Logic

| Query Type | Example | Route Decision | Tools Used |
|------------|---------|----------------|------------|
| CVE Lookup | "What is CVE-2023-52341?" | MCP Tools | CVEDetailsTool |
| General Question | "Explain what a CVE is" | LLM Only | Llama via Ollama |
| Multiple Questions | "Weather in Ireland and CVE details?" | BOTH | CVE Tool + LLM |
| Database Query | "Query MongoDB collection" | MCP Tools | MongoDBTool |

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Ollama installed and running
- (Optional) MongoDB

### Setup
```bash
# Run automated setup
chmod +x setup.sh
./setup.sh

# Or manually
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install Ollama and pull model
ollama serve
ollama pull llama3.2
```

### Run Application
```bash
python main.py
```

### Test API
```bash
# Run test suite
python test_api.py

# Or use cURL
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is CVE-2023-52341?"}'
```

## 📡 API Endpoints

### Health Check
```http
GET /health
```

### Process Query
```http
POST /query
Content-Type: application/json

{
  "query": "Your question here"
}
```

### Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 💡 Example Queries

### 1. Single CVE Query (MCP Only)
```json
{"query": "What is CVE-2023-52341?"}
```
**Response**: Rendered HTML CVE card with details

### 2. General Question (LLM Only)
```json
{"query": "Explain what a CVE is"}
```
**Response**: Natural language explanation from Llama

### 3. Multiple Questions (BOTH)
```json
{"query": "What is the weather in Ireland and also what is CVE-2023-52341?"}
```
**Response**: Combined response with weather answer and CVE details

### 4. Multiple CVEs (MCP Tools)
```json
{"query": "CVE-2023-52341 and CVE-2024-12345"}
```
**Response**: Details for both CVEs

## 🔧 Configuration

### Environment Variables (.env)
```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=mcp_database

# Ollama/LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# API
API_HOST=0.0.0.0
API_PORT=8000
```

## 🎨 Components

### Graph Nodes
1. **Initialize**: Sets up workflow state
2. **Route**: Analyzes and routes queries
3. **MCP Tools**: Executes MCP tools
4. **Generate**: LLM response generation
5. **Aggregate**: Combines all responses

### MCP Tools
1. **CVEDetailsTool**: CVE vulnerability lookup
2. **MongoDBTool**: Database queries

### Utilities
1. **TemplateRenderer**: Jinja2 template rendering
2. **ResponseAggregator**: Response combination

## 🧪 Testing

### Automated Tests
```bash
python test_api.py
```

### Postman Collection
Import `postman_collection.json` into Postman for easy API testing

### Test Cases Included
- Health check
- Single CVE queries
- General questions
- Multiple questions (both MCP + LLM)
- Multiple CVEs

## 📚 Documentation

| Document | Description |
|----------|-------------|
| README.md | Project overview and features |
| ARCHITECTURE.md | Detailed workflow architecture with diagrams |
| QUICKSTART.md | Quick start guide with examples |
| This file | Complete project summary |

## 🔌 Extending the Application

### Add New MCP Tool
1. Create tool class in `tools/mcp_tools.py`
2. Initialize in `graph/nodes.py`
3. Add routing logic in `route_node()`
4. Implement in `mcp_tools_node()`

### Add New Template
1. Create `{toolname}_template.html` in `templates/`
2. Template automatically detected and used

### Change LLM Model
Update `.env`:
```env
OLLAMA_MODEL=mistral  # or any Ollama model
```

## 🎯 Use Cases

1. **Security Analysis**: Query CVE databases for vulnerability information
2. **Data Retrieval**: Fetch structured data from MongoDB
3. **Hybrid Queries**: Combine data retrieval with AI analysis
4. **Knowledge Base**: Answer questions using both structured data and AI
5. **Template-based Responses**: Format data into beautiful cards/reports

## 🔍 Key Technologies

- **FastAPI**: Modern, fast web framework
- **LangGraph**: Workflow orchestration
- **LangChain**: LLM integration
- **Ollama**: Local LLM serving
- **Llama**: Open-source LLM
- **Jinja2**: Template rendering
- **MongoDB**: NoSQL database
- **Pydantic**: Data validation

## 📊 Performance

- Fast routing decisions (regex-based)
- Parallel tool execution when possible
- Efficient template rendering
- Local LLM inference (no API costs)

## 🛡️ Error Handling

- Graceful LLM failures
- Tool execution error handling
- Template rendering fallbacks
- Comprehensive logging

## 🌟 Highlights

✅ **Intelligent Routing**: Automatically determines the best processing path
✅ **Template Support**: Beautiful HTML rendering for structured data
✅ **Response Aggregation**: Seamlessly combines multiple data sources
✅ **Extensible Architecture**: Easy to add new tools and templates
✅ **Local LLM**: No external API dependencies
✅ **Comprehensive Documentation**: Multiple guides and examples
✅ **Testing Suite**: Automated tests included
✅ **API Documentation**: Auto-generated Swagger/ReDoc

## 🎓 Learning Resources

- Review `ARCHITECTURE.md` for workflow details
- Check `graph/nodes.py` for node implementations
- Explore `tools/mcp_tools.py` for tool examples
- See `templates/` for template examples

## 🚀 Production Considerations

For production deployment:
1. Use production ASGI server (e.g., Gunicorn with Uvicorn workers)
2. Add authentication/authorization
3. Configure proper MongoDB credentials
4. Set up monitoring and logging
5. Use environment-specific configurations
6. Add rate limiting
7. Implement caching for frequent queries

## 📝 Next Steps

1. ✅ Install dependencies
2. ✅ Configure Ollama and pull models
3. ✅ Run the application
4. ✅ Test with example queries
5. ✅ Add custom MCP tools
6. ✅ Create custom templates
7. ✅ Integrate your data sources
8. ✅ Deploy to production

## 🤝 Contributing

This project is structured for easy extension:
- Add new tools in `tools/`
- Add new templates in `templates/`
- Extend routing logic in `graph/nodes.py`
- Add new utilities in `utils/`

---

**Built with ❤️ using LangGraph, FastAPI, and Llama**
