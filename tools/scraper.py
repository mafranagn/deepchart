from typing import List
from firecrawl import Firecrawl
import os
import json
from agents import function_tool


@function_tool
def batch_scrape(urls: List[str]) -> str:
    """
    Scrape a list of URLs and return markdown content per URL.

    Args:
        urls: List of absolute URLs to fetch.

    Returns:
        JSON string with shape: {
          "results": [
            { "url": str, "markdown": str }
          ]
        }
    """
    firecrawl = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))
    resp = firecrawl.batch_scrape(urls, wait_timeout=120, formats=["markdown"])
    # Wait up to 120 seconds for the scrape to complete

    data = resp.get("data", [])  # Get data dictionary from resp
    results = []
    for item in data:
        results.append(
            {
                "url": item.get("metadata", {}).get("sourceURL", ""),
                "markdown": item.get("markdown", ""),
            }
        )

    return json.dumps({"results": results})
    # Turn dictionary into string for the Agent
