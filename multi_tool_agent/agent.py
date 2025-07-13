import datetime
from zoneinfo import ZoneInfo
import weave
from google.adk.agents import Agent

# # Import your tool wrappers (these call your TypeScript backend via Stagehand)
# from tool_stagehand import search_google_as_an_agent_to_find_the_best_result
# from my_tools import scrape_url_metadata

weave.init('content-owner-search-optimizer')  # 🐝 New W&B project


import asyncio
import os
import json
from stagehand import Stagehand, StagehandConfig
from typing import Optional, List, Dict, Any

async def stagehand_act(url: str, action: str) -> dict:
    cfg = StagehandConfig(env="BROWSERBASE")     # reads env vars
    sh = Stagehand(cfg)
    await sh.init()

    if url:
        await sh.page.goto(url)
    result = await sh.page.act(action)           # same API as TS
    await sh.close()
    return result

async def scrape_url_metadata_stagehand(url: str) -> Dict[str, Any]:
    """
    Scrape metadata from a URL using Stagehand.
    """
    # Create a temporary script to call the TypeScript function
    script_content = f"""
import {{ scrape_url_metadata }} from '../LLMBait/scrape_url_metadata.js';

async function main() {{
    try {{
        const result = await scrape_url_metadata("{url}");
        console.log(JSON.stringify(result));
    }} catch (error) {{
        console.error(JSON.stringify({{ error: error.message }}));
        process.exit(1);
    }}
}}

main();
"""
    
    # Write temporary script
    temp_script = "temp_scrape.js"
    with open(temp_script, 'w') as f:
        f.write(script_content)
    
    try:
        # Run the script using Node.js
        import subprocess
        result = subprocess.run(
            ['node', temp_script],
            cwd=os.path.join(os.path.dirname(__file__), '..', 'LLMBait'),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return {
                'status': 'error',
                'url': url,
                'error_message': result.stderr
            }
        
        return json.loads(result.stdout.strip())
    finally:
        # Clean up
        if os.path.exists(temp_script):
            os.remove(temp_script)

async def search_google_as_an_agent_to_find_the_best_result(
    query: str,
    objective: str,
    injectedResults: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Search Google as an agent using Stagehand.
    """
    # Create a temporary script to call the TypeScript function
    injected_results_json = json.dumps(injectedResults) if injectedResults else "null"
    
    script_content = f"""
import {{ search_google_as_an_agent_to_find_the_best_result }} from './googleSearch.js';

async function main() {{
    try {{
        // Mock page and stagehand for now since we can't easily pass them from Python
        const mockPage = {{
            act: async (action) => console.log('Mock act:', action),
            goto: async (url) => console.log('Mock goto:', url),
            extract: async (params) => {{
                console.log('Mock extract:', params);
                return {{
                    results: [
                        {{
                            title: 'Mock Search Result',
                            url: 'https://example.com',
                            description: 'This is a mock result',
                            rank: 1,
                            extractorRelevanceScore: 8.5,
                            resultId: 'mock1'
                        }}
                    ],
                    totalResults: 1
                }};
            }},
            observe: async (params) => {{
                console.log('Mock observe:', params);
                return [{{ selector: 'mock-selector' }}];
            }}
        }};
        
        const mockStagehand = {{
            log: (data) => console.log('Mock log:', data)
        }};
        
        const result = await search_google_as_an_agent_to_find_the_best_result(
            mockPage,
            mockStagehand,
            {{
                query: "{query}",
                objective: "{objective}",
                injectedResults: {injected_results_json}
            }}
        );
        console.log(JSON.stringify(result));
    }} catch (error) {{
        console.error(JSON.stringify({{ error: error.message }}));
        process.exit(1);
    }}
}}

main();
"""
    
    # Write temporary script
    temp_script = "temp_search.js"
    with open(temp_script, 'w') as f:
        f.write(script_content)
    
    try:
        # Run the script using Node.js
        import subprocess
        result = subprocess.run(
            ['node', temp_script],
            cwd=os.path.join(os.path.dirname(__file__), '..', 'LLMBait'),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            return {
                'error': result.stderr,
                'query': query,
                'totalResults': 0,
                'searchTime': 0,
                'selectedResultIndex': None,
                'results': []
            }
        
        return json.loads(result.stdout.strip())
    finally:
        # Clean up
        if os.path.exists(temp_script):
            os.remove(temp_script)

# Use the Python implementation directly (no async needed)
def scrape_url_metadata(url: str) -> Dict[str, Any]:
    """Scrape metadata from a URL using Python implementation"""
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

# def search_google_as_an_agent_to_find_the_best_result(
#     query: str,
#     objective: str,
#     injectedResults: Optional[List[Dict[str, Any]]] = None
# ) -> Dict[str, Any]:
#     """Synchronous wrapper for search_google_as_agent_stagehand"""
#     return asyncio.run(search_google_as_agent_stagehand(query, objective, injectedResults)) 


import requests
from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any
import json

def scrape_url_metadata(url: str) -> Dict[str, Any]:
    """
    Scrape metadata from a URL.
    
    Returns:
        Dict with status, url, title, metadescription, and optional error_message
    """
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
def monitored_scrape_url_metadata(url: str):
    return scrape_url_metadata(url)


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
def monitored_search_google(query: str, objective: str, injected_title: str = "", injected_url: str = "", injected_description: str = "", injected_rank: int = 1):
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
    
    return search_google_as_an_agent_to_find_the_best_result(
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