"""A simple web app using Plotly's Dash framework. The main aim is to understand how
Dash works by using it on a reasonably realistic problem, with real-world data. 

The ultimate goal is to do a loose comparision between Dash and some alternatives,
including:
- Streamlit (almost a direct 'competitor' to Dash)
- A 'full-stack' FOSS solution, using Flask, Bootstrap , Chart.js, d3.js
- Oracle APEX (possibly)

All dependencies are shown in requirements.txt

To run the app, run 'python app.py' in the terminal, then visit
http://localhost:8050/ in your web browser.
"""


# =====================================================================================
# Import libraries
# =====================================================================================
# External packages
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Local imports
import config as c


# =====================================================================================
# Initialise the app
# =====================================================================================
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = c.PAGE_TITLE


# =====================================================================================
# Load the data
# =====================================================================================
def load_data(path, date_col=None, infer_datetime_format=False):
    """Boilerplate function to load the check-in and edges data from the two CSV files.

    Parameters:
        path (str): path to the file containing the data.
        date_col (str, optional): Name of the timestamp column. Defaults to None.
        infer_datetime_format (bool, optional): flag to indicate whether Pandas should
            attempt to automatically infer the date format. Defaults to False.

    Returns:
        Pandas DataFrame: the date read from the file.
    """
    parse_dates = [date_col] if date_col else None
    df = pd.read_csv(
        path,
        parse_dates=parse_dates, 
        infer_datetime_format=infer_datetime_format 
    )

    # If a date column has been provided, set it to be the index (for resampling)
    df = df.set_index(date_col) if parse_dates else df
    return df


def create_cyto_data(edges_df):
    """Convert the Pandas DataFrame of edges to the format that dash-cytoscape uses.

    Parameters:
        edges_df (Pandas DataFrame): 

    Returns:
        dict: data formatted as a dict-of-dicts, including both nodes and edges. The 
            format is described here: https://dash.plotly.com/cytoscape/elements 
    """
    # Extract the nodes from edges_df and convert to dict-of-dicts
    node_list = list(set(edges_df["source"].tolist() + edges_df["target"].tolist()))
    nodes = [{"data": {"id": str(node), "label": f"User {node}"}} for node in node_list]

    # Extract the edges. There may be an elegant, vectorised way to do this; I couldn't
    # immediately think of it (and with a graph this size, the time-lag is no issue)
    edges = [{
        "data": {
            "source": str(edge[0]),
            "target": str(edge[1]),
            "label": f"User {edge[0]} to User {edge[1]}"
        }
    } for edge in edges_df.itertuples(index=False)]

    # Concatenate the dicts and return
    return nodes + edges


# Load the three dataframes. 
# NOTE: these *must* be globals (AFAIK), so that the original data is available to the
# callbacks.
checkins_df = load_data(
    path=c.CHECKINS_PATH, 
    date_col=c.DATE_COL,
    infer_datetime_format=True
)
# Roll-up the check-ins to capture on a daily basis
daily_checkins = checkins_df[c.USER_COL].resample("D").count()
edges_df = load_data(path=c.EDGES_PATH)


# =====================================================================================
# Create the components
# =====================================================================================
def get_marks(date_series):
        """Convert DateTimeIndex to a dict that maps epoch to str. Used for generating
        the marks on the date-range slider.

        Parameters:
            date_series (Pandas Series): Series of DateTimeIndex values 

        Returns:
            dict: format is {
                1270080000: 'Apr 2010',
                1235865600: 'Mar 2009',
                ...etc.
            }
        """
        # extract unique month/year combinations as a PeriodIndex
        months = date_series.to_period("M").unique()
        # convert PeriodIndex to epoch series and 'mmm YYYY' string series
        epochs = months.to_timestamp().astype(np.int64) // 10**9
        strings = months.strftime("%b %Y")

        return dict(zip(epochs, strings))

def build_slider(date_series):
    """Create the date range slider, with marks for each month in 'mmm YYYY' format.

    NOTE: Dash RangeSlider currently doesn't work well with datetime-type objects. The
    workaround is to convert the datetimes to epochs (i.e. integers), and map these to
    strings that show the date in the desired format for display.

    Parameters:
        date_series (Pandas Series): Series of DateTimeIndex values 

    Returns:
        Plotly RangeSlider object: the RangeSlider generated
    """
    fig = dcc.RangeSlider(
        allowCross=False,
        id="date-slider",
        min=pd.Timestamp(date_series.min()).timestamp(),
        max=pd.Timestamp(date_series.max()).timestamp(),
        marks = get_marks(date_series),
    )

    return fig


def build_checkins_bar(df):
    """Create the 'daily check-ins over time' bar chart.

    Parameters:
        df (Pandas DataFrame): DataFrame with timestamps as the index (one row per day)
            and check-in count as the only column.

    Returns:
        Plotly Express Bar Chart object: the bar chart created.
    """
    # Create the graph
    fig = px.bar(df, height=150, 
                labels={"value": "#check-ins", "check_in_time": "Date"})
    # Override the default margin at the top, and hide the legend (we don't need it)
    fig.update_layout(margin=dict(t=0), showlegend=False)
    return fig
    

