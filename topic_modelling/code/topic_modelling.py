
# =====================================================================================
# Import libraries
# =====================================================================================
import os
import json
import pickle
import time
import warnings
def no_op(*args, **kwargs): pass
warnings.warn = no_op

import click
from gensim.corpora import Dictionary
from gensim.models import LdaModel, LdaMulticore, CoherenceModel
import matplotlib.pyplot as plt

import conf
import text_processing as tp


# =====================================================================================
# Class Definitions
# =====================================================================================

class GensimTopicModeller:
    def __init__(self, docs, num_topics, dct=None, corpus=None, passes=10, 
                single_model=True, topics={"start":2, "limit":30, "step":1},
                seed=conf.SEED, save_plot=False, plot_path=conf.DATA_SOURCE["vis"],
                dict_no_below=5, dict_no_above=0.9):
        self.docs = docs
        self.dct = self.get_dictionary(dct, docs, dict_no_below, dict_no_above)
        self.num_topics = num_topics
        self.corpus = corpus if corpus else [self.dct.doc2bow(doc) for doc in docs]
        self.passes = passes
        self.single_model = single_model
        self.topics = topics
        self.seed = seed
        self.save_plot = save_plot
        self.plot_path = plot_path
    
    def get_dictionary(self, dct, docs, no_below, no_above):
        # Filter out words that occur less than 20 documents, or more than 50% of the documents.
        if dct:
            return dct
        else:
            dictionary = Dictionary(docs)
            # dictionary.filter_extremes(no_below=no_below, no_above=no_above)
            return dictionary

    def run_lda(self, num_topics):
        return LdaMulticore(
            self.corpus,
            num_topics=num_topics,
            id2word=self.dct,
            passes=self.passes,
            random_state=self.seed,
            workers=4
        )

    def run_coherence(self, model, coherence_type="c_v"):
        return CoherenceModel(
            model=model,
            texts=self.docs, 
            dictionary=self.dct, 
            coherence=coherence_type
        )

    def get_models_and_coherence(self):
        """Compute c_v coherence for different numbers of topics.

        Returns:
            - list, where each element is a dict of the form:
            {   
                "topics": int, the number of topics in the model
                "model": <Gensim LdaMulticore object, the model for i topics>
                "coherence": float, the c_v coherence for the model
            }
        """

        rng = ([self.num_topics, self.num_topics+1, 1] if self.single_model 
            else [self.topics["start"], self.topics["limit"], self.topics["step"]])
        
        models_and_coherence = []
        for i in range(rng[0], rng[1], rng[2]):
            print(f"  > Calculating model with {i} topics...", end="")
            model = self.run_lda(i)
            cv_model = self.run_coherence(model)
            models_and_coherence.append(
                {"topics": i, "model": model, "coherence": cv_model.get_coherence()}
            )
            print("COMPLETE")

        return models_and_coherence

    def save_coherence_plot(self, coherence_vals):
        x = range(self.topics["start"], self.topics["limit"], self.topics["step"])
        plt.plot(x, coherence_vals)
        plt.xlabel("Number of topics")
        plt.ylabel("Coherence score")
        plt.legend(("cv_coherence"), loc="best")
        plt.savefig(os.path.join(self.plot_path, conf.FILE_NAMES["cv_plt"]))
    
    def run_topic_modelling(self):
        models_coherence = self.get_models_and_coherence()
        if self.save_plot:
            coherence = [i["coherence"] for i in models_coherence]
            self.save_coherence_plot(coherence)
        return (self.dct, self.corpus, models_coherence)
    

# =====================================================================================
# Helper functions
# =====================================================================================

def save_artifacts(dct, corpus, model_coherence, path=conf.DATA_SOURCE["models"]):
    dct.save(os.path.join(path, conf.FILE_NAMES["dict"]))
    with open(os.path.join(path, conf.FILE_NAMES["corpus"]), "wb") as f:
        pickle.dump(corpus, f)
    with open(os.path.join(path, conf.FILE_NAMES["models_cvs"]), "wb") as f:
        pickle.dump(model_coherence, f)

def load_artifacts(path):
    dct = Dictionary.load(os.path.join(path, conf.FILE_NAMES["dict"]))
    with open(os.path.join(path, conf.FILE_NAMES["corpus"]), "rb") as f:
        corpus = pickle.load(f)
    with open(os.path.join(path, conf.FILE_NAMES["models_cvs"]), "rb") as f:
        models_coherence = pickle.load(f)
    
    return dct, corpus, models_coherence


def run_lda(run_model, docs=None, num_topics=None, dct=None, corpus=None, passes=10,
            single_model=True, topics={"start":2, "limit":30, "step":1}, 
            seed=conf.SEED, save_plot=False, plot_path=conf.DATA_SOURCE["vis"],
            model_path=conf.DATA_SOURCE["models"]):
    
    if run_model:   
        gtm = GensimTopicModeller(docs, num_topics, dct=dct, corpus=corpus, 
                                passes=passes, single_model=single_model, 
                                topics=topics, seed=seed, save_plot=True)
        dct, corpus, m_c = gtm.run_topic_modelling()
        save_artifacts(dct, corpus, m_c)
    else:
        dct, corpus, m_c = load_artifacts(model_path)

    return dct, corpus, m_c


# =====================================================================================
# Drivers
# =====================================================================================
# command-line options
@click.command()
@click.option("--lda", default=False, show_default=True, type=bool,
    help="Whether to run a new LDA model")
def main(lda):

    txt = tp.get_processed_text(conf.DATA_SOURCE, num_rows=None, run_processor=False)

    start_m = time.time()
    topic_range  = {"start":2, "limit":21, "step":1}
    dct, corpus, m_c = run_lda(run_model=True,
                               docs=txt, 
                               single_model=False, 
                               topics=topic_range, 
                               save_plot=True)
    end_m = time.time()
    print(f"Number of terms in dictionary: {len(dct)}")
    print(f"Coherence values: \n{[i['coherence'] for i in m_c]}")
    print(f"Topic modelling COMPLETE. Time: {end_m - start_m:.1f}")


if __name__ == "__main__":
    main()