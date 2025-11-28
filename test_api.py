#!/usr/bin/env python3
"""
Test script for the LangGraph MCP FastAPI Application.
"""

import requests
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_health_check():
    """Test the health check endpoint."""
    print_section("Testing Health Check Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        
        print("✓ Health check passed")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {str(e)}")
        return False


def test_query(query: str, description: str):
    """Test a query through the workflow."""
    print_section(f"Testing: {description}")
    print(f"Question: {query}\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json={"question": query},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        result = response.json()
        
        print("✓ Query processed successfully")
        print(f"\nRoute Taken: {result.get('route_taken')}")
        print(f"MCP Tools Used: {result.get('details', {}).get('mcp_tools_used', [])}")
        print(f"LLM Used: {result.get('details', {}).get('llm_used', False)}")
        print(f"\nResponse:\n{'-'*70}")
        print(result.get('response', 'No response'))
        print('-'*70)
        
        return True
    except requests.exceptions.HTTPError as e:
        print(f"✗ Query failed with HTTP error: {e}")
        print(f"Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"✗ Query failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    print(f"""
    {'='*70}
    LangGraph MCP FastAPI Application - Test Suite
    {'='*70}
    
    This script will test various queries through the application.
    Make sure the server is running before executing this script.
    
    Start the server with: python main.py
    {'='*70}
    """)
    
    # Test health check
    if not test_health_check():
        print("\n❌ Server is not running. Please start the server first.")
        print("Run: python main.py")
        return
    
    # Test cases
    test_cases = [
        {
            "query": "What is CVE-2023-52341?",
            "description": "Single CVE Query (MCP Tool Only)"
        },
        {
            "query": "Tell me about CVE-2024-12345",
            "description": "CVE Query with General Question (MCP + LLM)"
        },
        {
            "query": "What is the weather in Ireland and also what is CVE-2023-52341?",
            "description": "Multiple Questions (Both MCP and LLM)"
        },
        {
            "query": "Explain what a CVE is",
            "description": "General Question (LLM Only)"
        },
        {
            "query": "CVE-2023-52341 and CVE-2024-12345",
            "description": "Multiple CVEs (MCP Tools)"
        }
    ]
    
    # Run tests
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        if test_query(test_case["query"], test_case["description"]):
            passed += 1
        else:
            failed += 1
        
        # Add a small delay between tests
        import time
        time.sleep(1)
    
    # Summary
    print_section("Test Summary")
    print(f"Total Tests: {passed + failed}")
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed.")


if __name__ == "__main__":
    main()
