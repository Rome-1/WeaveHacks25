import datetime
from zoneinfo import ZoneInfo
import weave
from google.adk.agents import Agent
import asyncio
import os
import json
from typing import Optional, List, Dict, Any
import requests
from bs4 import BeautifulSoup

weave.init('content-owner-search-optimizer')  # 🐝 New W&B project



def scrape_url_metadata_simple(url: str) -> Dict[str, Any]:
    """
    Scrape metadata from a URL using requests and BeautifulSoup.
    """
    import requests
    from bs4 import BeautifulSoup
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ""
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ""
        
        return {
            'status': 'success',
            'url': url,
            'title': title_text,
            'metadescription': description
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'url': url,
            'error_message': str(e)
        }

def search_google_simple(
    query: str,
    objective: str,
    injectedResults: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Simple mock search function that simulates Google search results.
    """
    # Create mock search results
    mock_results = [
        {
            "title": "Premium Fedora Collection - Handcrafted Excellence",
            "url": "https://example.com/premium-fedoras",
            "description": "Discover our exclusive collection of handcrafted fedoras made from the finest materials.",
            "rank": 1,
            "extractorRelevanceScore": 9.2,
            "resultId": "result1",
            "isCustomResult": False
        },
        {
            "title": "Luxury Fedora Guide - How to Choose the Perfect Hat",
            "url": "https://example.com/fedora-guide",
            "description": "Comprehensive guide to selecting the perfect fedora. Learn about materials, fit, and style.",
            "rank": 2,
            "extractorRelevanceScore": 8.7,
            "resultId": "result2",
            "isCustomResult": False
        },
        {
            "title": "Best Fedora Hats 2024 - Top Rated Quality Hats",
            "url": "https://example.com/best-fedoras",
            "description": "Find the best fedora hats of 2024. Expert reviews and recommendations for quality hats.",
            "rank": 3,
            "extractorRelevanceScore": 8.1,
            "resultId": "result3",
            "isCustomResult": False
        }
    ]
    
    # Insert injected results if provided
    if injectedResults:
        for injected in injectedResults:
            insert_rank = injected.get('insertRank', 1)
            # Insert at the specified position (1-based index)
            insert_index = min(insert_rank - 1, len(mock_results))
            injected_result = {
                "title": injected.get('title', ''),
                "url": injected.get('url', ''),
                "description": injected.get('description', ''),
                "rank": insert_rank,
                "extractorRelevanceScore": 9.5,  # High score for injected results
                "resultId": f"injected_{insert_rank}",
                "isCustomResult": True
            }
            mock_results.insert(insert_index, injected_result)
    
    # Simulate agent selection (for now, select the first result)
    selected_result_index = 0
    
    return {
        "query": query,
        "totalResults": len(mock_results),
        "searchTime": 1500,  # Mock search time
        "selectedResultIndex": selected_result_index,
        "results": mock_results
    }

"""
 * Scrapes the given URL and returns its title and meta description.
 *
 * This tool is for content owners to trial and select titles/metadescriptions for their pages, simulating how a browser agent would choose among search results.
 *
 * Parameters:
 *   url (string): The URL to scrape.
 *
 * Returns:
 *   An object with:
 *     - status ("success" or "error")
 *     - url (string): The URL that was scraped
 *     - title (string): The page title (if found)
 *     - metadescription (string): The meta description (if found)
 *     - error_message (string): Error message if status is "error"
 *
 * Example usage:
 *   const result = await scrape_url_metadata("https://example.com");
 """
@weave.op()
async def monitored_scrape_url_metadata(url: str):
    """Async function tool for scraping URL metadata"""
    return scrape_url_metadata_simple(url)


"""
 * Search Google for a given query and optionally inject custom search results at specific positions.
 *
 * This function performs a Google search for the provided query and returns structured search results, including relevance scores and agent selection. Optionally, you can inject custom results into the search results list at specified positions, making them indistinguishable from organic results to the agent.
 *
 * Parameters:
 *   query (string): The search query to use on Google (e.g., "find the finest fedora").
 *   objective (string): The high-level goal or context for the search (e.g., "Find information about high-quality fedora hats").
 *   injected_title (string, optional): The title of the injected result.
 *   injected_url (string, optional): The URL for the injected result.
 *   injected_description (string, optional): The description/snippet for the injected result.
 *   injected_rank (number, optional): The 1-based position to insert the result (1 = first result).
 *
 * Returns:
 *   A Promise resolving to an object containing:
 *     - query (string): The search query that was used
 *     - totalResults (number): Total number of results found
 *     - searchTime (number): Time taken to perform search in milliseconds
 *     - selectedResultIndex (number | undefined): Index of result the agent would select, if any
 *     - results (Array): Array of result objects, each containing:
 *       - title (string): Result title
 *       - url (string): Result URL
 *       - description (string): Result description/snippet
 *       - rank (number): Position in results (1-based)
 *       - extractorRelevanceScore (number): Relevance score from 0-10
 *       - resultId (string): Unique identifier
 *       - isCustomResult (boolean): Whether this was an injected result
 *
 * Example usage:
 *   const results = await monitored_search_google(
 *     query: "find the finest fedora",
 *     objective: "Find information about high-quality fedora hats",
 *     injected_title: "My Custom Result",
 *     injected_url: "https://example.com",
 *     injected_description: "A special result.",
 *     injected_rank: 2
 *   );
 """
@weave.op()
async def monitored_search_google(query: str, objective: str, injected_title: str = "", injected_url: str = "", injected_description: str = "", injected_rank: int = 1):
    """
    Search Google as an agent to find the best result.
    
    Args:
        query: The search query to use
        objective: The high-level goal or context for the search
        injected_title: Title of the injected result (optional)
        injected_url: URL of the injected result (optional)
        injected_description: Description of the injected result (optional)
        injected_rank: Position to insert the result (1-based, default 1)
    """
    injected_results = None
    if injected_title and injected_url:
        injected_results = [{
            "title": injected_title,
            "url": injected_url,
            "description": injected_description,
            "insertRank": injected_rank
        }]
    
    return search_google_simple(
        query=query,
        objective=objective,
        injectedResults=injected_results
    )

root_agent = Agent(
    name="LLMBait",
    model="gemini-1.5-pro",
    description=(
        "Helps content owners trial and select titles/metadescriptions for their pages. "
        "Simulates how a browser agent would choose among Google search results, "
        "allowing you to inject your own result and see if it would be selected."
    ),
    instruction=(
        "Prompt the user to provide either a URL (to scrape title/metadescription) or a manual entry (title, url, metadescription). "
        "Ask for the user's objective (what a potential site visitor is trying to do). "
        "Suggest a search query based on the objective, allow the user to edit, and confirm all details before running the search. "
        "Use monitored_scrape_url_metadata to fetch metadata if a URL is provided. "
        "Use monitored_search_google to simulate the search, injecting the user's result. "
        "Present the results in a clear, readable format, highlighting which result the agent would select, and showing all titles, URLs, descriptions, ranks, and relevance scores."
    ),
    tools=[monitored_scrape_url_metadata, monitored_search_google],
)

# Agent interaction function for ADK
async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")

    # Prepare the user's message in ADK format
    from google.genai import types
    content = types.Content(role='user', parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response." # Default

    # Key Concept: run_async executes the agent logic and yields Events.
    # We iterate through events to find the final answer.
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        # You can uncomment the line below to see *all* events during execution
        # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

        # Key Concept: is_final_response() marks the concluding message for the turn.
        if event.is_final_response():
            if event.content and event.content.parts:
               # Assuming text response in the first part
               final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate: # Handle potential errors/escalations
               final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            # Add more checks here if needed (e.g., specific error codes)
            break # Stop processing events once the final response is found

    print(f"<<< Agent Response: {final_response_text}")
    return final_response_text