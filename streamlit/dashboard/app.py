"""A simple web app using the Streamlit framework. The main aim is to understand how
Streamlit works by using it on a reasonably realistic problem, with real-world data. 

The ultimate goal is to do a loose comparision between Streamlit and some alternatives,
including:
- Plotly Dash (almost a direct 'competitor' to Streamlit)
- A 'full-stack' FOSS solution, using Flask, Bootstrap , Chart.js, d3.js
- Oracle APEX (possibly)

All dependencies are shown in requirements.txt

To run the app, run 'streamlit run app.py' in the terminal, then visit
http://localhost:8501/ in your web browser.
"""


# =====================================================================================
# Import libraries
# =====================================================================================
# External packages
import networkx as nx
import pandas as pd
from pyvis.network import Network
import streamlit as st
import streamlit.components.v1 as components

# Local imports
import config as c


# =====================================================================================
# Page config
# =====================================================================================
# Add some basic setup info
st.set_page_config(
    page_title=c.PAGE_TITLE,
    layout="wide"
)


# =====================================================================================
# Helper functions
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


def filter_edges(checkins_df, edges_df):
    """Filter out any users who aren't included in the checkins.

    Parameters:
        checkins_df (Pandas DataFrame): DataFrame containing check-in info (incl users)
        edges_df (Pandas DataFrame): DataFrame containing the links between users

    Returns:
        Pandas DataFrame: the 'edges' DataFrame after any users not in checkins_df have
        been removed
    """
    users = checkins_df[c.USER_COL].unique()
    return edges_df[
        (edges_df[c.NET_COL_NAMES[0]].isin(users)) & 
        (edges_df[c.NET_COL_NAMES[1]].isin(users))
    ]

def create_network_html(edges_df, path=c.NETWORK_GRAPH_PATH):
    """Create the HTML file containing the social network, for display by the app.

    Parameters:
        edges_df (Pandas DataFrame): DataFrame containing the links between users.
            Assumes that the columns are named "source" and "target".
        path (str, optional): the path where the HTML file will be saved. Defaults to
            './network.html' (set in config.py)
    """
    # Create the network in networkx, and generate the html in pyvis
    G = nx.from_pandas_edgelist(edges_df)
    net = Network(height="500px", width='100%')
    net.from_nx(G)

    # Display the settings
    # net.show_buttons()

    # Save the HTML in the same directory as this file
    net.save_graph(path)


@st.cache()
def get_all_data(checkins_path=c.CHECKINS_PATH, edges_path=c.EDGES_PATH):
    """Convenience function to read the data required (allows use of st.cache).

    Parameters:
        checkins_path (str, optional): path to the checkins data. Defaults to 
            CHECKINS_PATH in config.py
        edges_path (str, optional): path to the edges data. Defaults to EDGES_PATH in
            config.py

    Returns:
        tuple(df, df, df): tuple containing three Pandas DataFrame objects - the 
            check-ins data, check-ins resampled to daily frequency, and the edges data.
    """
    checkins_df = load_data(
        path=checkins_path, 
        date_col=c.DATE_COL,
        infer_datetime_format=True
    )
    # Roll-up the check-ins to capture on a daily basis
    daily_checkins = checkins_df[c.USER_COL].resample("D").count()
    edges_df = load_data(path=edges_path)

    return checkins_df, daily_checkins, edges_df


def create_page(checkins_df, daily, edges_df):
    """Create the overall page structure and content.

    Parameters:
        checkins_df (Pandas DataFrame): check-ins data, including user id; date/time of
            each check-in; location of check-in (as decimal lat/lon); and location id.
        daily (Pandas DataFrame): check-ins per day. Includes daily timestamps (index) 
        and count of checkins for each day.
        edges_df (Pandas DataFrame): links between pairs of users. Two columns, 
            "source" and "target". The value in each column is a user id.
    """
    # Add a title and some text
    st.title(c.TITLE)
    st.markdown(c.TITLE_TEXT)
    with st.expander("More information about the project"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(c.PROJECT_OVERVIEW_MD)
        with col2:
            st.markdown(c.DATA_OVERVIEW_MD)
    st.markdown("---")

    # Add the date-range slider
    date_range = st.slider(
        "Check-in dates",
        value=(daily.index.min().to_pydatetime(), daily.index.max().to_pydatetime())
    )

    # When the slider is updated, filter the data to only include checkins and links 
    # that are relevant between the dates selected
    checkins_df = checkins_df[
        (checkins_df.index >= date_range[0]) & 
        (checkins_df.index <= date_range[1])
    ]
    edges_df = filter_edges(checkins_df, edges_df)

    # Add the checkins-over-time bar chart
    st.subheader("Check-ins over time")
    time_container = st.container()
    with time_container:        
        st.bar_chart(daily, height=100)

    # Add a new row, with the map and network graph side-by-side
    map_network_container = st.container()
    with map_network_container:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Check-in locations")
            st.map(checkins_df[c.GEO_COLS])
        with col2:
            st.subheader("Social network links")
            create_network_html(edges_df)
            with open(c.NETWORK_GRAPH_PATH, "r", encoding="utf-8") as f:
                source_code = f.read()
            components.html(source_code, height=550)


# =====================================================================================
# Drivers
# =====================================================================================
def main():
    checkins_df, daily_checkins, edges_df = get_all_data()
    create_page(checkins_df, daily_checkins, edges_df)
    

if __name__ == "__main__":
    main()
