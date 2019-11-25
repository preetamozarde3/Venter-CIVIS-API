'''
(C) Chintan Maniyar
File created 20:47,
May 28, 2019
'''

import json
import string, re
import inflect
import nltk


def mapNounFrequency(sentenceList):
    '''
    This function tags entities for a given list of sentences and returns a
    frequency map preserving the likeliness of singular and plural occurences
    '''
    fMap = {}

    if sentenceList == []:
        return fMap
    
    p = inflect.engine()

    for sentence in sentenceList:
        is_noun = lambda pos: pos[:2] == 'NN'
        tokenized = nltk.word_tokenize(sentence)
        entities = [word for (word, pos) in nltk.pos_tag(tokenized) if is_noun(pos)]
        for entity in entities.copy():
            entities.remove(entity)
            if not p.singular_noun(entity):
                entities.append(p.plural(entity).lower())
            else:
                entities.append(entity.lower())
        entities = set(entities)
        for entity in entities:
            if entity in fMap:
                fMap[entity] += 1
            else:
                fMap[entity] = 1

    if len(entities)==0:
        return fMap
    frequency = list(fMap.values())
    normalizer = max(frequency)
    for entity, raw in zip(fMap, frequency):
        fMap[entity] = int((raw/normalizer)*100)
    return fMap


def generate_wordcloud(input_wordcloud):
    '''   
    main/ driver function
    input_wordcloud has format { category: [complaint1, complaint2 ,..], }
    words_output has format { category: [{ word: "word1", freq: freq1 }], }
    '''
    
    '''
    input_wordcloud has format { category: [complaint1, complaint2 ,..], }
    words_output has format { category: [{ word: "word1", freq: freq1 }], }
    '''

    data = {}
    words = {}
    data = input_wordcloud

    for k, v in data.items():
        temp_list = []
        temp_list = mapNounFrequency(v)
        words[k] = temp_list

    words_output = {}

    for k, v in words.items():
        words_output[k]=[]
        for k1, v1 in v.items():
            words_output[k].append({'word':k1,'freq':v1})


    '''
    input_wordcloud has format [complaint1, complaint2 ,..]
    words_output has format [{ word: "word1", freq: freq1 }, { word: "word2", freq: freq2 },]
    '''

    # data = []
    # data = input_wordcloud
    # words = {}
    # words = mapNounFrequency(data)
    # words_output = {}
    # words_keys = list(words.keys())
    # f_1 = (lambda x: x.lower().translate(x.maketrans(string.punctuation,' '*len(string.punctuation))))
    # f_2 = (lambda x:re.sub(r"\s+", ' ', x))
    # words_keys = [f_1(x) for x in words_keys]
    # words_keys = [f_2(x) for x in words_keys]

    # for k, v in zip(words_keys, words.values()):
    #     if len(k)>2:
    #         words_output[k.upper()] = v

    return words_output