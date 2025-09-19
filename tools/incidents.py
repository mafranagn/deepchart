import json
from typing import Any, Dict, List

from agents import function_tool

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


@function_tool(name_override="add_incident")
def add_incident(state: str, description: str, references: List[str]) -> str:
    """
    Notify the app about a newly found incident to update the map.

    Args:
        state: U.S. state as full name (e.g., "California", "New York", etc.).
        description: Brief human-readable incident description.
        references: List of source URLs supporting the incident.

    Returns:
        JSON string with shape: {
          "incident": {
            "state_code": str, "description": str, "references": List[str]
          }
        }
    """
    code = STATE_LIST.get(state)
    if not code:
        return json.dumps(
            {
                "error": f"Unknown state: {state}",
            }
        )

    incident: Dict[str, Any] = {
        "state_code": code,
        "description": description,
        "references": references or [],
    }
    return json.dumps({"incident": incident}, ensure_ascii=False)
