import os
from agents import ItemHelpers, Runner, set_default_openai_client
from agent import build_agent
from openai import AsyncOpenAI
import json
import pandas as pd
from map import make_choropleth
from dash import Dash, dcc, html
import argparse
from state import US_STATES


# run_streamed() works async
async def main(prompt: str):
    app = Dash()

    # Dictionaries for make_choropleth(df)
    complete_dict = {"locations": [], "animation_frame": [], "color": []}
    inter_dict = {}

    # Dictionaries for references df
    complete_ref = {"state_abbr": [], "years": [], "references": []}
    inter_ref = {}

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
                    year = output.get("incident").get("year")
                    reference = output.get("incident").get("reference")
                    if state_code in inter_dict and year in inter_dict[state_code]:
                        inter_dict[state_code][year]["color"] += 1
                        inter_ref[state_code][year]["references"].append(reference)
                    else:
                        inter_dict[state_code][year]["color"] = 1
                        inter_ref[state_code][year]["references"] = [reference]
            elif event.item.type == "message_output_item":
                print(
                    f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}"
                )
            else:
                pass  # Ignore other event types

    # CREATE complete_dict and complete_ref from inter_dict and inter_ref, respectively
    for state_code in inter_dict:
        for year in inter_dict[state_code]:
            complete_dict["locations"].append(state_code)
            complete_dict["animation_frame"].append(year)
            complete_dict["color"].append(inter_dict[state_code][year]["color"])

            complete_ref["state_abbr"].append(state_code)
            complete_ref["years"].append(year)
            complete_ref["references"].extend(inter_ref[state_code][year]["references"])

    # CREATE final_dict, make_choropleth()-ready df
    us_df = pd.Dataframe(US_STATES)
    final_dict = complete_dict.merge(us_df, how="left", on="locations")

    df = pd.DataFrame(final_dict)
    # ref_df = pd.DataFrame(complete_ref)

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
