import json
import os

from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from Venter.models import File, Organisation, Draft, UserResponse, Category, SentenceCategory
from Venter.serializers import FileSerializer
from Venter.ML_Model.keyword_model.modeldriver import KeywordSimilarityMapping
from Venter.ML_Model.sentence_model.modeldriver import SimilarityMapping
from Backend.settings import MEDIA_ROOT

from .wordcloud import generate_wordcloud


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects
    serializer_class = FileSerializer

    @classmethod
    def list(cls, request):
        """
            FileViewSet for getting a list of output files predicted by the ML model
            for the input data(citizen responses) input by all organisations registered with the application
        """
        queryset = File.objects.all()

        # Serialize and return
        serialized = FileSerializer(queryset, context={'get': 'list'}, many=True).data

        return Response(serialized)

    @classmethod
    def retrieve(cls, request, organisation):
        """
            FileViewSet for retrieving a list of output files predicted by the ML model
            for the input data(citizen responses) input by a specific organisation
        """
        org_name = Organisation.objects.get(organisation_name=organisation)
        queryset = File.objects.filter(organisation_name=org_name).order_by('ckpt_date')

        # Serialize and return
        serialized = FileSerializer(queryset, context={'get': 'retrieve'}, many=True).data

        return Response(serialized)

class ModelKMView(APIView):
    """
        Arguments:  1) APIView: Handles POST requests of type DRF Request instance. 
        Methods:    1) post: This handler is utilized for CIVIS App to send json Input to Keyword-based ML API endpoint
        Workflow:   1) On retrieval of DICT containing one or more responses and categories(extracted from draft summary),
                        the responses and keywords(extracted categories) are separately retrieved to be fed into the categorizer(words) method.
                    2) The KeywordSimilarityMapping class handles the request to the CIVIS ML model.
                    3) The output/ directory is created in order to save the ML model output results based on draft_name, ckpt_date.
                    4) If the draft already exists in the db, then:
                        a. If responses received already exist in the db, the ml_output.json file is directly fetched from the db.
                        b. If a set of responses received do not exist in the db, a response list is generated and fed into the ml model.
                    5) The output from the CIVIS ML model is sent to the CIVIS application as an HTTPResponse (JSON format).
    """
    def post(self, request):
        ml_input_json_data=json.loads(request.body)

        draft = list(ml_input_json_data.keys())[0]
        draft_name = draft.lower()

        org_obj = Organisation.objects.get(organisation_name='CIVIS')
        response=[]
        for draft, val in ml_input_json_data.items():
            for item in val['responses']:
                response.append(item)
        keyword_dict={}
        for draft, val in ml_input_json_data.items():
            keyword_list = val['summary']
        keyword_dict[draft_name] = keyword_list

        try:
            draft_obj = Draft.objects.get(organisation_name=org_obj, draft_name=draft_name)

            # create response list(only for the new set of responses i.e. responses not already existing in the db for a particular draft_name)
            temp_response = []
            temp_response = response
            response2 = []
            for resp in temp_response:
                if UserResponse.objects.filter(draft_name=draft_obj, user_response=resp).exists()==False:
                    UserResponse.objects.create(draft_name=draft_obj, user_response=resp)
                    response2.append(resp)

            # if response list is empty, then responses received are same, hence directly fetch the ml_output file associated with the draft_name
            # if response list is not empty, the list is fed into the ML model for performing prediction on the new set of responses
            results = draft_obj.ml_output.output_file_json.path
            f = draft_obj.ml_output
            # with open(results, 'r') as content:
            #   dict1 = json.load(content)




            temp1 = f.output_filename
            temp2 = os.path.splitext(temp1)
            custom_input_file_name = temp2[0]
            output_json_file_name = custom_input_file_name+'.json'
            results = os.path.join(MEDIA_ROOT, f'{f.organisation_name}/{f.ckpt_date.date()}/output/{output_json_file_name}')

            with open(results, 'r') as content:
                dict1 = json.load(content)





            if len(response2)==0:
                ml_output = dict1
            else:
                sm = KeywordSimilarityMapping(draft_name, response2, keyword_dict)
                dict2 = sm.driver()

                # open pre-existing ml output file and append new response to it; update ml_output file; pass response to API.
                draft_key = list(dict1.keys())[0]
                d1=list(dict1.values())[0]
                d2=list(dict2.values())[0]
                d3={}
                for k, v in d1.items():
                    if k not in d3.keys():
                        d3[k]=v
                for k, v in d2.items():
                    if k in d3.keys():
                        if len(v)==0:
                            pass
                        else:
                            l=d3[k]
                            l=l+v
                            d3[k]=l
                    else:
                        d3[k]=v
                ml_output={}
                ml_output[draft_key]=d3

            with open(results, 'w') as content:
                json.dump(ml_output, content)

        except Draft.DoesNotExist:
            sm = KeywordSimilarityMapping(draft_name, response, keyword_dict)
            ml_output = sm.driver()

            # create Draft, Category, UserResponses, File objects instances in Database
            draft_obj = Draft.objects.create(organisation_name=org_obj, draft_name=draft_name)
            for cat in keyword_list:
                Category.objects.create(draft_name=draft_obj, category=cat)
            for resp in response:
                UserResponse.objects.create(draft_name=draft_obj, user_response=resp)

            file_instance = File.objects.create(
                organisation_name=org_obj,
            )
            file_instance.save()

            output_directory_path = os.path.join(MEDIA_ROOT, f'{file_instance.organisation_name}/{file_instance.ckpt_date.date()}/output')
            if not os.path.exists(output_directory_path):
                os.makedirs(output_directory_path)

            file_id = str(file_instance.id)
            output_file_json_name = 'ml_output__'+file_id+'.json'
            output_file_json_path = os.path.join(output_directory_path, output_file_json_name)

            with open(output_file_json_path, 'w') as temp:
                json.dump(ml_output, temp)
            file_instance.output_file_json = output_file_json_path
            file_instance.save()

            Draft.objects.filter(draft_name=draft_name).update(ml_output=file_instance)

        return HttpResponse(json.dumps(ml_output), content_type="application/json")


