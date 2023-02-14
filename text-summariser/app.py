""" 
This module does some stuff... TODO
"""

# =====================================================================================
# Import libraries
# =====================================================================================
# External modules
from flask import Flask, render_template, request, session

# Other modules in the repo
from text_summariser import TextSummariser
import config as cf


# =====================================================================================
# App setup
# =====================================================================================
app = Flask(__name__)
# for a production version, should be implemented as an environment var
app.secret_key = cf.SECRET_KEY


# =====================================================================================
# Routes
# =====================================================================================
@app.route("/", methods=("GET", "POST"))
def home():
    """The route used for the application; essentially the 'home page' at the root of
    the domain and accessed via <domain>/, e.g. www.example.com/ (rather than
    www.example.com)

    Returns:
        - a Flask render_template object with a series of arguments. The first argument
        is the name of the HTML file to be rendered (in the 'flask/templates/'
        directory); the rest are values that are passed to the template.

        Most variables will update as the user navigates through the app, overriding
        the defaults. E.g. initially the srch_term variable will be an empty string
        (since the user hasn't entered any information); however, once the user enters
        a search string, that string will be stored as a session variable and used to
        set the value of the input box (e.g. when a POST request is made, and the box
        would otherwise be cleared).
    """   
    # User clicked the 'Summarise' button
    if request.method == "POST":        
        summary_text = run_summariser(request.form)
    # If  a GET request, then clear all session variables
    else:
        summary_text = ""
        session.clear()

    return render_template(
        "index.html",  # html file
        original_text=session.get("original", ""),  # Original input text
        summary_text=summary_text,                  # Summary of the text
        html=cf.HTML
    )


# =====================================================================================
# Helper functions
# =====================================================================================
def run_summariser(form):
    session["original"] = form[cf.HTML["TEXT_ENTRY"]["NAME"]]
    min_words = form[cf.HTML["SUMMARY_SETTINGS"]["MIN_WORDS"]["NAME"]]
    min_words = int(min_words) if min_words else None
    max_words = form[cf.HTML["SUMMARY_SETTINGS"]["MAX_WORDS"]["NAME"]]
    max_words = int(max_words) if max_words else None

    bounds = (min_words, max_words) if (min_words and max_words) else None
  
    ts = TextSummariser(
        session["original"], 
        bounds, 
        model="philschmid/bart-large-cnn-samsum"
    )
    return ts.run_summariser()


# =====================================================================================
# Drivers
# =====================================================================================
if __name__ == "__main__":
    app.run(debug=True)