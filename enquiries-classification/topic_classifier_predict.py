"""
Name: topic_classifier_predict.py

Description: calculate predicted topics for enquiries, based on the TF-IDF scores of
             the text. Return a DataFrame containing the scores.

Known issues: none

How to run: can either be run as a script from the CLI, or called as a function.
    - To run as a script; in the terminal, run:
        $ python topic_classifier_predict.py
    - To call from another function; use the 'predict' function, taking the lines in
        main() as a template.

Notes:
    - Relies heavily on other scripts in the repo (see the imports for details)
"""


# -------------------------------------------------------------------------------------
# Import libraries
# -------------------------------------------------------------------------------------
# Standard library modules
import logging
import os

# Third-party libraries
import pandas as pd

# Modules within the repo
import utils as ut
import settings as s
import nlp_processing_base as npb


# -------------------------------------------------------------------------------------
# Set up logger
# -------------------------------------------------------------------------------------
logger = logging.getLogger(__name__)


# -------------------------------------------------------------------------------------
# Prediction functions
# -------------------------------------------------------------------------------------
def process_text(text_ser):
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


def get_model_name(pattern, path=s.MODEL_PATH):
    """Retrieve the correct 'model-like' data from the repo.

    Parameters:
        - pattern (str), an identifier to describe the filename required, based on the
            last n characters of the filename. To retrieve:
                - TF-IDF feature model, use 'feature.pkl'
                - Classifier model, use 'model.pkl'
        - path (str, optional), the directory where the files are stored.

    Returns:
        - str, the filename matching the pattern (if it exists)

    Raises:
        - FileNotFoudError, if no files matching the 'pattern' are found in 'path'
    """
    # Get all files in 'path' where the last n chars of the filename match 'pattern'
    # (Should be a list of length 1)
    model_files = [
        f
        for f in os.listdir(path)
        if (os.path.isfile(os.path.join(path, f)) and f[-len(pattern) :] == pattern)
    ]

    # If no matching files are found, raise FileNotFoundError
    if not model_files:
        raise FileNotFoundError(
            f"No models found in {path}." f"Files found: {os.listdir(path)}"
        )

    # If more than one file is found, log a warning
    if len(model_files) > 1:
        logger.warn(f"more than one model file in {path}. Model files: {model_files}")

    # Return the first item in the list, excluding the last 4 chars (i.e. '.pkl')
    return model_files[0][:-4]


def predict(
    df,
    text_col,
    id_col,
    features_pattern="features.pkl",
    features_path=s.MODEL_PATH,
    model_pattern="model.pkl",
    model_path=s.MODEL_PATH,
    label_cols=s.LABEL_COLS,
):
    """Run the classifier against a matrix of enquiries data.

    Parameters:
        - df(Pandas DataFrame), containing (at-minimum) columns with the enquiries text
            and the Zendesk enquiry IDs
        - text_col (str), the name of the column containing the enquiry text
        - id_col (str), the name of the column containing the Zendesk ids
        - features_pattern (str, optional), last n characters of the TF-IDF transformer
            filename
        - features_path (str, optional), directory in repo where the TF-IDF transfomer
            file should be read from
        - model_pattern (str, optional), last n characters of the classifier model
            filename
        - model_path (str, optional), directory in repo where the classifier model
            file should be read from

    Returns:
        - Pandas DataFrame containing the Zendesk IDs and the scores [0,3] for each
            of the topics (/ Strategic Priorities)

    NOTE:
        - Any enquiries where the processed text is an empty string (e.g. consist only
            of stop words) will be assigned NaN values in the returned DataFrame.
    """
    # Apply the standard cleaning processes to the text (i.e. tokenise, lemmatise etc.)
    logger.info("Cleaning text...")
    df[text_col] = process_text(df[text_col])

    # Drop all rows where the input text is None (i.e. there's no description)
    # [These will cause the predictions to fail]
    no_null_df = df[df[text_col].notnull()]
    text_ser = no_null_df[text_col]
    id_ser = no_null_df[id_col]

    # Get the TF-IDF Vectoriser object used to encode the text, and transform the
    # new enquiries
    logger.info("Loading TF-IDF and encoding enquiries...")
    f_name = get_model_name(features_pattern, path=features_path)
    tf_idf = ut.load_model(os.path.join(features_path, f_name))
    X = tf_idf.transform(text_ser)

    logger.info("Loading trained model...")
    model_name = get_model_name(model_pattern, path=model_path)
    model = ut.load_model(os.path.join(model_path, model_name))

    # Calculate the model predictions for the enquiries
    logger.info("Computing predictions...")
    results_array = model.predict(X)
    # Combine the results values with IDs, and convert into a DataFrame
    results_df = pd.concat(
        [
            id_ser.reset_index(drop=True),
            pd.DataFrame(data=results_array, columns=label_cols),
        ],
        axis=1,
    )

    # Join the results df with the original IDs, to include the enquiries which have
    # no processed description text
    return results_df.merge(df[id_col], how="right", on="id")


# -------------------------------------------------------------------------------------
# Drivers
# -------------------------------------------------------------------------------------
def main():
    """Driver function to illustrate how the prediction should be used."""
    df = pd.read_csv(s.RAW_DATA_PATH)
    df = df[[s.TEXT_COL, s.ID_COL]]
    results = predict(
        df,
        s.TEXT_COL,
        s.ID_COL,
        features_path=s.MODEL_PATH,
        model_path=s.MODEL_PATH,
        label_cols=s.LABEL_COLS,
    )
    print(results)


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
