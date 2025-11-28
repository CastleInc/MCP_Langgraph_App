# LangGraph Workflow Architecture

## Overview
This document describes the LangGraph workflow architecture for the MCP FastAPI Application.

## Workflow Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Query Input                              │
└────────────────────────────┬──────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │   INITIALIZE   │
                    │   (Node)       │
                    │  - Set state   │
                    │  - Create msgs │
                    └───────┬────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │     ROUTE      │
                    │    (Node)      │
                    │ - Analyze query│
                    │ - Detect CVEs  │
                    │ - Detect type  │
                    └───────┬────────┘
                            │
                ┌───────────┼───────────┐
                │           │           │
                ▼           ▼           ▼
         ┌──────────┐  ┌──────────┐  ┌──────────┐
         │MCP_TOOLS │  │   BOTH   │  │ GENERATE │
         │  (Path)  │  │  (Path)  │  │  (Path)  │
         └────┬─────┘  └────┬─────┘  └────┬─────┘
              │             │               │
              │             │               │
              ▼             ▼               │
     ┌────────────────────────┐            │
     │     MCP_TOOLS_NODE     │            │
     │  - Execute CVE Tool    │            │
     │  - Execute MongoDB Tool│            │
     │  - Check for Templates │            │
     └───────┬────────────────┘            │
             │                             │
             ▼                             │
     ┌────────────────┐                   │
     │  Has Template? │                   │
     └───────┬────────┘                   │
             │                             │
      ┌──────┼──────┐                     │
      │             │                     │
  Yes │         No  │                     │
      │             │                     │
      ▼             ▼                     │
┌──────────┐  ┌──────────┐               │
│ RENDER   │  │  Pass    │               │
│TEMPLATE  │  │  Data    │               │
└────┬─────┘  └────┬─────┘               │
     │             │                      │
     │     ┌───────┘                      │
     │     │                              │
     ▼     ▼                              │
  ┌─────────────────┐                    │
  │  Needs LLM?     │                    │
  └────┬────────────┘                    │
       │                                 │
 ┌─────┼─────┐                          │
 │           │                          │
Yes          No                         │
 │           │                          │
 │           ▼                          │
 │      ┌──────────┐                   │
 │      │ END      │                   │
 │      │(Template)│                   │
 │      └──────────┘                   │
 │                                     │
 └──────┬──────────────────────────────┘
        │
        ▼
┌────────────────┐
│ GENERATE_NODE  │
│ - Init Llama   │
│ - Add context  │
│ - Generate LLM │
└───────┬────────┘
        │
        ▼
┌────────────────┐
│  AGGREGATE     │
│   (Node)       │
│ - Collect MCP  │
│ - Collect LLM  │
│ - Combine All  │
└───────┬────────┘
        │
        ▼
┌────────────────┐
│      END       │
│  Final Output  │
└────────────────┘
```

## Node Descriptions

### 1. INITIALIZE Node
**Purpose**: Set up the initial state for the workflow
- Receives user query
- Initializes empty state variables
- Creates initial message

### 2. ROUTE Node
**Purpose**: Analyze query and decide routing path
- Detects CVE IDs using regex pattern
- Identifies data/database queries
- Detects general questions
- Sets routing decision: `mcp_tools`, `generate`, or `both`

**Routing Logic**:
- CVE patterns → `mcp_tools` or `both`
- Database keywords → `mcp_tools` or `both`
- General questions → `generate` or `both`
- Multiple questions (with "and", "also") → `both`

### 3. MCP_TOOLS Node
**Purpose**: Execute MCP tools (CVE Details, MongoDB)
- Extracts CVE IDs from query
- Calls CVEDetailsTool for each CVE
- Queries MongoDB if data patterns detected
- Checks for Jinja2 templates
- Renders template if exists

**Template Rendering**:
- Looks for `{toolname}_template.html` in templates/
- Renders with tool data if found
- Sets `template_rendered` flag

### 4. GENERATE Node
**Purpose**: Generate response using Llama LLM
- Initializes ChatOllama with configured model
- Adds context from MCP tools if available
- Generates natural language response
- Handles errors gracefully

### 5. AGGREGATE Node
**Purpose**: Combine all responses into final output
- Uses ResponseAggregator utility
- Collects MCP tool results
- Collects LLM responses
- Formats combined output with sections
- Returns unified response

## Conditional Edges

### After ROUTE
```python
if route_decision == "mcp_tools":
    → MCP_TOOLS_NODE
elif route_decision == "generate":
    → GENERATE_NODE
elif route_decision == "both":
    → MCP_TOOLS_NODE (then to GENERATE)
```

### After MCP_TOOLS
```python
if template_rendered and not needs_llm:
    → END (template is complete response)
elif needs_llm:
    → GENERATE_NODE
else:
    → AGGREGATE_NODE
```

### After GENERATE
```python
Always → AGGREGATE_NODE
```

### After AGGREGATE
```python
Always → END
```

## State Structure

```python
GraphState = {
    "query": str,              # User's input query
    "route_decision": str,     # Routing decision
    "needs_mcp": bool,         # Whether MCP tools needed
    "needs_llm": bool,         # Whether LLM needed
    "mcp_results": dict,       # Results from MCP tools
    "llm_response": dict,      # Response from LLM
    "final_response": str,     # Final aggregated response
    "messages": List[Message]  # Message history
}
```

## Example Flows

### Example 1: Simple CVE Query
```
Query: "What is CVE-2023-52341?"

Flow:
INITIALIZE → ROUTE (decides: mcp_tools)
         → MCP_TOOLS (fetches CVE, renders template)
         → AGGREGATE (formats response)
         → END

Result: Rendered HTML CVE card
```

### Example 2: General Question
```
Query: "Explain what a CVE is"

Flow:
INITIALIZE → ROUTE (decides: generate)
         → GENERATE (LLM explains CVE)
         → AGGREGATE (formats response)
         → END

Result: LLM-generated explanation
```

### Example 3: Multiple Questions
```
Query: "What is the weather in Ireland and also what is CVE-2023-52341?"

Flow:
INITIALIZE → ROUTE (decides: both)
         → MCP_TOOLS (fetches CVE data)
         → GENERATE (answers weather + uses CVE context)
         → AGGREGATE (combines both responses)
         → END

Result: Combined response with both answers
```

## Components Used

### MCP Tools
1. **CVEDetailsTool**: Fetches CVE vulnerability details
2. **MongoDBTool**: Queries MongoDB collections

### Utilities
1. **TemplateRenderer**: Renders Jinja2 templates
2. **ResponseAggregator**: Combines multiple responses

### LLM
- **ChatOllama**: Interface to Llama model via Ollama

## Configuration

All settings in `config.py` loaded from `.env`:
- `OLLAMA_BASE_URL`: Ollama server URL
- `OLLAMA_MODEL`: Model name (e.g., llama3.2)
- `MONGODB_URI`: MongoDB connection string
- `MONGODB_DATABASE`: Database name
