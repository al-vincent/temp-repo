"""
Name: topic_classifier_train.py

Description: script to train a series of multiclass-multioutput models, across a range
    of hyperparameter values for each model, using k-fold cross-validation. The 'best'
    versions of each model are then run against a hold-out test set, and the overall
    best model (i.e. the one with the highest score against the test set) is persisted.

    Consists of a ModelTrain class that can be re-used more widely if needed, together
    with a 'main' function that demonstrates the use of the class and allows it to be
    run from the CLI.

Known issues:
    - Some of the models used take quite a long time to run across the range of
        parameters (e.g. Random Forests, Extra Trees). However, most run in a few
        seconds.
    - Scikit-learn doesn't include any out-of-the-box metrics for assessing multiclass-
        multioutput models. For this use case, the multiclass f1 score metric has been
        adapted for the multioutput context, averaged across the labels. However, this
        averaging will conceal variance between different outputs.

How to run: the functionality can be called in two ways:
    - Importing the main class and calling the run_trainer method, or;
    - As a script via the CLI, using the command
        $ python topic_classifier_train.py
"""


# -------------------------------------------------------------------------------------
# Import libraries
# -------------------------------------------------------------------------------------
# Standard library
from datetime import datetime
import logging
import os

# External packages
import pandas as pd
from sklearn.model_selection import GridSearchCV

# Modules imported from the repo
import utils as ut
import settings as s
import topic_classifier_processing as tcp


# -------------------------------------------------------------------------------------
# Set up logger
# -------------------------------------------------------------------------------------
log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_fmt)
logger = logging.getLogger(__name__)