class WCView(APIView):
    """
        Handles a get request where the draft name is mentioned in the URL itself
        input: url/venter/modelWC?draft_name="draft name string without quotes"
        output: {draft name: {'word': word 1, 'freq': freq1}, ...}

    """
    def get(self, request):

        draftname = request.GET.get('draft_name')
        draft_obj = Draft.objects.get(draft_name = draftname)
        user_response_obj = UserResponse.objects.filter(draft_name = draft_obj)
        wc_input = {}
        wc_input[draftname] = []
        for user_response_obj_instance in user_response_obj:
            wc_input[draftname].append(user_response_obj_instance.user_response)

        wc_output = generate_wordcloud(wc_input)

        with open("wc_output.json", 'w') as content:
                json.dump(wc_output, content)
        
        return HttpResponse(json.dumps(wc_output), content_type="application/json")


class ModelSMView(APIView):

    """
        Arguments:  1) APIView: Handles POST requests of type DRF Request instance. 
        Methods:    1) post: This handler is utilized for CIVIS App to send json Input to Sentence-based ML API endpoint.
        Workflow:   1) On retrieval of DICT containing one or more responses and categories(extracted from draft summary),
                        the responses and sentences(extracted categories) are separately retrieved to be fed into the model_driver method.
                    2) The SimilarityMapping class handles the request to the CIVIS ML model.
                    3) If the draft already exists in the db, then:
                        a. New responses are saved into the db.
                        b. All responses with respective draft are fed into the ml model .
                    4) If the draft does not exist in the db then:
                        a. Save the new draft and all the corresponding new responses and list of categories
                        b. Fed the new draft and list of new responses and categories to the ml model
                    5) The output from the CIVIS ML model is sent to the CIVIS application as an HTTPResponse (JSON format).
    """

    def post(self, request):

        ml_input_json_data = json.loads(request.body)

        ml_sm_output = {}

        # Start traversing the data sent as the body
        for draft, data in ml_input_json_data.items():
            
            org_obj = Organisation.objects.get(organisation_name='CIVIS')
            
            print("draft: \n", draft)
            # Checking if the draft exist in the db or not
            # If yes then fitering the new responses and populating them to db
            # Try will work only if the draft already exists
            try:
                print("Trying if draft exists\n")
                
                new_responses = []
                print("Checking for new responses and creating the instances for them")
                for response in data["responses"]:
                    if UserResponse.objects.filter(user_response=response).exists():
                        pass
                    else:
                        user_response_obj = UserResponse.objects.create(
                            draft_name=Draft.objects.get(organisation_name=org_obj, draft_name=draft),
                            user_response=response)

                        new_responses.append(response)

                print("Checking for new responses and creating the instances for them")
                for category in data["summary"]:
                    if Category.objects.filter(category=category).exists():
                        pass
                    else:
                        cat_obj = SentenceCategory.objects.create(
                            draft_name=Draft.objects.get(
                                organisation_name=org_obj, 
                                draft_name=draft),
                            category=category)

                
                sm = SimilarityMapping(draft, data['responses'], data["summary"])
                print("Sentence model declared\n")

                print("Sentence Model invoked\n")
                output = sm.driver()

                ps = "Output for " + draft + " generated\n"
                print(ps)

                ml_sm_output[draft] = output[draft]


            # If draft doesn't exist then adding it to db
            # Adding all the corresponding responses to db
            # Adding all the corresponding categories to db
            # Fed new draft, responses and the categories to ML model

            # Except if draft doesn't exist
            except:
                print("The draft does not exists\n")
                draft_obj = Draft.objects.create(draft_name=draft, organisation_name=org_obj)
                
                new_responses = []

                print("Creating the response instances\n")
                for response in data["responses"]:
                    user_response_obj = UserResponse.objects.create(draft_name=draft_obj, user_response=response)
                    user_response_obj.save()
                    new_responses.append(response)

                print("Creating sentence category instances\n")
                for category in data["summary"]:
                    cat_obj = SentenceCategory.objects.create(
                            draft_name=Draft.objects.get(organisation_name=org_obj, draft_name=draft),
                            category=category)
                
                print("Declaring the Sentence model\n")
                sm = SimilarityMapping(draft, new_responses, data["summary"])
                output = sm.driver()

                ps = "Output for " + draft + " generated\n"
                print(ps)

                ml_sm_output[draft] = output[draft]

            

        return HttpResponse(json.dumps(ml_sm_output), content_type="application/json")
