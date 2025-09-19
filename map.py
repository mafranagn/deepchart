import pandas as pd
import plotly.express as px


def make_choropleth(df: pd.DataFrame):
    """
    Creates a dataframe by compiling year_state_incidents dictionaries
    based on the total number of incidents per state each year.
    Use two-letter state abbreviations.
    With the df, make choropleth map of the US.

    Args:
      year_state_stateabbr_incidents (dict): {"locations":"stateAbbr",
                                              "hover_name":"state",
                                              "color":"incidents",
                                              "animiation_frame":"year"
                                              }
      title (str): Appropriate title for choropleth graph

    Returns:
      A complete dataframe and a choropleth map.
    """

    # Max value of total incidents - so legend range is uniform
    maximum = max(df["color"])

    # Build choropleth
    figure = px.choropleth(
        df,
        locations="locations",
        locationmode="USA-states",
        scope="usa",
        color="color",
        hover_name="hover_name",  # Full State Name
        hover_data={"locations": False},  # Take out info on hover data
        animation_frame="animation_frame",
        labels={
            "animation_frame": "Year",
            "color": "Incidents",
        },
        range_color=[0, maximum],
        # title=title
    )
    figure.update_layout(
        hoverlabel_bgcolor="white",
        hoverlabel_bordercolor="black",
        hoverlabel_font_color="black",
    )

    return df, figure
