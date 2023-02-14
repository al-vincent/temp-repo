"""
A series of generally useful 'helper functions'.
These fall into the following types:
- Functions used for reading data;
- Those used for cleaning data; and
- Functions for performing simple data validation checks.

Could be grouped together in classes; however, this seems to add little
value and some overhead, so keeping them as functions
"""

#======================================================================
# Import libraries
#======================================================================
from datetime import datetime
import logging
import logging.config
import os
import sys
from zipfile import ZipFile

import numpy as np
import pandas as pd

import config as c
import log_config as lc

#======================================================================
# Setup Logger
#======================================================================
## File config with a .conf file. Possible to achieve what I want, but
# legacy (and on slow update path) and not super-readable
# logging.config.fileConfig(fname="logging.conf",
#                         # defaults={"logfilename": "logfile.log"},
#                         disable_existing_loggers=False)

## dict config with a yaml file. More readable than file config, but
## hard to set the filename in a flexible way 
# with open('log_config.yml', 'r') as f:
#     conf = yaml.safe_load(f.read())
#     logging.config.dictConfig(conf)

# dict config with a python dict in a .py file. My favourite approach
logging.config.dictConfig(lc.LOG_CONFIG)
logger = logging.getLogger(__name__)


#======================================================================
# File Ingestion Helpers
#======================================================================
def get_csv_data(filepath, keep_default_na=False, 
                na_values=c.CONST["NAN_VALS"]):
    try:
        df = pd.read_csv(filepath, 
                            keep_default_na=keep_default_na,
                            na_values=na_values, 
                            dtype=str)
    except Exception as err:
        logger.critical(f"{err}")
        sys.exit(1)
    else:
        logger.info(f"File {filepath} read successfully.")
        return df
    
#======================================================================
# DataFrame Cleaning and Standardisation Helpers
#======================================================================
def add_standardised_comm_code(df, comm_code_col, 
                               new_col=c.COL_HDRS["STANDARD_COMM_CODE"]):
    """Add a standardised 10-digit commodity code to a dataframe,
    using an existing column as an input. All non-numeric chars are
    stripped from the input, and if the stripped input is less than
    10 digits long, zeros are padded on the end of the new code.
    
    Parameters:
        - df (pandas DataFrame object), the input dataframe that 
        the standardised comm code column should be added to.
        - comm_code_col (str), the name of the column to
        standardise.
        - new_col (str, optional), the name of the column to add
        with the standardised comm code. Defaults to the 
        STANDARDISED_COMM_CODE variable in ingest_config.py
        
    
    Returns:
        pandas DataFrame object, the original dataframe with an 
        extra column appended.
    
    Examples:
        0101          -> 0101000000
        0101 01       -> 0101010000
        0101.01       -> 0101010000
        0101 01 01 01 -> 0101010101
        0101.01.01.01 -> 0101010101
    """
    if comm_code_col in df.columns:
        df[new_col] = (
            df[comm_code_col]
            .str.replace(r"\D+", "", regex=True)
            .str.ljust(width=10, fillchar="0")
        )
    else:
        logger.warning(f"Column {comm_code_col} not in dataframe. " 
                        "Cols: {df.columns}")

    return df

def convert_blank_rows_to_nan(df, col=c.COL_HDRS["COMM_CODE"]):
    df=df.astype("string")
    if col in df.columns:
        idxs = df.index[df[col].str.strip() == ""]
        df.iloc[idxs] = df.iloc[idxs].replace("", np.nan, regex=True)            
    else:
        logger.warning(f"Column {col} not in dataframe. " 
                        "Cols: {df.columns}")
    return df

def remove_nan_rows(df):
    return df.dropna(axis=0, how="all")        

def fill_unused_cells(df, non_regex_replace, non_regex_fill_str,
                    regex_replace=None, regex_fill_str=None):  
    df = df.fillna(non_regex_fill_str)
    
    # NOTE: important that regex=False below, as otherwise *parts*
    # of cells may be replaced with fill_str.
    df = df.replace(non_regex_replace, non_regex_fill_str, regex=False)

    # If regex replacements are needed (e.g. to remove \n, \t in
    # any cell they might occur), then the below will do that. 
    if regex_replace is not None:
        df = df.replace(regex_replace, regex_fill_str, regex=True)

    return df

