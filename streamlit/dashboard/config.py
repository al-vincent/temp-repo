"""Settings to use for the Dash app. Consists of:
    - App data references (e.g. paths, column headers);
    - Constant values (e.g. string literals, settings).
"""

# =====================================================================================
# Import libraries
# =====================================================================================
import os

# =====================================================================================
# Constants
# =====================================================================================
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

PAGE_TITLE = "Gowalla: Streamlit"
TITLE = "Gowalla Checkins Dashboard: Streamlit"
TITLE_TEXT = "A simple dashboard to experiment with Streamlit"

CHECKINS_PATH = os.path.join(ROOT_DIR, "gowalla_checkins_20k.csv")
USER_COL = "user"
GEO_COLS = ["lat", "lon"]
DATE_COL = "check_in_time"

EDGES_PATH = os.path.join(ROOT_DIR, "gowalla_edges_1k.csv")
NET_COL_NAMES = ["source", "target"]
NETWORK_GRAPH_PATH = os.path.join(ROOT_DIR, "network.html")


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