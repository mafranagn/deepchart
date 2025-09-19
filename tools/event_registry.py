from eventregistry import EventRegistry, QueryArticlesIter, QueryItems
import json
import os
from agents import function_tool
from typing import List


STATE_LIST = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
]


@function_tool(name_override="event_registry_search")
def event_registry(
    keywords: List(str),
    ignore: List(str),
    states: List(str),
    start_date: str,
    end_date: str,
) -> str:
    """
    Search Event Registry for news using a list of keywords, grouped by U.S. state.

    Args:
        keywords: Search keywords. The tool trims to a cumulative total of 15 words across the list of keyword strings.
        ignore: Keywords to ignore during search.
        states: Optional list of U.S. state names. Defaults to all 50 states.
        start_date: Optional ISO date (YYYY-MM-DD) inclusive start.
        end_date: Optional ISO date (YYYY-MM-DD) inclusive end.

    Returns:
        A JSON string with grouped results: { states: [ { state, count, articles: [...] } ] }
    """

    er = EventRegistry(apiKey=os.getenv("EVENT_REGISTRY_API_KEY"))

    final_list = []
    for state in states:
        location = er.getLocationUri(state)
        q_iter = QueryArticlesIter(
            keywords=QueryItems.OR(keywords),
            ignoreKeywords=QueryItems.OR(ignore),  # Ignore certain words
            keywordsLoc="body,title",
            lang="eng",
            dateStart=start_date,  # YYYY-MM-DD
            dateEnd=end_date,  # YYYY-MM-DD
            locationUri=location,  # State
            dataType=["news", "pr"],
            isDuplicateFilter="skipDuplicates",
            hasDuplicateFilter="skipHasDuplicates",
        )

        article_list = []
        for article in q_iter.execQuery(er, sortBy="date"):
            article_list.append(
                {
                    "title": article.get("title"),
                    "url": article.get("url"),
                    "date": article.get("date") or article.get("dateTime"),
                    "source": (article.get("source") or {}).get("title"),
                    "eventUri": article.get("eventUri"),
                    "location": state,
                }
            )

        final_list.append(
            {"state": state, "count": len(article_list), "articles": article_list}
        )

    # NewsAPI ai outputs a huge dictionary, we only need some of it
    return json.dumps({"states": final_list})
