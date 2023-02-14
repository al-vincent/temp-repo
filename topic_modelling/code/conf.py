"""
Config and settings file for topic_modelling.py

Contains:
- File names and paths;
- Database conn strings and field names;
- Regex patterns;
- CDN URLs (for pyLDAvis);
- Data Workspace URLs;
- Graph labels;
- Other constant values

All these values are considered to be constants, so UPPER_CASE is used for var names.
"""

import os

CODE_DIR = os.path.abspath(os.path.dirname(__file__))

DATA_SOURCE = {
    "data": os.path.join(CODE_DIR, "..", "data"),
    "query_col": "query",
    "models": os.path.join(CODE_DIR, "..", "models"),
    "vis": os.path.join(CODE_DIR, "..", "visualisation")
}

EXTRA_STOP_WORDS = [
    "uk",
    "business",
    "businesses",
    "company",
    "growth",
    "gateway",
    "dear",
    "sir",
    "madam",
    "sincerely",
    "thank",
    "export",
    "exporting",
    "exports",
    "exporter",
    "exporters",
    "exported"
]

FILE_NAMES = {
    "cv_plt": "coherence.png",
    "corpus": "corpus.pkl",
    "models_cvs": "models_coherence.pkl",
    "dict": "dict",
    "docs": "docs.json",
    "lda": "lda",
    "lda_vis": "lda_vis",
}

LDA_VIS = {
    "cdn": "https://cdn.jsdelivr.net/gh/bmabey/pyLDAvis@3.3.1/pyLDAvis/js/",
    "lib": os.path.join("/src", "libs"),
    "pyldavis_css": "ldavis.v1.0.0.css",
    "pyldavis_js": "ldavis.v3.0.0.js",
    "d3_js": "d3.v5.js",
}

NLTK = {
    "url": "https://s3-eu-west-2.amazonaws.com/mirrors.notebook.uktrade.io/nltk/index.xml",
    "resources": ["words", "punkt", "stopwords"]
    }

REPLACE_MAP = {
    "growthgateway": "growth gateway",
    "sir/madam": "sir / madam",
    r"(\dk)|(\d{1,4}million)|(£\d{1,4})|(€\d{1,4})": "MONEY",
    r"(\d{1,2}(/|\.)\d{1,2}(/|\.)\d{2})|(\d{1,2}(st|nd|rd|th){1})": "DATE",
    (
        r"((http|ftp|https):\/\/)*([\w\-_]+(?:(?:\.[\w\-_]+)+))"
        r"([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?"
    ): "URL",
    r"(?<=\s)(\d{4})(?=\s)": "NUM_4_DIGITS",
    r"(?<=\s)(\d{2})(?=\s)": "NUM_2_DIGITS",
    r"(?<=\s)(\d{3}|\d{5,20})(?=\s)": "NUM_OTHER",
    r"[^\w\s\d]": "",
}

KEEP_LIST = list(set(["lc", "ita"] + list(REPLACE_MAP.values())))
KEEP_LIST.remove("")

SEED = 42
