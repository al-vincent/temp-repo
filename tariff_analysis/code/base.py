#!/usr/bin/env python
# coding: utf-8

"""
This module provides data processing base classes and helper classes,
that can be called in other modules and/or inherited by other classes.

It is assumed that this module will not be run standalone, and that the
classes contained in it will *only* be invoked by other classes.
However, a main function is included iot demonstrate some of the 
functionality provided.

The classes included here are:
- WordDocProcessor, a base class used for processing Word documents in
docx format;
- ExcelProcessor, a base class used for processing Excel documents;
- HelperFunctions, a class containing a series of helper functions for
reading files (other than Word documents), cleaning pandas dataframes,
file manipulation, and applying simple validity checks.
"""

#======================================================================
# Import libraries
#======================================================================
import logging
import logging.config
import sys

from docx import Document
import numpy as np
import pandas as pd

import log_config as lc

#======================================================================
# Setup Logger
#======================================================================
logging.config.dictConfig(lc.LOG_CONFIG)
logger = logging.getLogger(__name__)


#======================================================================
# Document Processor Class
#======================================================================
class WordDocProcessor():
    """Base class for processing Word documents. Contains a series of
    methods that are generally useful for:
    - Reading the document;
    - Processing data from any tables contained within the document;
    - Converting tables into Pandas DataFrame objects.
    
    Parameters:
        - filepath (str), the docx file to be read / processed.
    """
    
    def __init__(self, filepath):
        self.filepath = filepath        
        self.doc = self.get_raw_data_from_file()            
    
    def get_raw_data_from_file(self):
        """Access the file that contains the raw data.

        Returns:
            - python-docx Document object, containing the Word doc
        """
        try:
            doc = Document(self.filepath)
        # Note: generic 'Exception' used as python-docx raises its own
        # exceptions that can't be imported (AFAIK)
        except Exception as err:
            print(f"ERROR: {err}. Exiting program.")
            logger.critical(f"{err}. Check the filepath, and that the "
                            "file is not corrupted.")
            sys.exit(1)
        else:
            logger.info(f"File {self.filepath} read successfully.")
            return doc
    
    def table_to_df(self, table, headers):
        """Convert a table (list of lists) to a pandas DataFrame.

        Parameters:
            - table (list), the data to convert. All elements in table
            will be concatenated to create a single dataframe.
            - headers (list), the column headers for the dataframe. 
            Each element is a string.
            - first_row_as_hdr (bool), optional flag to indicate 
            whether the first row of the table is a header. 
        
        Returns:
            - Pandas DataFrame object containing the data from 'table'
            and with columns named from 'headers'.
        """
        # create the dataframe from 'table' and 'headers'
        num_rows = len(table)
        num_cols = len(headers)
        try:
            df = pd.DataFrame(np.array(table).reshape(num_rows, num_cols),
                            columns=headers)
        except ValueError as err:
            logger.error(f"{err}. Table could not be convered to df. "
                         f"Original table as np.array:\n{np.array(table)}")
            df = pd.DataFrame(data=[], columns=list(dict.fromkeys(headers)))            

        return df
    
    def docx_to_list(self, table, first_row_as_hdr=True):
        """Convert python-docx Table object to list-of-lists.

        Parameters:
            - table (docx Table object), the table to convert
        
        Returns:
            - list, where each element is an array representing
            an individual table 
        """        
        
        #Recognise and extract all tariff tables
        tbl_rows = len(table.rows)
        num_rows = tbl_rows if not first_row_as_hdr else tbl_rows-1
        num_cols = len(table.columns)
        tbl = [["" for i in range(num_cols)] for j in range(num_rows)]
        
        # There's no nice, fast vectorised way to iterate through
        # tables in python-docx, so have to read them cell by cell.
        hdrs = None
        for i, row in enumerate(table.rows):            
            if first_row_as_hdr and i == 0:
                hdrs = [cell.text.strip() for cell in row.cells]
            else:                
                for j, cell in enumerate(row.cells):
                    if cell.text:
                        if first_row_as_hdr:
                            tbl[i-1][j] = cell.text.strip()
                        else:
                            tbl[i][j] = cell.text.strip()
    
        return {"headers": hdrs, "table": tbl}   
