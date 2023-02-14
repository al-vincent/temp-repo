# =====================================================================================
# Import libraries
# =====================================================================================
import os
import json
import time

import click
import nltk
from nltk.corpus import stopwords, words
from nltk.metrics.distance import edit_distance
from nltk.tokenize import word_tokenize
import pandas as pd
import spacy

import conf

# =====================================================================================
# Class Definitions
# =====================================================================================

class TextProcessor:
    def __init__(self, df,check_sp=False, resources=conf.NLTK["resources"],
                stopwords=None, vocab=None, keep_list=conf.KEEP_LIST,  
                replace_map=conf.REPLACE_MAP):
        self.download_nltk(resources=resources)
        self.nlp = spacy.load("en_core_web_md")
        self.df = df
        self.stopwords = stopwords if stopwords else self.get_stopwords()
        self.vocab = vocab if vocab else self.get_vocab()
        self.keep_list = keep_list
        self.check_sp = check_sp
        self.replace_map = replace_map

    def download_nltk(self, resources):
        for r in resources:
            nltk.download(r)

    def get_stopwords(self):
        return stopwords.words("english") + conf.EXTRA_STOP_WORDS

    def get_vocab(self):
        # combine the vocabularies from NLTK and spaCy into a single list, retaining 
        # only words that start with a letter
        joint_vocab = words.words() + list(self.nlp.vocab.strings)
        vocab = [wd.lower() for wd in joint_vocab if wd.isalpha()]
        vocab = list(set(vocab))

        # convert the vocab list to a dict, where each key is a letter of the alphabet
        # and each value is a list of the words that start with that letter
        vocab_dict = {}
        for wd in vocab:
            if wd[0] in vocab_dict:
                vocab_dict[wd[0]].append(wd)
            else:
                vocab_dict[wd[0]] = [wd]
        
        return vocab_dict

    def normalise_jargon(self, text):
        return text.replace(self.replace_map, regex=True)

    def tokenise(self, text):
        """Split a string into individual tokens.

        Parameters:
            - text (str), the text to be tokenised

        Returns:
            - list, with each token as a single element, or None
            (None is returned if s is 'falsy', e.g. None, "")

        Notes:
            - uses NLTK's tokenize package; https://www.nltk.org/api/nltk.tokenize.html
        """
        if text:
            return word_tokenize(text)
        return None

    def remove_stopwords(self, words):
        """Remove any stopwords from a list of words.

        Parameters:
            - words (list), the list of lower-case words to process
            
        Returns:
            - list, with all stopwords removed

        Notes:
            - It is assumed that all words in word_list are lower-case (all stop-words are)
            - The default list of stop-words is provided by NLTK
        """
        if words:
            return [word for word in words if (word not in self.stopwords)]
        else:
            return None

    def correct_lemmatise_word(self, word):
        """Check and (if required) correct spelling of a word, and lemmatise it.

        Parameters:
            - word (str), the word to be checked and lemmatised

        Returns:
            - str, the correct, lemmatised version of the word.

        Notes:
            - Spelling correction uses n-edit distance, and selects the word in the
            vocabulary with the smallest distance to the original.
            - ASSUMES THAT THE *FIRST* LETTER OF 'WORD' IS CORRECT!
            - If 'word' is in the vocab, it will be returned unchanged. This means that
            mis-spellings which are actual words will be missed (e.g. if word='red', when
            it should be 'read', this will *NOT* be corrected).
        """
        suggestion = word
        if (word[0] in self.vocab) and (word not in self.vocab[word[0]]):
            options = [(edit_distance(word, w), w) for w in self.vocab[word[0]]]
            try:
                suggestion = sorted(options, key=lambda val: val[0])[0][1]
            except IndexError as err:
                print(f"{err}. Word: {word}")

        return self.nlp(suggestion)[0].lemma_

    def correct_lemmatise_words(self, words):
        """Convenience function for applying spelling and lemmatisation to a list of words

        Parameters:
            - word (list), list of words to correct (if necessary) and lemmatise

        Returns:
            - list, with each element a corrected and lemmatised word; or [] if
            word_list is 'falsey' (e.g. None, [])

        Notes:
            - uses spaCy's lemmatisation function
        """
        if words:
            return [
                self.correct_lemmatise_word(word) 
                if word not in self.keep_list else word
                for word in words
            ]
        else:
            return []

    def lemmatise_words(self, words):
        """Lemmatise a list of words.

        Parameters:
            - words (list), list of words to lemmatise

        Returns:
            - list, with each element a corrected and lemmatised word; or [] if
            word_list is 'falsey' (e.g. None, [])

        Notes:
            - uses spaCy's lemmatisation function
        """
        if words:
            return [
                self.nlp(wd)[0].lemma_ 
                if wd not in self.keep_list else wd 
                for wd in words
            ]
        else:
            return []

    def process_text(self, text):
         # tokenise the text
        token_list = self.tokenise(text)

        # remove stop-words and punctuation
        no_stop_list = self.remove_stopwords(token_list)

        # correct spelling errors (if req'd); lemmatise words
        if self.check_sp:
            lemmatised_list = self.correct_lemmatise_words(no_stop_list)
        else:
            lemmatised_list = self.lemmatise_words(no_stop_list)

        return lemmatised_list

    def run_processor(self):
        # process the documents
        text = pd.DataFrame(self.df.str.lower())
        text["jargon_replaced"] = self.normalise_jargon(text)
        text["processed_text"] = text.jargon_replaced.apply(self.process_text)

        return text.processed_text


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

