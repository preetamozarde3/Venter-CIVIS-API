# -*- coding: utf-8 -*-
"""
Created on Tue June 25 2019

@author: Anushri Arora
"""

import os

import pandas as pd
from nltk.tokenize import sent_tokenize, word_tokenize

from Backend.settings import BASE_DIR


def parse(draft_name, response):
    '''
    This function parses the json response(sent by POST API Endpoint) and creates .txt file based
    on the corresponding draft name
    Args(1) - draft_name (string)
    Args(2) - responses (list)
    
    '''
    tokenized_text=[]
    for item in response:
        tokenized_text+=sent_tokenize(item)
    draft_name = draft_name.lower()
    name = draft_name+'.txt'
    path = 'Venter/ML_Model/keyword_model/data/keyword data/'+name

    file1 = open(path, 'w')
    for sent in tokenized_text:
        file1.write(sent)
        file1.write('\n')
    file1.close()
