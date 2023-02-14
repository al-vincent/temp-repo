# -------------------------------------------------------------------------------------
# Import libraries
# -------------------------------------------------------------------------------------
import os

from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score


# -------------------------------------------------------------------------------------
# SETTINGS
# -------------------------------------------------------------------------------------
# NLTK packages used by the text processor
NLTK_PACKAGES = [
    "punkt",
    "stopwords",
    "wordnet",
    "omw-1.4",
    "averaged_perceptron_tagger",
]


# Data file path
RAW_DATA_PATH = os.path.join(
    "data", 
    "activity_fields_and_leak_discovery_date_time_utf8.csv"
)


# Directory containing all the model
MODEL_PATH = "models"


# Relevant columns in the raw data
TEXT_COL = "OrderCmnt"
LABEL_COL = "LeakCauseCd"


# Constant to set the max number of TF-IDF features
MAX_FEATURES = 2000


# Models and settings to use with the GridSearch experiments
MODEL_SETTINGS = [
    # {
    #     "model": RandomForestClassifier(),
    #     "params": {
    #         "n_estimators": [250, 500, 1000],
    #         "max_features": [None, "sqrt", "log2"],
    #     },
    #     "scorer": "accuracy",
    #     "test_scorer": accuracy_score
    # },
    {
        "model": KNeighborsClassifier(algorithm="brute"),
        "params": {
            "n_neighbors": [2, 3, 4, 5],
        },
        "scorer": "accuracy",
        "test_scorer": accuracy_score
    },
    {
        "model": MLPClassifier(max_iter=2000),
        "params": {
            "learning_rate": ["constant", "adaptive"],
            "hidden_layer_sizes": [50, 100, 250],
        },
        "scorer": "accuracy",
        "test_scorer": accuracy_score
    }
]