def remove_rows_with_non_digits(df, col_name):
    """Remove all rows from an input dataframe where a named
    column contains non-numeric characters (after whitespace
    has been removed).
    
    Useful for CHIEF ingest, where some rows contain seasonal
    information; comm codes in these rows contain an alphabetic
    character, and are not required in the output file.
    
    Parameters:
        - df (pandas DataFrame object), the dataframe to be 
        subsetted
        - col_name (str), the column to search 
    
    Returns:
        - pandas DataFrame object, the subset of the original 
        dataframe where all entries in col_name are numeric (may
        contain whitespace)
    """
    return df[df[col_name].str.replace(" ", "").str.isdigit()]

    
#======================================================================
# Data Validation Helpers
#======================================================================       
def check_col_for_pattern(df, col_name, pattern):
    """Find all rows in a dataframe where a given column contains
    a particular pattern. Returns all rows where df.col (with all
    whitespace removed) == pattern. If there are no examples in the
    column, returns an empty dataframe.
    
    Useful for checking whether a column contains the empty_cell
    pattern, for example; or where the Standarised Comm Code column
    contains the pattern "0000000000" (which generally shouldn't
    happen).
    
    Parameters:
        - df (pandas DataFrame object), the dataframe to search.
        - col_name (str), the column name within the dataframe that
        we want to check for 'pattern'
        - pattern (str), the pattern to search for in df.col_name
    
    Returns: 
        - pandas DataFrame containing only rows where 'pattern' is
        in df.col_name            
    """
    return df[df[col_name].astype(str).str.strip() == pattern]

def check_cell_length_is_correct(df, col_name, num_chars):
    """Checks whether all entries in a column have the expected
    number of characters. Returns all rows of df where this is
    *not* true. If all cells in the row have the expected number of
    characters, an empty dataframe is returned.
    
    Parameters:
        - df (pandas DataFrame object), the dataframe whose column
        is to be checked.
        - col_name (str), column in df to check
        - num_chars (int), the number of characters we're expecting
        to be in each cell
    
    Returns:
        - pandas DataFrame object, containing only rows where the
        cells in df.col_name are *not* of length num_chars. If all
        cells have the expected number of characters, return an
        empty DataFrame.
    """
    return df[df[col_name].astype(str).str.len() != num_chars]

def cols_do_not_match(df, col_1, col_2):
    """Checks whether two columns of the same dataframe are
    identical. Returns all rows of the df where they're different.
    If all rows are the same, returns an empty dataframe.
    
    Useful for checking that things like TAP commodity__code is the
    same as 'Standardised Commodity Code' (it should be).
    
    Parameters:
        - df (pandas DataFrame object), the dataframe to check
        - col_1 (str), the first column in df to compare
        - col_2 (str), the second column in df to compare
    
    Returns:
        - pandas DataFrame object containing only rows where 
        df.col_1 != df.col2
    """
    return df[df[col_1] != df[col_2]]

def check_ser_for_length(df, col_name, max_chars):
    """ID any rows in df.col_name to see if there are entries that
    are longer than an expected number of chars
    """
    return df[df[col_name].astype(str).str.len > max_chars]


#======================================================================
# File Renaming and Auto-Archiving Helpers
#======================================================================    
def add_timestamp(input_str):
    """Insert a timestamp to a filepath-like input, and return the 
    new filepath.

    Parameters:
        - input_str (str, or any data type that can be cast to 
        str), the string to prepend the timestamp to. 

    Returns:
        - str, original input plus a timestamp in YYYYMMDD-hhmmss
        format inserted at the start of the filename part of the 
        pathname, with an underscore separating the timestamp and
        the filename
    
    Examples:
        input_str = "/path/to/file.csv"
        returns: "/path/to/20211103-132021_file.csv"
        
        input_str = "file.csv"
        returns: "20211103-132021_file.csv"
    
    Notes:
        - It is assumed that input_str is filepath-like. If this
        isn't the case, it will simply prepend a timestamp at the
        start of input_str.
    """
    # get the timestamp and convert it to the correct format
    now = datetime.now()
    timestamp = now.strftime(c.CONST["TIME_FORMAT"])
    
    # split input_str into dir and file; insert timestamp; re-merge
    dir_name, file_name = os.path.split(input_str)
    file_name = f"{timestamp}_{file_name}"
    return os.path.join(dir_name, file_name)

