from typing import Dict, Any, List, Optional
from pymongo import MongoClient
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)


class MongoDBTool:
    """MCP Tool for interacting with MongoDB."""
    
    def __init__(self, connection_uri: str, database_name: str):
        """
        Initialize MongoDB connection.
        
        Args:
            connection_uri: MongoDB connection string
            database_name: Name of the database to use
        """
        self.client = MongoClient(connection_uri)
        self.db = self.client[database_name]
        self.name = "MongoDBTool"
    
    def query_data(self, collection: str, query: Dict[str, Any] = None, limit: int = 10) -> Dict[str, Any]:
        """
        Query data from MongoDB collection.
        
        Args:
            collection: Collection name
            query: MongoDB query filter
            limit: Maximum number of documents to return
            
        Returns:
            Dictionary containing the query results
        """
        try:
            if query is None:
                query = {}
            
            col = self.db[collection]
            results = list(col.find(query).limit(limit))
            
            # Convert ObjectId to string for JSON serialization
            for doc in results:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            return {
                "success": True,
                "tool": self.name,
                "collection": collection,
                "count": len(results),
                "data": results,
                "has_context": len(results) > 0,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "tool": self.name,
                "error": str(e),
                "has_context": False,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def ainvoke(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Async invoke method for tool execution.
        
        Args:
            tool_input: Dictionary containing query parameters
            
        Returns:
            Tool response dictionary
        """
        collection = tool_input.get("collection", "default")
        query = tool_input.get("query", {})
        limit = tool_input.get("limit", 10)
        return self.query_data(collection, query, limit)
    
    def close(self):
        """Close the MongoDB connection."""
        self.client.close()


class CVEDetailsTool:
    """MCP Tool for fetching CVE details."""
    
    def __init__(self):
        """Initialize CVE Details tool."""
        self.name = "CVEDetails"
        # Mock CVE database for testing
        self.mock_cve_data = {
            "CVE-2023-52341": {
                "cve_number": "CVE-2023-52341",
                "cve_title": "XYZ Component Remote Code Execution",
                "description": "A critical vulnerability in the XYZ component allows remote code execution through malicious input validation.",
                "severity": "CRITICAL",
                "cvss_score": 9.8,
                "classifications_location": "Remote / Network Access",
                "classifications_attack_type": "Remote Code Execution",
                "classifications_impact": "Complete System Compromise",
                "classifications_exploit": "Exploit Exists",
                "solution": "Apply the vendor-provided security patch immediately.",
                "affected_products": "Product XYZ version 1.0 - 2.5, Product ABC version 3.0 - 3.2",
                "source_last_modified_date": "2024-01-10T00:00:00.000+00:00",
                "cisa_key": "Yes",
                "exploit_code_maturity": "High",
                "remediation_level": "Official Fix",
                "report_confidence": "Confirmed"
            },
            "CVE-2024-12345": {
                "cve_number": "CVE-2024-12345",
                "cve_title": "Authentication Module SQL Injection",
                "description": "SQL injection vulnerability in authentication module allows unauthorized access.",
                "severity": "HIGH",
                "cvss_score": 8.1,
                "classifications_location": "Remote / Network Access",
                "classifications_attack_type": "SQL Injection",
                "classifications_impact": "Information Disclosure",
                "classifications_exploit": "Proof of Concept",
                "solution": "Upgrade to WebApp Framework version 2.4 or later.",
                "affected_products": "WebApp Framework version 2.0 - 2.3",
                "source_last_modified_date": "2024-04-05T00:00:00.000+00:00",
                "cisa_key": "No",
                "exploit_code_maturity": "Proof of Concept",
                "remediation_level": "Official Fix",
                "report_confidence": "Confirmed"
            },
            "CVE-2020-000001": {
                "cve_number": "CVE-2020-000001",
                "cve_title": "Red Hat Operating System Directory Traversal",
                "description": "Red Hat Operating System contains a directory traversal vulnerability that allows an authenticated attacker to execute arbitrary code.",
                "severity": "CRITICAL",
                "cvss_score": 9.9,
                "classifications_location": "Remote / Network Access",
                "classifications_attack_type": "Memory Corruption",
                "classifications_impact": "Information Disclosure",
                "classifications_exploit": "Exploit Exists",
                "solution": "Apply the vendor-provided hotfix immediately.",
                "affected_products": "Red Hat Operating System versions 5.2 through 8.8",
                "source_last_modified_date": "2023-02-11T00:00:00.000+00:00",
                "cisa_key": "No",
                "exploit_code_maturity": "High",
                "remediation_level": "Official Fix",
                "report_confidence": "Confirmed",
                "input_vector": "CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:L/A:N/E:P/RL:U/RC:U"
            }
        }
    
    def get_cve_details(self, cve_id: str) -> Dict[str, Any]:
        """
        Fetch CVE details by ID.
        
        Args:
            cve_id: CVE identifier (e.g., CVE-2023-52341)
            
        Returns:
            Dictionary containing CVE details
        """
        try:
            # Normalize CVE ID
            cve_id = cve_id.upper().strip()
            
            if cve_id in self.mock_cve_data:
                cve_data = self.mock_cve_data[cve_id]
                return {
                    "success": True,
                    "tool": self.name,
                    "data": cve_data,
                    "has_context": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "tool": self.name,
                    "error": f"CVE {cve_id} not found",
                    "has_context": False,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {
                "success": False,
                "tool": self.name,
                "error": str(e),
                "has_context": False,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def search_cves(self, keyword: str, limit: int = 5) -> Dict[str, Any]:
        """
        Search CVEs by keyword.
        
        Args:
            keyword: Search keyword
            limit: Maximum number of results
            
        Returns:
            Dictionary containing search results
        """
        try:
            keyword_lower = keyword.lower()
            results = []
            
            for cve_id, cve_data in self.mock_cve_data.items():
                if (keyword_lower in cve_data['description'].lower() or
                    keyword_lower in cve_id.lower()):
                    results.append(cve_data)
                    if len(results) >= limit:
                        break
            
            return {
                "success": True,
                "tool": self.name,
                "count": len(results),
                "data": results,
                "has_context": len(results) > 0,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "tool": self.name,
                "error": str(e),
                "has_context": False,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def ainvoke(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Async invoke method for tool execution.
        
        Args:
            tool_input: Dictionary containing CVE ID or search parameters
            
        Returns:
            Tool response dictionary
        """
        cve_id = tool_input.get("cve_id")
        keyword = tool_input.get("keyword")
        
        if cve_id:
            return self.get_cve_details(cve_id)
        elif keyword:
            return self.search_cves(keyword, tool_input.get("limit", 5))
        else:
            return {
                "success": False,
                "tool": self.name,
                "error": "No cve_id or keyword provided",
                "has_context": False,
                "timestamp": datetime.utcnow().isoformat()
            }


def get_tool_by_name(tool_name: str):
    """
    Get a tool instance by name.
    
    Args:
        tool_name: Name of the tool to retrieve
        
    Returns:
        Tool instance
    """
    logger.info(f"Getting tool by name: {tool_name}")
    
    if tool_name == "CVEDetails":
        return CVEDetailsTool()
    elif tool_name == "MongoDBTool":
        from config import settings
        return MongoDBTool(settings.mongodb_uri, settings.mongodb_database)
    else:
        logger.error(f"Unknown tool: {tool_name}")
        raise ValueError(f"Unknown tool: {tool_name}")
