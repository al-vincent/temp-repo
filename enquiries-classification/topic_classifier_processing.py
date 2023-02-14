"""
Name: topic_classifier_processing.py

Description: pre-processes text for the topic classifier. Includes the following steps:
    - Running a 'standard' set of NLP processing techniques, including removing stop-
        words and punctuation; tokenisation; lemmatisation
    - Splitting the text and labels into train and test data sets
    - Applying a TF-IDF vectoriser to the text training data, and persisting it in
        the repo

Known issues: none

How to run: the functionality can be called in two ways:
    - Importing the main class and calling the run_text_prep method, or;
    - As a script via the CLI, using the command
        $ python topic_classifier_processing.py

Notes:
    - The TF-IDF vectoriser is run on the training text *only*. This is to prevent data
        leakage, from either the test data set or the wider corpus. However, given the
        relatively small training data set, and the comparitively large number of labels
        and classes, this is likely to limit the model's effectiveness.
    - The TF-IDF vectoriser has been limited to 1000 features. This was originally done
        to avoid constraints on Data Workspace; however, the pipeline design has
        changed somewhat, and more features could be introduced (potentially leading to
        a more effective model).
"""


# -------------------------------------------------------------------------------------
# Import libraries
# -------------------------------------------------------------------------------------
# Standard library modules
from datetime import datetime
import logging
import os

# External libraries
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

# Imports from within repo
import nlp_processing_base as npb
import settings as s
import utils as ut


# -------------------------------------------------------------------------------------
# Set up logger
# -------------------------------------------------------------------------------------
log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_fmt)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------------------
# Processor class
# -------------------------------------------------------------------------------------
class PrepareText:
    """Pre-process text, and generate / persist TF-IDF feature matrix for all enquiries
    in the master dataset.

    Parameters
        - df (Pandas DataFrame), the master Live Services enquiries dataset (passed
            through the default text cleaning process)
        - text_col (str), the name of the column containing the enquiry text
        - label_cols (list), the names of the columns that contain labels
        - max_features (int), upper bound for the number of TF-IDF features to calculate
        - model_dir (str), the path to the directory where the TF-IDF transformer will
            be stored
        - model_name (str, optional), the name to use for the TF-IDF feature model. If
            not provided, a default name will automatically be generated using the
            current timestamp.
        - save_model (bool, optional), flag to indicate whether the TF-IDF transformer
            should be persisted. Default True (set to False for testing)
    """

    def __init__(
        self,
        df,
        text_col,
        label_cols,
        max_features,
        model_dir,
        model_name=None,
        save_model=True,
    ):
        self.df = df
        self.text_col = text_col
        self.label_cols = label_cols
        self.max_features = max_features
        self.model_name = self._get_model_name(model_name)
        self.model_path = os.path.join(model_dir,self.model_name)
        self.save_model = save_model

    def _get_model_name(self, model_name):
        """Private method to generate a default name for the TF-IDF model file. If a
        model name as been provided, this is retained; otherwise, a name is auto-
        generated from the current timestamp, in the format:
            'YYYY-mm-ddTHH:MM:SS-tf_idf_features'; e.g.
            2022-07-19T08:30:12-tf_idf_features

        Parameters:
            - model_name (str or None), the model name provided when the constructor
                was called. Defaults to None, in which case a name is auto-generated.

        Returns:
            - str, the name of the model file.
        """
        if model_name is not None:
            return model_name
        else:
            now = datetime.now()
            return f"{now.strftime('%Y-%m-%dT%H:%M:%S')}-tf_idf_features.pkl"

    def process_text(self, text_ser):
        """Pre-process the enquiries for NLP-type applications (remove stopwords,
        tokenisation, lemmatisation etc).

        Parameters:
            - text_ser (Pandas Series), the corpus of enquiries to be processed. Each
                row is an enquiry, and each enquiry is a string.

        Returns:
            - Pandas Series containing the processed strings. Each row is an enquiry,
                and each enquiry is a string (i.e. *not* a list of tokens).
        """
        proc = npb.NlpProcessingBase(text_ser, s.NLTK_PACKAGES)
        return proc.run_processor()

    def split_data_and_get_features(self, df, text_col, label_cols, test_size=0.3):
        """Split the master dataset into train and test sets for the features and
        labels, calculate the TF-IDF feature model, and persist it to the repo
        (auto-archiving any existing models).

        Parameters:
            - df (Pandas DataFrame), the data to be split
            - text_col (str), the name of the column that contains the enquiries
            - label_cols (list), the names of the columns that contain the labels
            - test_size (float, optional), the proportion of the dataset to use for
                the hold-out test set.

        Returns:
            - tuple containing 4 x numpy arrays, one for each of X_train, X_test,
                Y_train, Y_test
        """
        # Get the data and split into test / train sets
        X = df[text_col].astype(str)
        Y = df[label_cols].astype(str)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=test_size)

        # Generate the features and save the feture object (for testing, prediction)
        tf_idf = self.generate_features(X_train)
        if self.save_model:
            ut.persist_model(tf_idf, self.model_path)

        # Transform the test inputs to use the same TF-IDF vectors as the training data
        X_train = tf_idf.transform(X_train)
        X_test = tf_idf.transform(X_test)
        logger.info(
            f"Feature matrices created. X_train shape: {X_train.shape}, "
            f"X_test shape: {X_test.shape}, Y_train shape: {Y_train.shape},"
            f"Y_test shape: {Y_test.shape}"
        )

        return X_train, X_test, np.array(Y_train), np.array(Y_test)

    def generate_features(self, X_train):
        """Generate the Term Frequency-Inverse Document Frequency (TF-IDF) scores for
        the corpus of enquiries.

        Parameters:
            - X_train (Pandas Series), the enquiries to be processed. Each row is an
                enquiry, and each enquiry is a string.

        Returns:
            - TfidfVectoriser object that has been fitted to the training data
        """
        # Convert the X vectors to tf-idf vectors
        tf_idf = TfidfVectorizer(max_features=self.max_features)
        return tf_idf.fit(X_train)

    def run_text_prep(self):
        """Convenience method that implements each step in the pipeline.

        Returns:
            - tuple containing 4 x numpy arrays, one for each of X_train, X_test,
                Y_train, Y_test
        """
        # Process the text to remove stop-words, tokenise, lemmatise etc.
        self.df[self.text_col] = np.where(
            self.df[self.text_col].notnull(),
            self.process_text(self.df[self.text_col].astype(str)),
            None,
        )

        # Keep only rows where the processed text is not NA (i.e. NaN, None etc.)
        self.df = self.df[self.df[self.text_col].notnull()]

        # Generate the TF-IDF feature set, and test / train data
        return self.split_data_and_get_features(self.df, self.text_col, self.label_cols)


# -------------------------------------------------------------------------------------
# Drivers
# -------------------------------------------------------------------------------------
def main():
    """Driver function to run the script from the CLI"""
    df = pd.read_csv(s.RAW_DATA_PATH)
    pt = PrepareText(
        df=df,
        text_col=s.TEXT_COL,
        label_cols=s.LABEL_COL,
        max_features=s.MAX_FEATURES,
        model_dir=s.MODEL_PATH,
        model_name="features.pkl",
        save_model=True,
    )
    X_train, X_test, Y_train, Y_test = pt.run_text_prep()


if __name__ == "__main__":
    main()
