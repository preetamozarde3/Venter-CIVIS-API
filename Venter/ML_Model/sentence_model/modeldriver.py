from . import csvparser, sentencemodel

# class SimilarityMapping:
#     '''
#     This class consumes the model and sequences the flow of execution for the given input
#     '''
#     def __init__(self, path):
#         self.filepath = path

#     def driver(self):
#         #parsing the input file for having sampled input to the model
#         csvparser.parse(self.filepath)
#         results = sentencemodel.categorizer()
#         return results

class SimilarityMapping:
    '''
    This class consumes the model and sequences the flow of execution for the given input
    '''
    def __init__(self, draft_name, new_responses, category_list):
        self.draft_name = draft_name
        self.new_responses = new_responses
        self.category_list = category_list

    def driver(self):
        #parsing the input file for having sampled input to the model
        responses = csvparser.parse(self.draft_name, self.new_responses)
        results = sentencemodel.categorizer(self.draft_name, responses, self.category_list)
        return results
