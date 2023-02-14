# Topic Classifier
These files provide a simple pipeline for classification tasks, using raw text as the
feature set (via TF-IDF vectorisation of the training documents). It's been designed to 
work on a series of different classification problems, with minimal changes required; e.g. 
the same framework _should_ work for binary classification, multiclass, multi-output, and 
multiclass-multioutput problems (**note:** has not been tested on multi-output problems).

The original use-case was to categorise user enquiries (e.g. provided via a simple 
online form) for automatic triage, saving time for a human operator. If your use-case is
substantially different to this, then the approach may not work well.

**In particular:** if your text documents are short (e.g. less than ~20 words), then the
approach is **unlikely to work well**.

## How does it work?
The process uses the following high-level steps:
1. Basic text processing steps are applied (more detail below) - `nlp_processing_base.py`
2. Documents are split into train and test sets, and converted to TF-IDF vectors - `topic_classifier_processing.py`
3. A series of classifier models are trained on the vectors, and the best one taken forward - `topic_classifier.train.py`
4. New examples are provided to the trained model, and predicted labels assigned - `topic_classifier_predict.py`

## Warnings!
- There are currently **no unit tests** for this code; use at own risk!
- The code has been used fairly extensively for a DIT project, and works well in that
context. Your mileage may vary in other projects.
- Applying the grid search may take a long time, especially if lots of settings are 
being used. However, it's probably better to accept this and plan for it, than to have a
search-breadth that's too narrow.
    - Additionally; some models are _much_ faster than others. In particular, ensemble 
    methods are slow to run (though their performance is often very good).
- Some of the steps could be shortcutted; e.g. unless the NLP pre-processing steps change,
the output from these steps could (probably should) be persisted in a new file, rather than
repeating pre-processing every time.

---

## Files

### `environment.yml`
A conda environment file, that contains the full dev environment (python version, all 
dependencies etc.)


### `settings.py`
Contains a series of constant values / file paths / other settings that are used by the
other files (for a more DRY design).


### `utils.py`
A series of utility functions, for use across other files. Currently only contains functions
for model serialisation and de-serialisation.


### `nlp_processing_base.py`
This file contains a class and methods that apply a series of common NLP-type transforms
to the raw input text. Wherever possible, these transforms use Pandas' native vectorised 
methods; however, a few of them use `apply`. 

Transforms include:  
- Conversion to lower case
- Remove stop-words
- Remove punctuation
- Word tokenistion
- Lemmatisation, using Part-of-Speech tagging for better results


### `topic_classifier_processing.py`
This file contains a class and methods to run the classifier pre-processing steps:
1. Split the input text labels into train and test sets (with a 70/30 split)
2. Run the text through the NLP processor (above)
3. Apply a TF-IDF vectoriser to the processed text
4. Serialise and save the vectoriser object (in `./models/features.pkl`)
5. Return a tuple containing X_train, X_test, Y_train, Y_test


### `topic_classifier_train.py`
This file contains a class and methods to run the model training.

A series of models are trained across a range of hyperparameters, using Grid Search. This
consists of two steps:
1. The best individual model and parameter set (i.e. the one that optimises the scoring metric chosen) for each model is selected, using 5-fold cross validation on the training data _only_.
2. The overall single best model is then selected using the test data.

E.g. the output of step 1 is the best model and parameter set for _each model examined_; 
if Random Forests, K Nearest Neighbours and MLP are all included, each with several parameters,
then 3 models are returned (one Random Forest, one KNN, and one MLP).

The output of step 2 is the model and params that performs best when run against the hold-out test data; this model is then persisted (in `./models/model.pkl`) and used for prediction.

Models and parameter options are set in `settings.py`. The current set is very basic, just to illustrate how the process works; however, adding more models, hyperparameters and options is 
straightforward.

**Notes:**
- Currently, the scoring metric used is accuracy. This is not a good metric if the dataset
is unbalanced; in this context, something like f1 score is probably better.
- Grid search should be **used with caution**. It's tempting to include a lot of hyperparameter 
values; however, this will cause the search space to explode (with a substantial increase in
model training time).


### `topic_classification_predict.py`
This file contains functions that:
- Apply the NLP text transforms to a DataFrame of unseen text;
- Load the trained TF-IDF vectoriser and classifier model;
- Use the TF-IDF vectoriser on the processed text;
- Use the classifier to generate a prediction for the unseen text.

---

## To run
To train the model, simply navigate to the root directory and run:  
`> python topic_classifier_train.py`

This will complete all the pre-processing steps and generate the 2 x `.pkl` files.

To generate predictions, the best approach is to import the `predict` function from 
`topic_classifier_predict.py`