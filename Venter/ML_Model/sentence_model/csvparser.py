# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 17:15:22 2019

@author: Chintan Maniyar
"""

import os
# import re

# import pandas as pd

from Backend.settings import BASE_DIR

def parse(draft_name, new_responses):
    '''
    This function reads the list of new responses and performs the preprocessing
    Args(1) - draft_name (string), Args(2) - new responses (list)
    '''
    
    for sentence in new_responses:
        sentence = sentence.lstrip().replace('\n', ' ')

    return new_responses

