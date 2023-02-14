"""Settings to use for the Dash app. Consists of:
    - App data references (e.g. paths, column headers);
    - Constant values (e.g. string literals, settings);
    - Secrets (set as environment variables).
"""

# =====================================================================================
# Import libraries
# =====================================================================================
import os

# =====================================================================================
# Constants
# =====================================================================================
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# String literals to be embedded into the page
PAGE_TITLE = "Gowalla: Dash"
TITLE = "Gowalla Checkins Dashboard: Plotly Dash"
TITLE_TEXT = "A simple dashboard to experiment with Dash"


# Paths and references to the app data
CHECKINS_PATH = os.path.join(ROOT_DIR, "gowalla_checkins_20k.csv")
USER_COL = "user"
GEO_COLS = ["lat", "lon"]
DATE_COL = "check_in_time"

EDGES_PATH = os.path.join(ROOT_DIR, "gowalla_edges_1k.csv")
NET_COL_NAMES = ["source", "target"]
NETWORK_GRAPH_PATH = os.path.join(ROOT_DIR, "network.html")


# The app uses a personal mapbox token, so putting as an environment variable
MAPBOX_PUBLIC_TOKEN = os.getenv("MAPBOX_TOKEN", None)


# Styling and settings for the Cytoscape network graph
CYTO_STYLES = {
    'container': {
        'position': 'fixed',
        'display': 'flex',
        'flexDirection': 'column',
        'height': '450px',
        'width': '100%'
    },
    'cy-container': {
        'flex': '1',
        'position': 'relative'
    },
    'cytoscape': {
        'position': 'absolute',
        'width': '100%',
        'height': '100%',
        'zIndex': 999
    }
}

CYTO_STYLESHEET = [
    {
        "selector": "node",
        "style": {
            "content": "data(label)",                  
            "background-color": "blue",
            "border-size": 2,
            "border-color": "red",
            "color": "violet",
            "opacity": 0.7,

        }
    },
]

CYTO_LAYOUT = {
    'name': 'cose',
    'idealEdgeLength': 100,
    'nodeOverlap': 20,
    'refresh': 20,
    'fit': True,
    'padding': 30,
    'randomize': True,
    'componentSpacing': 100,
    'nodeRepulsion': 4000000,
    'edgeElasticity': 100,
    'nestingFactor': 5,
    'gravity': 80,
    'numIter': 1000,
    'initialTemp': 200,
    'coolingFactor': 0.95,
    'minTemp': 1.0
}


# Strings to use for 'explainer' text (formatted as Markdown)
PROJECT_OVERVIEW_MD = """
    #### Project overview
    This small project is designed to understand the capabilities of 
    [Streamlit](https://streamlit.io/). This package has become extremely popular for 
    rapidly developing data-focussed web apps, as it only requires a small amount of 
    Python code to create impressive apps, with no need for HTML, JavaScript or CSS. 
    This sounds ideal for many use-cases; but will also introduce issues..

    The layout has been specifically chosen as it includes some fairly useful graphics
    that are not always well-supported:
    - **Time-slider.** Very useful for filtering time-series data.
    - **Map.** Esssential for displaying geographic data.
    - **Network graph.** Powerful and intuitive for displaying data on social networks, 
    physical networks etc. (**Note:** many platforms struggle to compute and display
    large, complex network graphs.)
"""

DATA_OVERVIEW_MD = """
    #### Data overview
    The [data](https://snap.stanford.edu/data/loc-gowalla.html) used for this 
    dashboard is provided by the 
    [Stanford Network Analysis Project (SNAP)](https://snap.stanford.edu/). 
    It comes from a location-based social platform called 
    [Gowalla](https://go.gowalla.com/), and consists of two sources:
    - A set of check-ins that provide lat/lon coordinates for each user at a particular timestamp;
    - A set of links between users, providing the friendship network.
    
    The full datasets are fairly long (~6.4 million checkins and nearly 1 
    million connections), so for this demo, a cut has been taken of each 
    one. 20,000 rows have been randomly sampled from the check-ins data, 
    and 1,000 edges of the network graph (even this small sample causes 
    issues with rendering the graph).
"""