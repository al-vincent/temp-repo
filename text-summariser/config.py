import os

SECRET_KEY = "MY_SECRET_KEY"


HTML = {
    "TEXT_ENTRY": {
        "PANEL_ID": "text-entry-div-id",
        "EXAMPLE_BTN_ID": "example-btn-id",
        "FORM_ID": "summarise-form-id",
        "ID": "text-entry-id",
        "NAME": "text-entry",
        "ROWS": 15
    },
    "SUMMARY_SETTINGS": {
        "MIN_WORDS": {
            "NAME": "min-words",
            "MIN": 10,
            "MAX": 100,
            "VALUE": ""
        },
        "MAX_WORDS": {
            "NAME": "max-words",
            "MIN": 40,
            "MAX": 250,
            "VALUE": ""
        },
        "SUMMARISE": {
            "NAME": "summarise-submit",
            "VALUE": "Summarise"
        }
    },
    "SUMMARISE": {
        "ID": "summarise-div-id"
    }
}
