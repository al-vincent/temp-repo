# =====================================================================================
# Import libraries
# =====================================================================================
import os
import json
import time

import click
from geograpy import extraction
import nltk
import pandas as pd

import conf


# =====================================================================================
# Helper functions
# =====================================================================================

def get_data(path, num_rows=None,  seed=conf.SEED):
    try:
        df = pd.read_json(path, orient="records")
    except Exception as err:
        print(f"*** ERROR: {err} Path: {path} ***")
    else:
        return df.sample(num_rows, random_state=seed) if num_rows else df

def download_nltk_resources(resources):
    for r in resources:
        nltk.download(r)


# =====================================================================================
# Drivers
# =====================================================================================
# command-line options
# @click.command()
# @click.option("-p", "--process", default=False, show_default=True, type=bool,
#     help="Whether to process the corpus (often takes a long time)")
def main():

    download_nltk_resources([
        "averaged_perceptron_tagger",
        "maxent_ne_chunker"
    ])
    path = os.path.join(conf.DATA_SOURCE["data"], "cg_enquiries.json")
    txt = get_data(path)["query"].tolist()    
    print(f"Processed text: \n{txt[0]}")

    print("\nExtracting places...", end="")
    places = extraction.Extractor(text=txt[0])
    places.find_geoEntities()
    print(places.places)


if __name__ == "__main__":
    main()