import json
from typing import Any, Dict, List

from agents import function_tool
from state import US_STATES


@function_tool(name_override="add_incident")
def add_incident(state: str, year: int, description: str, references: List[str]) -> str:
    """
    Notify the user about a newly found incident to update the map.

    Args:
        state: U.S. state as full name (e.g., "California", "New York", etc.).
        year: Year the incident occured.
        description: Brief human-readable incident description.
        references: List of source URLs supporting the incident.

    Returns:
        JSON string with shape: {
          "incident": {
            "state_code": str, "state_name": str, "description": str, "year": year, "references": List[str]
          }
        }
    """
    code = US_STATES.get(state)
    if not code:
        return json.dumps(
            {
                "error": f"Unknown state: {state}",
            }
        )

    incident: Dict[str, Any] = {
        "state_code": code,
        "state_name": state,
        "description": description,
        "year": year,
        "references": references or [],
    }
    return json.dumps({"incident": incident}, ensure_ascii=False)
