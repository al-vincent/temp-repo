"""
This file contains a range of settings used by the data processing and
ingestion programs. The ingestion uses a number of constant values,
including filenames, filepaths, column names etc., and storing these
values in a single place should make it more straightfoward to update
and maintain the code base.

To help navigation, the values are broken down into sections, with one
section for each major data source or 'governance area'. The structure
is designed to keep string literals to a single place at the top of
the file as much as possible, and then refer to variable names below 
(rather than have the same string literal scattered across the file in
several different places).
"""

from datetime import datetime
import os

#======================================================================
# FILE AND DIRECTORY PATHS
#======================================================================
# Top-level directory paths
# FILE_DIR is the path to the file containing the calling function
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.abspath(os.path.join(FILE_DIR, "..",  "data", "raw"))
OUTPUT_DIR = os.path.abspath(os.path.join(FILE_DIR, "..", "data", "processed"))

INPUT_DIR_DEMO = os.path.join(INPUT_DIR,"demo")
OUTPUT_DIR_DEMO = os.path.join(OUTPUT_DIR,"demo")

ARCHIVE_DIR = os.path.join(OUTPUT_DIR,"archive")

# Input files used for key data sources
AU_RATES_FILE = "Authorised-Use-Eligible-goods-and-rates-Final-20210719.docx"
AU_USES_FILE = "Authorised-Use-Eligible-goods-and-authorised-uses-Final-20210719__1_.docx"

DEMO_AU_RATES_FILE = "Authorised-Use-Eligible-goods-and-rates-Final-20210719_shortened.docx"
DEMO_AU_USES_FILE = "Authorised-Use-Eligible-goods-and-authorised-uses-Final-20210719__1_shortened.docx"


# Output filenames for key data sources 
# Note: demo output files use the same filenames as 'full' outputs
AU_RATES_OUT = "au_rates.csv" 
AU_USES_OUT = "au_uses.csv"


# Other key files and directories
f_name = datetime.strftime(datetime.now(), '%Y%m%d-%H%M%S')
LOG_FILE = os.path.join(FILE_DIR, "logs", f"{f_name}_ingest.log")

#======================================================================
# OVERALL CONSTANTS
#======================================================================

CONST = {
    "EMPTY_CELL": "empty_cell",

    # Values for Pandas to interpret as NaN with read_csv. Largely as per
    # default, but with "NA", "n/a" and a few others removed
    "NAN_VALS": ["", "#N/A", "#N/A N/A", "#NA", "-1.#IND", "-1.#QNAN", 
                "-NaN", "-nan", "1.#IND", "1.#QNAN", "<NA>", "NULL", "NaN",
                "nan", "null"],

    # Time formatting for filenames
    "TIME_FORMAT": "%Y%m%d-%H%M%S"
}

# Column headers (done here and reused throughout)
COL_HDRS = {
    "COMM_CODE": "commodity_code",
    "STANDARD_COMM_CODE": "standardised_commodity_code",
    "FULL_DESCRIPTION": "parent_and_commodity_description",
    "DESCRIPTION": "commodity_description",
    "DUTY_EXP": "duty_expression",
    "GOODS_USE_DESCRIPTION": "goods_and_use_description",
    "USAGE": "usage_statements"
}



#======================================================================
# AUTHORISED USE DOCUMENTS INGEST SETTINGS
#======================================================================
AU_RATES = {
    "INPUT_FILE": os.path.join(INPUT_DIR, AU_RATES_FILE),
    "INPUT_FILE_DEMO": os.path.join(INPUT_DIR_DEMO, DEMO_AU_RATES_FILE),
    "OUTPUT_FILE": os.path.join(OUTPUT_DIR_DEMO, AU_RATES_OUT),
    "OUTPUT_FILE_DEMO": os.path.join(OUTPUT_DIR_DEMO, AU_RATES_OUT),
    "HEADERS": [COL_HDRS["COMM_CODE"], COL_HDRS["DESCRIPTION"], 
                COL_HDRS["DUTY_EXP"]]
}

AU_USES = {
    "INPUT_FILE": os.path.join(INPUT_DIR, AU_USES_FILE),
    "INPUT_FILE_DEMO": os.path.join(INPUT_DIR_DEMO, DEMO_AU_USES_FILE),
    "OUTPUT_FILE": os.path.join(OUTPUT_DIR, AU_USES_OUT),
    "OUTPUT_FILE_DEMO": os.path.join(OUTPUT_DIR_DEMO, AU_USES_OUT),
    "HEADERS": [COL_HDRS["COMM_CODE"],
                COL_HDRS["GOODS_USE_DESCRIPTION"]],
    "NEW_COLS": {
        "FULL_DESC": COL_HDRS["FULL_DESCRIPTION"],
        "USAGE": COL_HDRS["USAGE"],
        "DESC": COL_HDRS["DESCRIPTION"]
    },
    "REPLACE_PATTERNS": [f"\n{chr(8226)} ", "\n- ", "\n-\t","\n14• ", "\n-          ", "\n"],
    "USAGE_PATTERNS": {
        "for incorporation in ships, boats or other vessels listed in Table 1": (
            "for incorporation in ships, boats or other vessels listed in Table 1, for the purposes of their construction, repair, maintenance or conversion;"
            "\nfor fitting to or equipping such ships, boats or other vessels;"
            "\nfor incorporation, for the purposes of their construction, repair, maintenance or conversion, in drilling or production platforms listed below: fixed, of subheading ex 8430 49 or floating or submersible of subheading 8905 20;"
            "\nfor equipping the above platforms;"
            "\nfor linking these drilling or production platforms to the mainland"
        ),    
        "use by, or on behalf of, the UK Armed Forces": (
            "use by, or on behalf of, the UK Armed Forces, individually or in cooperation with other States"
            "\nfor defending the territorial integrity of the United Kingdom, or"
            "\nin participating in international peace-keeping or support operations, or"
            "\nfor other military purposes like the protection of nationals of the United Kingdom from social or military unrest or,"
            "\nfor training purposes, or"
            "\ntemporarily, for civil purposes in the customs territory of the United Kingdom due to unforeseen or natural disasters."
        ),
        f"{chr(8226)} use in civil aircraft": (
            "use in civil aircraft"
            "\nuse for incorporation in civil aircraft in the course of their manufacture, repair, maintenance, rebuilding, modification or conversion"
            "\nuse in ground flying trainers for civil use"
        ),
        "for the construction, maintenance and repair": (
            "for the construction, maintenance and repair of aircraft of an unladen weight exceeding 2000 kilograms and of ground flying trainers for civil use"
        )
    }
}
