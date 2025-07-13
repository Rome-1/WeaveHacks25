import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from LLMBait.scrape_url_metadata import scrape_url_metadata
from LLMBait.googleSearch import search_google_as_an_agent_to_find_the_best_result

LLMBait_agent = Agent(
    name="LLMBait",
    model="gemini-2.0-pro",
    description=(
        "Helps users understand what browser agents will click on in a Google search. "
        "Can simulate a search, inject a custom result (from a URL or manual entry), and show which result the agent would select."
    ),
    instruction=(
        "Prompt the user for a URL (to scrape) or manual entry (title, url, metadescription), and an objective. "
        "Suggest a search query based on the objective, allow the user to edit, and confirm all inputs before running the search. "
        "Present the results in a clear, readable format, highlighting the agent's selection and relevance scores."
    ),
    tools=[scrape_url_metadata, search_google_as_an_agent_to_find_the_best_result],
)