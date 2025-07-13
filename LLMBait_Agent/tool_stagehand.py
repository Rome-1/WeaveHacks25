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

async def scrape_url_metadata(url: str) -> Dict[str, Any]:
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

# # Synchronous wrappers for the agent
# def scrape_url_metadata(url: str) -> Dict[str, Any]:
#     """Synchronous wrapper for scrape_url_metadata_stagehand"""
#     return asyncio.run(scrape_url_metadata_stagehand(url))

# def search_google_as_an_agent_to_find_the_best_result(
#     query: str,
#     objective: str,
#     injectedResults: Optional[List[Dict[str, Any]]] = None
# ) -> Dict[str, Any]:
#     """Synchronous wrapper for search_google_as_agent_stagehand"""
#     return asyncio.run(search_google_as_agent_stagehand(query, objective, injectedResults)) 