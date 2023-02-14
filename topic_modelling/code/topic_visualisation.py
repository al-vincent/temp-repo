# =====================================================================================
# Import libraries
# =====================================================================================
import os
import json
import pickle
import time

import click
from gensim.corpora import Dictionary
import pyLDAvis.gensim_models

import conf
import topic_modelling as tm


# =====================================================================================
# Class Definitions
# =====================================================================================
class TopicVisualisation:
    def __init__(self, model, corpus, dictionary, f_path):
        self.model = model
        self.corpus = corpus
        self.dct = dictionary
        self.f_path = f_path
    
    def create_save_vis(self):
        vis = pyLDAvis.gensim_models.prepare(self.model, self.corpus, self.dct)
        pyLDAvis.save_html(vis, self.f_path)


# =====================================================================================
# Helper Functions
# =====================================================================================
def run_lda_vis(path, num_topics, out_path):
    dct, corpus, m_c = tm.load_artifacts(path)
    model = None
    for m in m_c:
        if m["topics"] == num_topics:
            model = m["model"]

    if model:
        tv = TopicVisualisation(model, corpus, dct, out_path)
        tv.create_save_vis()
    else:
        print(f"There is no available model with {num_topics} topics")


# =====================================================================================
# Drivers
# =====================================================================================
# command-line options
@click.command()
@click.option("-t", "--topics", type=int, help="Number of topics to use")
def main(topics):

    out_path = os.path.join(conf.DATA_SOURCE["vis"], 
                            f"{conf.FILE_NAMES['lda_vis']}_{topics}_topics.html")
    run_lda_vis(conf.DATA_SOURCE["models"], topics, out_path)
    

if __name__ == "__main__":
    main()