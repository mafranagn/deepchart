from typing import Dict

from agents import Agent, ModelSettings
from openai.types.shared import Reasoning

from tools.event_registry import search_event_registry
from tools.scraper import scrape_urls
from tools.incidents import add_incident


RESEARCH_INSTRUCTION_AGENT_PROMPT = """
Rewrite the user's request as explicit, step-by-step research instructions for a deep research agent, then transfer to that agent.

REQUIREMENTS:
- Use the first person voice (as the user).
- Include explicit directives to search U.S. news and group results by U.S. state.
- If the user specified time ranges, states, or severity (fatal-only), include them. If not, look for news within the last 12 months.
- Define an iterative loop for the research agent:
  1) Use the `event_registry_search` tool with the given keywords/timeframe to fetch recent articles, grouped by state.
  2) For each state, collect article URLs and call the `scrape_urls` tool to retrieve markdown content.
  3) From the scraped content and ER metadata, identify distinct incidents relevant to the query.
  4) For each confirmed incident, call the `add_incident` tool with:
     - state: full U.S. state name (e.g., "California")
     - description: concise summary (include date/location if known)
     - references: list of source URLs
  5) Deduplicate incidents by URL/title/eventUri to avoid double counting.
  6) Continue looping (paginate ER or try additional keywords) until no new incidents are found or limits are reached.
- Ask the research agent to return at the end:
  1) A per-state list of incidents with title, URL, date, and source
  2) Aggregated counts per state
  3) Any patterns, notable clusters, or data quality notes
"""


def build_agent() -> Dict[str, Agent]:
    research_agent = Agent(
        name="research_agent",
        model="gpt-5",
        model_settings=ModelSettings(
            reasoning=Reasoning(effort="minimal"), verbosity="low"
        ),
        tools=[search_event_registry, scrape_urls, add_incident],
        instructions=(
            "Execute an iterative research loop to discover incidents and update the map in real time.\n"
            "Loop steps: (1) Use 'event_registry_search' with the user's keywords/timeframe to fetch recent articles grouped by state.\n"
            "(2) For each state's articles, call 'scrape_urls' with their URLs to get markdown content.\n"
            "(3) From the scraped content and ER metadata, identify distinct incidents relevant to the query.\n"
            "(4) For every confirmed incident, immediately call 'add_incident' with: state as full name (e.g., California), "
            "a concise description (include date/location if known), and references as a list of source URLs.\n"
            "(5) Deduplicate incidents by URL/title/eventUri to avoid double counting.\n"
            "(6) Continue looping (paginate ER or try additional keywords) until no new incidents are found or limits are reached.\n"
            "Rules: Do not ask the user any follow-up questions. Prefer the provided tools. If no timeframe is specified, use the last 12 months."
        ),
    )

    instruction_agent = Agent(
        name="Research Instruction Agent",
        model="gpt-5",
        model_settings=ModelSettings(reasoning=Reasoning(effort="minimal")),
        instructions=RESEARCH_INSTRUCTION_AGENT_PROMPT,
        handoffs=[research_agent],
    )

    return {
        "instruct": instruction_agent,
        "research": research_agent,
    }
