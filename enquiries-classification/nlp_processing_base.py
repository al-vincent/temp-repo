"""
Description: a class / script that contains a series of text pre-processing methods,
    commonly used in NLP applications. Users can select the methods that are relevant
    to their project. Includes methods for:
        - Setting up NLTK resources by downloading from Data Workspace
        - Converting text to lower case
        - Removing stop words
        - Removing punctuation
        - Tokenising sentences to word tokens
        - Lemmatising words, using Part-of-Speech tagging
        - Joining tokens back into 'sentences'

Dependencies:
    - Uses a 'settings' dict for downloading NLTK resources (more information below).

Points to note:
    - Where possible, methods are implemented in a vectorised manner; however, in some
      cases it has been necessary to use .apply()
    - The order in which some of the methods are run may change the output in some
      cases. The user must consider the appropriate running order for their use case.
    - The processor is currently implemented as a class. However, it may be easier to
      use (and more consistent with existing cookie-cutter utils) as a series of
      functions.

How to run: the class can be imported to other modules, or called standalone via the
    CLI. To run from the CLI, use:
    $ python nlp_processing_base.py

    NOTE: this will run ALL the methods in the class.
"""


# -------------------------------------------------------------------------------------
# Import libraries
# -------------------------------------------------------------------------------------
# Standard library modules
import logging

# Third-party packages / modules
import nltk
import pandas as pd
from nltk.corpus import stopwords, wordnet
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Internal repo modules
import settings as s


# -------------------------------------------------------------------------------------
# Set up logger
# -------------------------------------------------------------------------------------
log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_fmt)
logger = logging.getLogger(__name__)


