# deepchart

DeepChart is a deep-research agent built on top of 
[OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) and a custom 
[Event Registry](https://eventregistry.org/) tool to 
retrieve and group news by U.S. state.

## Local Setup

1. Install deps:

```bash
uv sync
```

2. Env vars:

```bash
export OPENAI_API_KEY=...
export EVENT_REGISTRY_API_KEY=...
export FIRECRAWL_API_KEY=...
```

3. Run

```bash
uv run main.py --prompt ""
```

## How it works

- `tools/event_registry.py`: Custom `event_registry_search` [FunctionTool](https://openai.github.io/openai-agents-python/tools/#function-tools) that queries Event Registry and groups results by state.
-  `tools/incidents.py`: Tracks incident
- `tools/scraper.py`: Custom [Firecrawl](https://www.firecrawl.dev) tool that srapes articles retrieved by Event Registry.
- `agent.py`: Defines two agents: Instruction (prompt optimization) and Research Agent.
- `main.py`: Agent loop and builds [Dash](https://dash.plotly.com/) visualization
