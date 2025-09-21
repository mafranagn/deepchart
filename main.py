import os
from agents import ItemHelpers, Runner, set_default_openai_client
from agent import build_agent
from openai import AsyncOpenAI
import json
import pandas as pd
from map import make_choropleth
from dash import Dash, dcc, html
import argparse


# run_streamed() works async
async def main(prompt: str):
    app = Dash()

    state_dict = {}

    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=600.0)
    set_default_openai_client(client)  # Set client for agent library ????
    os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = (
        "1"  # No agent tracing/logging technique
    )

    agents = build_agent()

    result = Runner.run_streamed(
        agents["instruct"],
        input=prompt,
    )
    print("=== Run starting ===")

    async for event in result.stream_events():
        last_tool_call = ""
        # We'll ignore the raw responses event deltas
        if event.type == "raw_response_event":
            continue
        # When the agent updates, print that
        elif event.type == "agent_updated_stream_event":
            print(f"Agent updated: {event.new_agent.name}")
            continue
        # When items are generated, print them
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                last_tool_call = event.item.raw_item.name
                print("-- Tool was called")
            elif event.item.type == "tool_call_output_item":
                print(f"-- Tool output: {event.item.output}")
                if last_tool_call == "add_incident":
                    output = json.loads(event.item.output)
                    state_code = output.get("incident").get("state_code")
                    if state_code in state_dict:
                        state_dict[state_code] += 1
                    else:
                        state_dict[state_code] = 1

            elif event.item.type == "message_output_item":
                print(
                    f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}"
                )
            else:
                pass  # Ignore other event types

    df = pd.DataFrame(state_dict)

    figure = make_choropleth(df)

    app.layout = [html.H1("Deep Chart"), dcc.Graph(figure=figure)]
    app.run(debug=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", "--prompt")
    args = parser.parse_args()

    if args.prompt:
        raise Exception("Please enter a research prompt.")

    main(args.prompt)