# -------------------------------------------------------------------------------------
# NLP processing class
# -------------------------------------------------------------------------------------
class NlpProcessingBase:
    """Pre-process text for use in NLP-type applications.

    Parameters:
        - text_ser (Pandas Series object), a Series where each cell contains text
            to be individually processed.
        - nltk_packages (list), NLTK packages to download. Example
                [
                    "stopwords",
                    "punkt",
                    "wordnet",
                    "omw-1.4",
                    "averaged_perceptron_tagger",
                ],
            }
            NOTE: the resources shown here are required to implement all methods
            in the class.
        - stop_words (list, optional), common words that should be stripped from
            the text. Default is the list of English-language stopwords in NLTK.
    """

    def __init__(
        self, text_ser, nltk_packages, stop_words=stopwords.words("english"), quiet=True
    ):
        self.text_ser = text_ser
        self.nltk_packages = nltk_packages
        self.setup(quiet)
        self.stop_words = stop_words

    def setup(self, quiet):
        """Download the NLTK resources required from Data Workspace mirror"""
        logger.info("Running setup...")

        for n_p in self.nltk_packages:
            nltk.download(n_p, quiet=quiet)

    def remove_stop_words_and_set_case(self, text_ser, pattern=r"\b(?:{})\b"):
        """Remove all stopwords and convert text to lower case.

        Parameters:
            - text_ser (Pandas Series object), a Series where each cell contains text
                to be individually processed.
            - pattern (str, optional), a regex pattern to join all the stopwords into
                a single regex string, as a series of words with the 'or' separator

        Returns:
            - Pandas Series object, with each cell containing the processed text
        """
        logger.info("Removing stopwords and setting to lower case...")
        stop_str = pattern.format("|".join(self.stop_words))
        return text_ser.str.replace(stop_str, "", regex=True).str.lower()

    def remove_punctuation(self, text_ser, pattern=r"[^\w\s]"):
        """Remove all punctuation from each text cell.

        Parameters:
            - text_ser (Pandas Series object), a Series where each cell contains text
                to be individually processed.
            - pattern (str, optional), a regex pattern to remove any characters other
                than alphanumeric, underscores and whitespace

        Returns:
            - Pandas Series object, with each cell containing the processed text

        NOTE: this method will leave underscore characters *in* the text. If these
        characters are not desired, the pattern should be changed to r'[^\\w\\s]|[_]'
        (with single backslashes)
        """
        logger.info("Removing punctuation...")
        return text_ser.str.replace(pattern, "", regex=True)

    def tokenise_ser(self, text_ser):
        """Tokenise each text cell in a series, using the punkt tokeniser.

        Parameters:
            - text_ser (Pandas Series object), a Series where each cell contains text
                to be individually processed.

        Returns:
            - Pandas Series object, where each cell contains a list of tokens.
        """
        logger.info("Tokenising the text...")
        return text_ser.apply(word_tokenize)

    def _get_wordnet_pos_tag(self, tag):
        """Private method to convert NLTK Part-of-Speech (PoS) tags to their WordNet
        equivalents.

        Parameters:
            - tag (str), the NLTK PoS tag

        Returns:
            - str, the equivalent WordNet PoS tag

        NOTE: this may seem like a clunky way to convert, since both of the tags are
        'within' NLTK already.
        """
        if tag.startswith("J"):
            return wordnet.ADJ
        elif tag.startswith("V"):
            return wordnet.VERB
        elif tag.startswith("N"):
            return wordnet.NOUN
        elif tag.startswith("R"):
            return wordnet.ADV
        else:
            # the default tag for the lemmatiser is a noun, so return that if nothing
            # else fits
            return wordnet.NOUN

    def _lemmatise_tokens(self, tokens):
        """Private method that lemmatises tokens using their Part-of-Speech tags.

        Parameters:
            - tokens (list), a series of tokens to be lemmatised

        Returns:
            - list of lemmas for the original token

        NOTE: using PoS tags provides a more accurate lemma.
        """
        wnl = WordNetLemmatizer()
        if tokens:
            nltk_tags = nltk.pos_tag(tokens)
            return [
                wnl.lemmatize(token, pos=self._get_wordnet_pos_tag(tag))
                for token, tag in nltk_tags
            ]

    def lemmatise_ser(self, text_ser):
        """Lemmatise each text cell in a Series, using Part-of-Speech tags for more
        accurate lemmas.

        Parameters:
            - text_ser (Pandas Series object), a Series where each cell contains a list
                of tokens to be lemmatised.

        Returns:
            - Pandas Series object, where each cell contains a list of lemmas of the
            original tokens.
        """
        logger.info("Lemmatising the text...")
        return text_ser.apply(self._lemmatise_tokens)

    def join_tokens(self, text_ser):
        """Join lists-of-tokens into sentences (format required for TF-IDF
        vectorisation).

        Parameters:
            - text_ser (Pandas Series object), a Series where each cell contains a list
                of tokens.

        Returns:
            - Pandas Series object, where each cell contains a string of joined tokens
                separated by a single space.
        """
        logger.info("Converting tokens to sentences...")
        return text_ser.str.join(sep=" ")

    def run_processor(self):
        """Run all methods in the NLP pipeline in order.

        Returns:
            - Pandas Series object, where each cell contains a string of processed text
        """
        logger.info("Running NLP pipeline")
        result = (
            self.text_ser.pipe(self.remove_stop_words_and_set_case)
            .pipe(self.remove_punctuation)
            .pipe(self.tokenise_ser)
            .pipe(self.lemmatise_ser)
            .pipe(self.join_tokens)
        )
        logger.info("...Done!")
        return result


# -------------------------------------------------------------------------------------
# Drivers
# -------------------------------------------------------------------------------------
def main():
    """Driver function to demonstrate use of the pipeline.

    Reads data in, applies the cleaning methods, displays the original and processed
    versions of each cell in the terminal.
    """
    
    logger.info("Reading data...")
    df = pd.read_csv(s.RAW_DATA_PATH)

    npb = NlpProcessingBase(
        text_ser=df[s.TEXT_COL].astype(str), nltk_packages=s.NLTK_PACKAGES
    )
    processed = npb.run_processor()
    output = pd.DataFrame({"original": df[s.TEXT_COL], "processed": processed})
    logger.info(f"\nOutput of cleaning: \n{output.head()}\n")


if __name__ == "__main__": 
    main()