def save_processed_text(text, dir, f_name=conf.FILE_NAMES["docs"]):
    if not os.path.isdir(dir):
        os.mkdir(dir)
    
    f_path = os.path.join(dir, f_name)

    try:
        with open(f_path, "w") as f:
            json.dump(text.tolist(), f)
        print(f"Wrote text to {f_path}")
    except TypeError as err:
        print(f"{err}; the data {text} is not JSON-serialisable")
    except FileNotFoundError as err:
        print(f"{err}; the path {f_path} does not exist")

def load_processed_text(dir, f_name=conf.FILE_NAMES["docs"]):
    f_path = os.path.join(dir, f_name)
    try:
        with open(f_path, "r") as f:
            return json.load(f)
    except FileNotFoundError as err:
        print(f"{err}; the file {f_path} does not exist")

def get_processed_text(src, num_rows, run_processor=False):
    dir = os.path.join(src["models"], f"_{num_rows}") if num_rows else src["models"]
    if run_processor:
        df = get_data(src["data"], num_rows=num_rows)
        msg = f"Full dataset: {len(df)} rows"
        msg = f"{msg}. Rows used: {num_rows}" if num_rows else msg
        print(msg)
        tp = TextProcessor(df[src["query_col"]])
        text = tp.run_processor()
        save_processed_text(text, dir=dir)
        return text
    else:
        return pd.Series(load_processed_text(dir=dir))


# =====================================================================================
# Drivers
# =====================================================================================
# command-line options
@click.command()
@click.option("-p", "--process", default=False, show_default=True, type=bool,
    help="Whether to process the corpus (often takes a long time)")
@click.option("-f", "--src_file", default="cg_enquiries.json", show_default=True, type=str,
    help="The source file to use as input")
@click.option("--cut", default=None, show_default=True, type=int,
    help="The number of rows to include in the sample. 'None'=all rows")
def main(process, src_file, cut):

    start = time.time()
    conf.DATA_SOURCE["data"] = os.path.join(conf.DATA_SOURCE["data"], src_file)
    txt = get_processed_text(conf.DATA_SOURCE, num_rows=cut, 
                            run_processor=process)
    end = time.time()
    print(f"Text processing COMPLETE. Time: {end - start:.1f}")
    print(f"Processed text: \n{txt.head()}")

if __name__ == "__main__":
    main()