def build_map(df, mapbox_token=c.MAPBOX_PUBLIC_TOKEN):
    """Create the 'check-in locations' map.

    Parameters:
        df (Pandas DataFrame): DataFrame containing the lat/lon check-in locations
        mapbox_token (str, optional): MapBox access token. Defaults to 
        c.MAPBOX_PUBLIC_TOKEN, set in config.py       

    Returns:
        Plotly Scattermapbox object: the map generated, with a marker for each check-in

    NOTE: the map is generated from vector maps provided by MapBox (see 
    https://www.mapbox.com/). This requires an API token, generated when an account is
    created. See https://docs.mapbox.com/help/glossary/access-token/
    """
    fig = go.Figure(
        go.Scattermapbox(
            hoverinfo="text",
            lat=df["lat"].tolist(), 
            lon=df["lon"].tolist(), 
            mode="markers",
            marker=go.scattermapbox.Marker(size=5),
            opacity=0.5,
            text= (
                "lat: " + df["lat"].round(2).astype(str) +", " +
                "lon: " + df["lon"].round(2).astype(str)
            ).tolist()
        )
    )
    
    fig.update_layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_token,
            bearing=0,
            center=dict(lat=51.509, lon=0),  # centre the map on London
            pitch=0,
            zoom=1
        ),
        margin=dict(t=0, b=0, l=0, r=0),
    )

    return fig

def build_network(elements):
    """Generate the network graph, using dash-cytoscape.

    Parameters:
        elements (dict): nodes and edges of the graph, in the format required cytoscape

    Returns:
        Cytoscape network object: the network generated from the nodes and edges.

    NOTE: 
    - A lot of styling and settings for the network have been factored into 
        config.py
    - The graph will usually render outside the intended panel initially, and needs to
        be dragged in. It's not clear why this is; seems to be an issue with 
        dash-cytoscape generally, as several examples on their web pages have a similar
        issue.
    """
        
    fig = cyto.Cytoscape(
        id='cytoscape',
        elements=elements,
        stylesheet=c.CYTO_STYLESHEET,
        style=c.CYTO_STYLES['cytoscape'],
        layout= c.CYTO_LAYOUT,
        responsive=True
    )

    return fig


def build_layout():
    """Driver function to set up the overall app."""
    
    app.layout = dbc.Container(
        [
            # Title and sub-title
            dbc.Row(
                dbc.Col([
                    html.H1(children=c.TITLE),                        
                    html.Div(children=c.TITLE_TEXT),
                ], class_name="m-4 lead"),
            ),

            # Expand panel that contains more info about the project. Implemented as
            # an accordian component, with a single item
            dbc.Row(
                dbc.Col(
                    dbc.Accordion(                        [
                        dbc.AccordionItem(
                            dbc.Row([
                                dbc.Col(dcc.Markdown(c.PROJECT_OVERVIEW_MD)),
                                dbc.Col(dcc.Markdown(c.DATA_OVERVIEW_MD))
                            ]),
                            title="More information about the project",
                        ),
                    ], start_collapsed=True,)
                )
            ),

            # Divider line
            dbc.Row(
                dbc.Col(html.Hr()),
                class_name="my-4"
            ),

            # Date range slider
            dbc.Row(                
                dbc.Col([
                    html.P("Check-in dates"),
                    build_slider(daily_checkins.index), 
                ]),
                class_name="mx-4 mb-4"
            ),

            # Check-ins over time bar graph
            dbc.Row(
                dbc.Col([
                    html.H3(children='Check-ins over time'),
                    dcc.Graph(id='daily-checkins-graph'),
                ]),
                class_name="m-2"
            ),

            # Check-in locations map and network graph
            dbc.Row([
                # Check-in locations map
                dbc.Col([
                    html.H3(children='Check-in locations'),
                    dcc.Graph(id='checkins-map'),                    
                ], class_name="col-md-6"),
                # Network graph
                dbc.Col([
                    html.H3(children='Social network links'),
                    html.Div(style=c.CYTO_STYLES['container'], children=[                            
                        html.Div(
                            id="network-graph", 
                            style=c.CYTO_STYLES['cy-container']
                        ),
                    ]),                    
                ], class_name="col-md-6")
            ], class_name="m-2"),
        ],
        fluid=True
    )


# =====================================================================================
# Callbacks
# =====================================================================================
@app.callback(
    Output("daily-checkins-graph", "figure"),
    Output("checkins-map", "figure"),
    Output("network-graph" , "children"),
    Input("date-slider", "value")
)
def update_date_slider(dates):
    """Callback that updates all plots when the date slider is moved.

    Parameters:
        dates (list or None): 
            - If the date slider has been used; a list of two ints, where each int is 
            the epoch (UNIX time) representation of the date selected
            - If the date slider hasn't been used (e.g. on initial load); will be None

    Returns:
        3 x Plotly figure objects:
            - Plotly Express Bar Chart object, showing check-ins per day;
            - Plotly Scattermapbox object, showing check-in locations;
            - Dash-cytoscape object, showing links between users
    """
    if dates:
        # convert the epochs
        min_date = pd.to_datetime(dates[0], unit="s", utc=True)        
        max_date = pd.to_datetime(dates[1], unit="s", utc=True)
        new_chk_df = checkins_df[
            (checkins_df.index >= min_date) & (checkins_df.index <= max_date)
        ]
        new_daily_df = new_chk_df[c.USER_COL].resample("D").count()
        

        users = new_chk_df["user"].unique()
        new_edges_df = edges_df[
            (edges_df["source"].isin(users)) & (edges_df["target"].isin(users))
        ]
    else:
        new_chk_df = checkins_df
        new_daily_df = daily_checkins
        new_edges_df = edges_df


    daily_checkins_fig = build_checkins_bar(new_daily_df)
    checkins_map_fig = build_map(new_chk_df)

    elements = create_cyto_data(new_edges_df)
    network_fig = build_network(elements)

    return daily_checkins_fig, checkins_map_fig, network_fig
        

# =====================================================================================
# Drivers
# =====================================================================================
def main():
    """Driver for the app"""

    # build_layout(checkins_df, daily_checkins, edges_df, app)
    build_layout()

    # NOTE: this must be done LAST!!
    app.run_server(debug=True)

if __name__ == '__main__':
    main()