def write_file_info(dir_name, text_list):
    if not isinstance(text_list, list):
        text_list = [text_list]
    
    now = datetime.now()
    file_name = f"{now.strftime(c.CONST['TIME_FORMAT'])}_input_files.txt"
    file_path = os.path.join(dir_name, file_name)
    
    try:
        with open(file_path, "w") as f:
            for item in text_list:
                f.write(item + "\n")
    except Exception as err:
        logger.error(f"{err}. The list {text_list} could not be "
                        f"written to {file_path}")
    else:
        logger.info(f"{file_path} successfully written.")

def add_files_to_zip(target_dir, file_list, 
                        time_format=c.CONST["TIME_FORMAT"]):
    """Add a list of files to a zip archive. Name of the zip is 
    ''<timestamp>_results.zip', e.g. '20211105-133123_results.zip'
    
    Parameters:
        - target_dir (str), the directory where the zip file will
        be saved
        - file_list (list), a list of filenames to be added to the
        zip file.
        - time_format (str), a strftime-style time format string
        that represents the first n characters of the files to be 
        zipped. Optional, default is set by the TIME_FORMAT
        constant in ingest_config.py
    
    Notes:
        - This assumes that files to be zipped start with a 
        timestamp. If they don't, the name of the zip file will
        be unpredictable in format. If the filename is shorter
        than len(time_format), the results file will be default to
        "results.zip"
    """
    # generate the zip filename by stripping the timestamp from the
    # name of the 1st file to be archived.
    # Note: num_chars is calculated fully so that the below works
    # regardless of the time format used.
    num_chars = len(datetime.strftime(datetime.now(), time_format))
    zip_name = "results.zip"
    try:
        zip_name = f"{os.path.basename(file_list[0])[:num_chars]}_results.zip"
    except Exception as err:
        logger.warning(f"{err}. The zip filename was not created "
                        f"successfully.\nfile_list: {file_list}"
                        f"\nnum_chars: {num_chars}")
    
    # zip all files in the list
    zip_path = os.path.join(target_dir, zip_name)
    try:
        with ZipFile(zip_path, mode="w") as zip_obj:
            for f in file_list:
                zip_obj.write(f, os.path.basename(f))
    except Exception as err:
        logger.error(f"{err}. The list {file_list} could not be "
                        f"written to {zip_path}")
    else:
        logger.info(f"{file_list} successfully written to {zip_path}")
                
            
def get_all_files_in_dir(dir_name):
    """Get a list of all files (of any file type) in a directory.
    
    Parameters:
        - dir_name (str), the directory to take files from.
        
    Return:
        - list, containing the filenames recovered (as strings)
    """
    try:
        file_list = [os.path.abspath(os.path.join(dir_name, f.name)) 
                        for f in os.scandir(dir_name) if f.is_file()]
    except Exception as err:
        logger.error(f"{err}. Files could not be taken from {dir_name}")
    else:
        logger.info(f"Files extracted from {dir_name}: {file_list}")
        return file_list

def delete_files_from_dir(file_list):
    """Delete all files in a list.
    
    Parameters:
        - file_list (list), a list of the files to be deleted.
    
    Notes:
        - the files in file_list should contain the filepath,
        (relative or absolute), not just the filenames
    """
    for f in file_list:
        try:
            os.remove(f)
        except OSError as err:
            logger.error(f"{err}. could not delete file {f}")
        else:
            logger.info(f"File {f} successfully deleted")

def auto_archive_files(dir_name, archive_dir, to_zip=True):
    """Archive all files contained within a directory.

    If the to_zip flag is true (default), all files are added to a 
    zip archive, which is saved in the archive_dir directory. The 
    original files are deleted.

    If to_zip == False, all original files are moved to the archive 
    directly.

    Parameters:
        - dir_name (str), the source path of the directory whose 
        contents are to be archived
        - achive_dir (str), the destination path for the archived files
        - to_zip (bool), flag to indicate whether the files should be
        zipped before archiving
    """
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
    
    # case 1: add files to zip, archive, delete originals
    if to_zip:
        file_list = get_all_files_in_dir(dir_name)
        add_files_to_zip(archive_dir, file_list)
        delete_files_from_dir(file_list)
    # case 2: move files straight to archive
    else:
        pass