# -------------------------------------------------------------------------------------
# Model training class
# -------------------------------------------------------------------------------------
class ModelTrain:
    """Main class to train and assess the different models.

    Parameters:
        - data (tuple), the train and test features and labels. Unpacks to X_train,
            X_test, Y_train, Y_test (where each item is a numpy array)
        - model_params (list), where each item is a dict containing:
            - the model object to run, and;
            - the models and hyperparameters to use for grid search.
            Format used is:
                [
                    {
                        "model": RandomForestClassifier(),
                        "params": {
                            "estimator__n_estimators": [250, 500, 1000],
                            "estimator__max_features": [None, "sqrt", "log2"],
                            ...etc.
                        },
                        "scorer": "roc_auc",
                        "test_scorer": roc_auc_score
                    },
                    {
                        "model": KNeighborsClassifier(algorithm="brute"),
                        "params": {
                            "estimator__n_neighbors": [2, 3, 4, 5],
                            ... etc.
                        },
                        "scorer": "roc_auc",
                        "test_scorer": roc_auc_score
                    },
                    ...etc.
                ]
        - model_dir (str), the path to the directory where the TF-IDF transformer will
            be stored
        - model_name (str or None, optional), the filename for the saved model (without
            a file extension)
        - save_model (bool, optional), flag to indicate whether the model should be
            persisted. Default True (set to False for testing)
    """

    def __init__(
        self,
        data,
        model_params,
        model_dir,
        model_name=None,
        save_model=True,
    ):
        self.data = data
        self.model_params = model_params
        self.model_name = self._get_model_name(model_name)
        self.model_path = os.path.join(model_dir, self.model_name)
        self.save_model = save_model

    def _get_model_name(self, model_name):
        """Private method to generate a default name for the TF-IDF model file. If a
        model name as been provided, this is retained; otherwise, a name is auto-
        generated from the current timestamp, in the format:
            'YYYY-mm-ddTHH:MM:SS-topic_class_model'; e.g.
            2022-07-19T08:30:12-topic_class_model

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
            return f"{now.strftime('%Y-%m-%dT%H:%M:%S')}-topic_class_model"

    def train_single_model(self, model, params, data, scorer, test_scorer):
        """Train a single model across a range of parameters using grid search, to find
        the best combination of hyperparameter values.

        The initial 'best' model is chosen using k-fold cross validation on the training
        data *only*. This model is then run against the (unseen) test data.

        Parameters:
            - model (scikit-learn model object), the model to train
            - params (dict), the model hyperparameters to search across. Format:
                {
                    "estimator__<param_1>": [values, to, search],
                    "estimator__<param_2>": [values, to, search],
                    ...etc.
                }
                E.g. (for KNeighborsClassifier):
                {
                    "estimator__n_neighbors": [2, 3, 4, 5],
                    "estimator__p": [1, 2],
                    ...etc.
                }
            - data (tuple), the train and test features and labels. Unpacks to X_train,
                X_test, Y_train, Y_test (where each item is a numpy array)
            - scorer (callable), the method to use for scoring the models

        Returns:
            - dict, format {"model": <model object>, "score": <float>}, containing the
                model that achieved the best score on the test data
        """
        # Unpack the test and training data
        X_train, X_test, Y_train, Y_test = data
        logger.info(f"Model: {model}")

        # Create the Classifier object and set up the grid search
        grid_search = GridSearchCV(model, params, n_jobs=-1, verbose=1, scoring=scorer)

        # Run grid search across the range of parameters and log the results. Run the
        # best model against the hold-out test data set
        t0 = datetime.now()
        try:
            grid_search.fit(X_train, Y_train)
        except Exception as err:
            logger.warning(f"Exception in model_training: {err}")
            return {"model": None, "score": -1.0}
        else:
            logger.info(f"Time taken: {(datetime.now() - t0).total_seconds():.3f}s \n")
            logger.info(f"Best training score: {grid_search.best_score_:.3f}")
            logger.info(f"Best parameters set: {grid_search.best_params_}")
            test_score = test_scorer(
                y_true=Y_test, y_pred=grid_search.best_estimator_.predict(X_test)
            )
            logger.info(f"Score on test set: {test_score}\n\n---\n")
            return {"model": grid_search.best_estimator_, "score": test_score}

    def train_all_models(self, data, model_settings):
        """Train all models in model_settings using grid search to find a good parameter
        set. Then compare each optimal model against the hold-out test set, to select
        the overall best model.

        Parameters:
            - data (tuple), the train and test features and labels. Unpacks to X_train,
                X_test, Y_train, Y_test (where each item is a numpy array)
            - model_settings (list), the models and hyperparameters to use for grid
            search. Format used is:
                [
                    {
                        "model": RandomForestClassifier(),
                        "params": {
                            "estimator__n_estimators": [250, 500, 1000],
                            "estimator__max_features": [None, "sqrt", "log2"],
                            ...etc.
                        },
                        "scorer": "roc_auc",
                        "test_scorer": roc_auc_score
                    },
                    {
                        "model": KNeighborsClassifier(algorithm="brute"),
                        "params": {
                            "estimator__n_neighbors": [2, 3, 4, 5],
                            ... etc.
                        },
                        "scorer": "roc_auc",
                        "test_scorer": roc_auc_score
                    },
                    ...etc.
                ]

        Returns:
            - dict, in format {"model": <trained model object>, "score": <float>},
                containing the overall best model.
        """
        logger.info("Training models")

        # Iterate through the models, running grid search on each. If the model score is
        # higher than the current best score, replace 'best' with the new model & score
        best = {"model": None, "score": -1.0}
        for m_s in model_settings:
            mod = self.train_single_model(
                model=m_s["model"],
                params=m_s["params"],
                data=data,
                scorer=m_s["scorer"],
                test_scorer=m_s["test_scorer"],
            )
            if (mod is not None) and (mod["score"] > best["score"]):
                logging.info(
                    f"New best model: {mod['model']}." f"Test score: {mod['score']}"
                )
                best = mod

        if best["model"] is not None:
            return best
        else:
            logging.warning("No models were successfully trained")

    def save_model_to_repo(self, model, model_name):
        """Save the new model for later use.

        Parameters:
            - model (sklearn model object), the trained model to be saved.
            - model_name (str), the name to use when saving (*without* a file extension)
        """
        try:
            ut.persist_model(model, self.model_path)
            logger.info(f"Model {model} saved as {model_name}.")
        except Exception as err:
            logger.error(f"{err}")

    def run_trainer(self):
        """Convenience function to run the model training and save the best model.

        Returns:
            - dict, in format {"model": <trained model object>, "score": <float>},
                containing the overall best model.
        """
        best_model = self.train_all_models(self.data, self.model_params)
        if self.save_model:
            self.save_model_to_repo(best_model["model"], self.model_name)
        return best_model


# -------------------------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------------------------
def get_data():
    """Load and pre-process the enquiries that the models will be trained on.

    Returns:
        - tuple containing 4 x numpy arrays, one for each of X_train, X_test,
                Y_train, Y_test
    """
    df = pd.read_csv(s.RAW_DATA_PATH)
    pt = tcp.PrepareText(
        df=df,
        text_col=s.TEXT_COL,
        label_cols=s.LABEL_COL,
        max_features=s.MAX_FEATURES,
        model_dir=s.MODEL_PATH,
        model_name="features.pkl",
        save_model=True,
    )
    return pt.run_text_prep()


# -------------------------------------------------------------------------------------
# Drivers
# -------------------------------------------------------------------------------------
def main():
    """Driver function to demonstrate how the class should be used (and to run it as a
    script).
    """
    data = get_data()
    model_settings = s.MODEL_SETTINGS
    mt = ModelTrain(
        data=data,
        model_params=model_settings,
        model_dir=s.MODEL_PATH,
        model_name="model.pkl",
        save_model=True,
    )
    best_model = mt.run_trainer()


if __name__ == "__main__":
    main()
