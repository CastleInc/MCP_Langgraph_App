from typing import Dict, Any, List
from datetime import datetime


class ResponseAggregator:
    """Utility for aggregating responses from multiple sources (MCP tools and LLM)."""
    
    def __init__(self):
        """Initialize the response aggregator."""
        self.responses = []
    
    def add_response(self, source: str, response: Any):
        """
        Add a response from a source.
        
        Args:
            source: Source identifier (tool name or 'llm')
            response: Response data
        """
        self.responses.append({
            "source": source,
            "response": response,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def aggregate(self) -> Dict[str, Any]:
        """
        Aggregate all collected responses into a unified response.
        
        Returns:
            Dictionary containing aggregated response
        """
        if not self.responses:
            return {
                "aggregated": True,
                "count": 0,
                "responses": [],
                "combined_output": "No responses to aggregate."
            }
        
        # Separate MCP tool responses and LLM responses
        tool_responses = []
        llm_responses = []
        
        for item in self.responses:
            if item["source"].lower() == "llm":
                llm_responses.append(item)
            else:
                tool_responses.append(item)
        
        # Build combined output
        combined_parts = []
        
        # Add tool responses
        if tool_responses:
            combined_parts.append("=== Data from Tools ===\n")
            for item in tool_responses:
                source = item["source"]
                response = item["response"]
                
                if isinstance(response, dict):
                    if "rendered_template" in response:
                        # Template was rendered
                        combined_parts.append(f"\n{source} (Rendered):\n{response['rendered_template']}\n")
                    elif "data" in response:
                        # Raw data
                        combined_parts.append(f"\n{source} Data:\n{self._format_data(response['data'])}\n")
                    else:
                        combined_parts.append(f"\n{source}:\n{str(response)}\n")
                else:
                    combined_parts.append(f"\n{source}:\n{str(response)}\n")
        
        # Add LLM responses
        if llm_responses:
            combined_parts.append("\n=== AI Generated Response ===\n")
            for item in llm_responses:
                response = item["response"]
                if isinstance(response, dict) and "content" in response:
                    combined_parts.append(f"{response['content']}\n")
                else:
                    combined_parts.append(f"{str(response)}\n")
        
        combined_output = "\n".join(combined_parts)
        
        return {
            "aggregated": True,
            "count": len(self.responses),
            "tool_count": len(tool_responses),
            "llm_count": len(llm_responses),
            "responses": self.responses,
            "combined_output": combined_output.strip(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _format_data(self, data: Any) -> str:
        """
        Format data for display.
        
        Args:
            data: Data to format
            
        Returns:
            Formatted string
        """
        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    lines.append(f"{key}: {str(value)}")
                else:
                    lines.append(f"{key}: {value}")
            return "\n".join(lines)
        elif isinstance(data, list):
            if data and isinstance(data[0], dict):
                return "\n".join([self._format_data(item) for item in data])
            return "\n".join([str(item) for item in data])
        else:
            return str(data)
    
    def clear(self):
        """Clear all collected responses."""
        self.responses = []
    
    def has_responses(self) -> bool:
        """
        Check if there are any responses collected.
        
        Returns:
            True if responses exist, False otherwise
        """
        return len(self.responses) > 0
