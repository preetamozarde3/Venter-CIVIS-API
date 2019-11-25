from . import xlsxparser, keywordmodel

class KeywordSimilarityMapping:
    '''
    This class consumes the model and sequences the flow of execution for the given input
    '''
    def __init__(self, draft_name, response, draft_keyword_dict):
        self.draft_name = draft_name
        self.response = response
        self.draft_keyword_dict = draft_keyword_dict

    def driver(self):
        # parsing the input file for having sampled input to the model
        xlsxparser.parse(self.draft_name, self.response)

        results = keywordmodel.categorizer(self.draft_keyword_dict)
        return results


