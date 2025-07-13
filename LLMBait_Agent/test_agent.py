#!/usr/bin/env python3
"""
Simple test script to verify the agent setup works correctly.
"""

import asyncio
import sys
import os

# Add the current directory to the path so we can import agent
sys.path.insert(0, os.path.dirname(__file__))

from agent import root_agent, call_agent_async

async def test_agent():
    """Test the agent with a simple query."""
    print("Testing LLMBait agent...")
    
    # Simple test query
    test_query = "Test the system with a simple query"
    
    try:
        # This would normally require a runner, user_id, and session_id
        # For now, just test that the agent can be imported and initialized
        print(f"Agent name: {root_agent.name}")
        print(f"Agent description: {root_agent.description}")
        print(f"Number of tools: {len(root_agent.tools)}")
        
        print("✅ Agent setup appears to be working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing agent: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_agent()) 