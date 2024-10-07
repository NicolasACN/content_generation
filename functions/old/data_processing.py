import os
import json
from copy import deepcopy
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
import openai
from tqdm import tqdm
import openpyxl
import pandas as pd
from operator import itemgetter
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
# from functions.chain import choose_model
import streamlit as st


# Global Variables 
## Load cw_guidelines
# LEXICON_PATH = os.path.join(os.getcwd(), "data", "guidelines", "full_lexicon", "cw_guidelines.txt")
# assert os.path.exists(LEXICON_PATH)

# with open(LEXICON_PATH, "r") as f:
#     cw_guidelines = f.read()

load_dotenv(find_dotenv())
openai.api_key = st.secrets['OPENAI_API_KEY']
    
# Correct and Consolidate
# def correct_answers(df):

#     def consolidate_and_correct_info(df, consolidate_and_correct_chain):
#         input_data = {
#             "variable_name": df["Key information"],
#             "variable_retrieved": df["Key information retrieved"],
#             "hotel_comment": df["Please validate, correct or complete the information if needed"]
#         }
#         return consolidate_and_correct_chain.invoke(input_data)
    
    
#     def make_consolidation_chain(model): 
#         class ConsolidatedAnswer(BaseModel):
#             consolidated_answer:str = Field(description="Modified information retrived based on the hotel feedback")
        
#         parser = JsonOutputParser(pydantic_object=ConsolidatedAnswer)

#         prompt_template = PromptTemplate(
#             template="""
# You are an expert senior consultant working for the Pullman hotel group client. You have launch a survey to hotel managers to collect their feedback on information retrieved by your team on their hotels. Your task is to take into account the feedback left by the hotel to modify accordingly the information you retrieved and correct it if necessary. There are a few cases to consider: the hotel might have commented 'ok' which indicated the information you retrived is right, the hotel might have commented 'x' which indicates there is no information for this field in which case you should leave the information as an empty string. There are also 2 more complex cases where the hotel have typed a comment, if the comment is modifying the information or part of it your task is to modify the information accordingly, but if the hotel comment looks unrelated to the information you retrieved then you should only consider the hotel comment as replacement.
# Here are the information retrieved and the hotel comment for the variable named '{variable_name}':
#     Information Retrieved : {variable_retrieved}
#     Hotel Comment : {hotel_comment}
    
#     Please modify the information retrieved based on the hotel comment if needed. 
    
#     {format_instructions}
# """,
#             input_variables=["variable_name", "variable_retrieved", "hotel_comment"],
#             partial_variables={"format_instructions": parser.get_format_instructions()}
#         )

#         consolidation_chain = prompt_template | model | parser
#         consolidation_chain_fallback = prompt_template | ChatOpenAI(model_name="gpt-4-turbo", temperature=0) | parser
#         return consolidation_chain.with_fallbacks([consolidation_chain_fallback])

#     def make_lexicon_correction_chain(model):
#         class CorrectedText(BaseModel):
#             corrected_text: str = Field(description="The corrected text")
        
#         data_refactoring_system_message_prompt_template = """
# You are impersonating the british editor of a premium travel magazine, perhaps Condé Nast Traveller Magazine.

# You are familiar with Pullman's copywriting and brand guidelines. Your task is to be the final reviewer of a text written about one aspect of a Pullman hotel and ensure it strictly follow the Pullman copywriting rules and especially the lexicon of words. 
# However, pay close attention to if the writer has used any forbidden words and rework the copy to ensure they are replaced. 

# <copywriting_guidelines>
# {cw_guidelines}
# </copywriting_guidelines>

# """

#         data_refactoring_human_message_prompt_template = """
# Your task is to review then make minor edits if necessary to ensure the copy stricly follows the Pullman copywriting rules and lexicon of words.
# You are not allowed to make substantial changes to the copy, only minor edits if the writer has used any forbidden words and rework the copy to ensure they are replaced making the copy perfect without editing numbers. 

# <writer_text>
# {consolidated_answer}
# </writer_text>

# {format_instructions}

# """

#         output_parser = JsonOutputParser(pydantic_object=CorrectedText)
#         prompt = ChatPromptTemplate(
#             messages=[
#                 SystemMessagePromptTemplate.from_template(data_refactoring_system_message_prompt_template),
#                 HumanMessagePromptTemplate.from_template(data_refactoring_human_message_prompt_template)
#             ],
#             input_variables=["cw_guidelines", "generated_text"],
#             partial_variables={"format_instructions": output_parser.get_format_instructions()}
#         )
    
#         lexicon_correction_chain = RunnablePassthrough.assign(cw_guidelines=lambda x: cw_guidelines) | prompt | model | output_parser | itemgetter("corrected_text")
#         fallback_lexicon_correction_chain = RunnablePassthrough.assign(cw_guidelines=lambda x: cw_guidelines) | prompt | ChatOpenAI(model_name="gpt-4-turbo", temperature=0) | output_parser | itemgetter("corrected_text")
        
#         return lexicon_correction_chain.with_fallbacks([fallback_lexicon_correction_chain])

#     # model = choose_model("4-turbo") original, if code breaks revert to this model
#     model = choose_model("gpt-4-turbo") 

    
#     consolidation_and_correction_chain = make_consolidation_chain(model) | make_lexicon_correction_chain(model)
    
#     # Process values
#     df['Post Processed Value'] = df.apply(lambda x: consolidate_and_correct_info(x, consolidation_and_correction_chain), axis=1)
    
#     return df


# # Make Non Nested Data Dict
# ## General case
# def make_non_nested_tab_variables(surey_tab):
#     df = deepcopy(surey_tab)
#     df.fillna('', inplace=True)
    
#     # Clean useless lines:
#     df = clean_useless_separator_lines(df)
#     # Consolidate and Correct    
#     df = correct_answers(df)
    
#     data_dict = {}

#     for index, row in df.iterrows():
#         # TODO : debug to remove once fixes
#         try:
#             if row['Key information'] in ['', '\xa0']:
#                 pass
#             elif row['Key information'] == "Best selling events in that venue (M&E, weddings, gatherings, coworking, etc)":
#                 key_info = "best_selling_events"
#                 data_dict[key_info] = {
#                     "value": str(row['Post Processed Value']).replace('\n', ', '),
#                     "description": row['Key information'].strip(' ')
#                 }
#             elif row['Key information'] == "Service name":
#                 key_info = "service_name"
#                 data_dict[key_info] = {
#                     "value": str(row['Post Processed Value']),
#                     "description": "Name of the service"
#                 }
#             else:    
#                 key_info = row['Key information'].split(':')[0].lower().strip(' ').replace(' ', '_')
#                 data_dict[key_info] = {
#                     "value": str(row['Post Processed Value'].strip()),
#                     "description": row['Key information'].split(':')[1].strip(' ')
#                 }
#         # TODO : debug to remove
#         except Exception as e:
#             print(f"Error for row {row}\n DF: {df}")
#             raise e
        
#     return data_dict

# MICE case
# def make_mice_non_nested_tab_variables(mice_tab):
#     df = deepcopy(mice_tab)
#     rows_to_keep = [0, 1, 2, 3]

#     df = df.loc[rows_to_keep]
#     df.fillna('', inplace=True)
#     df.head()
    
#     # Consolidate and Correct
#     df = correct_answers(df)

#     # TODO: add consolidation and correction processing HERE !
    
#     featured_venues_hotel_contribution = df.iloc[0]['Please validate, correct or complete the information if needed']

#     if '\n' in featured_venues_hotel_contribution:
#         parsed_featured_venues_hotel_contribution = [elt.strip(' ') for elt in featured_venues_hotel_contribution.split('\n')]
#     elif ',' in featured_venues_hotel_contribution:
#         parsed_featured_venues_hotel_contribution = [elt.strip(' ') for elt in featured_venues_hotel_contribution.split(',')]
#     elif '-' in featured_venues_hotel_contribution:
#         parsed_featured_venues_hotel_contribution = [elt.strip(' ') for elt in featured_venues_hotel_contribution.split('-')]
#     elif not featured_venues_hotel_contribution or featured_venues_hotel_contribution.upper() in {'NA', 'N/A'} or featured_venues_hotel_contribution.strip() == '':
#         parsed_featured_venues_hotel_contribution = []
#     else:
#         parsed_featured_venues_hotel_contribution = process_featured_venues_chain(featured_venues_hotel_contribution)

#     featured_venues = {
#         "mice_featured_venues_list": {
#             "value": parsed_featured_venues_hotel_contribution, 
#             "description": "list of the hotel featured venues"
#         }
#     }
    
#     return featured_venues | {"mice_featured_venues_" + key: value for key, value in make_non_nested_tab_variables(df.loc[[1, 2, 3]]).items()}
    
    
# # Build non nested data dict
# def make_non_nested_data_dict(survey):
#     non_nested_tabs = ['General Info', 'Food and Beverage', 'Wellness & Wellbeing', "MICE"]
    
#     non_nested_data_dict = {} 
    
#     for tab in non_nested_tabs:
#         if not tab == "MICE":
#             non_nested_data_dict = non_nested_data_dict | make_non_nested_tab_variables(survey[tab])
#         else:
#             non_nested_data_dict = non_nested_data_dict | make_mice_non_nested_tab_variables(survey[tab])
    
#     return non_nested_data_dict

def make_dict_variable_values(category_dict, variable_name):
    variable_value_dict = {}
    for element in category_dict: 
        variable_value_dict[element] = category_dict[element][variable_name]
    return variable_value_dict

def get_bloc_data_variable(data_dict, variable_name):
    # if non nested:
    if variable_name in data_dict:
        return data_dict[variable_name]
    # if nested case or missing:
    else:
        found = False
        for category in data_dict:
            # if nested:
            # if variable is a category
            if 'value' not in data_dict[category].keys():
                for key in data_dict[category].keys():
                    if variable_name in data_dict[category][key]:
                        found = True 
                        return make_dict_variable_values(data_dict[category], variable_name)
        
        # # mispelled variables
        # if variable_name == "taxi_or_shuttle_availability" or variable_name == "taxi_or_shuttle_availabilty":
        #     if "taxi_or_shuttle_availabilty" in data_dict.keys():
        #         found = True
        #         return data_dict["taxi_or_shuttle_availabilty"]
        #     elif "taxi_or_shuttle_availability" in data_dict.keys():
        #         found = True
        #         return data_dict["taxi_or_shuttle_availability"]
        
        # if variable_name == "restaurant_athmosphere" or variable_name == "restaurant_atmosphere":
        #     if "restaurant_athmosphere" in data_dict["RESTAURANT"][list(data_dict["RESTAURANT"].keys())[0]]:
        #         found = True
        #         return make_dict_variable_values(data_dict["RESTAURANT"], "restaurant_athmosphere")
        #     elif "restaurant_atmosphere" in data_dict["RESTAURANT"][list(data_dict["RESTAURANT"].keys())[0]]:
        #         found = True
        #         return make_dict_variable_values(data_dict["RESTAURANT"], "restaurant_atmosphere")
        
        # missing variable
        print(f"variable {variable_name} is missing")
        return ''


def fill_hotel_data(hotel_data_template, data_dict):
    filled_hotel_data = deepcopy(hotel_data_template)
    for page in hotel_data_template:
        try:
            if page == "WEDDINGS LP":
                continue  # Skip filling for "WEDDING LP" page
            for section in hotel_data_template[page]:
                for variable in hotel_data_template[page][section]['bloc_data']:
                    filled_hotel_data[page][section]['bloc_data'][variable] = get_bloc_data_variable(data_dict, variable) 
        except Exception as e:
            print(f"Error at page {page} and section {section}")
            raise e                  

    return filled_hotel_data


# Nested Data Dict
# def clean_useless_separator_lines(df):
#     def all_non_breaking_space(row):
#         return all(x == '\xa0' for x in row)
    
#     # Remove all NaN rows (useless separating rows)
#     df = df.dropna(how='all')

#     # Apply the function to each row
#     row_condition = df.apply(all_non_breaking_space, axis=1)

#     # Filter out rows that contain only '\xa0'
#     df = df[~row_condition]
    
#     return df

# def clean_useless_separator_lines(df):
#     def is_empty_or_nbsp(x):
#         return pd.isna(x) or x == '\xa0' or x == ''
    
#     def all_empty_or_nbsp(row):
#         return all(is_empty_or_nbsp(x) for x in row)
    
#     # Remove all rows where every entry is either NaN or '\xa0'
#     row_condition = df.apply(all_empty_or_nbsp, axis=1)
#     df = df[~row_condition]
    
#     return df

# def make_nested_item_variables(item_df):
#     tmp_non_nested_data_dict = make_non_nested_tab_variables(item_df.iloc[:, 1:])
    
#     return {
#         tmp_non_nested_data_dict[list(tmp_non_nested_data_dict.keys())[0]]['value']: tmp_non_nested_data_dict
#     }    
    
# def make_nested_tab_variables(survey_tab, key_depth, name):
#     tab_variables = {}
    
#     df = deepcopy(survey_tab)

#     # Remove useless separating rows NaN and '\xao'
#     df = clean_useless_separator_lines(df)
    
#     # Identify rows that start a new key element (resto, room, mice, ...)
#     non_nan_mask = df.iloc[:, 0].notna()
#     non_nan_indices = df.index[non_nan_mask].tolist()
    
#     for key_idx in non_nan_indices:
#         # print("key_idx", key_idx)
#         # print("key_depth", key_depth)
#         # logging.debug("key_idx: %s", key_idx)
#         # logging.debug("key_depth: %s", key_depth)
        
#         # print("DataFrame before selecting rows:\n", df)
#         # logging.debug("DataFrame before selecting rows:\n%s", df)
        
        
#         print(f"key_idx: {key_idx}, key_depth: {key_depth},total rows: {len(df)}")
#         item_df = df.loc[range(key_idx, key_idx + key_depth)]
#         # print("DataFrame after selecting rows:\n", item_df)
#         # logging.debug("DataFrame after selecting rows:\n%s", item_df)
#         tab_variables = tab_variables | make_nested_item_variables(item_df)

#     return {name: tab_variables}
    
# def make_nested_data_dict(survey):
#     nested_data_dict = {}
    
#     nested_tabs = ['Restaurants', 'Rooms', 'MICE', 'Homepage - Meetings & Events ', 'Homepage - Other Services']

#     key_depth_mapping = {
#         "Restaurants": 12,
#         "Homepage - Meetings & Events ": 7,
#         "Homepage - Other Services": 3,
#         "Rooms": 12,
#         "MICE": 8
#     }
    
#     name_mapping = {
#         "Restaurants": "RESTAURANT",
#         "Rooms": "ROOM",
#         "MICE": "MICE",
#         "Homepage - Other Services" : "OTHER SERVICE HP",
#         "Homepage - Meetings & Events ": "MICE HP"
#     }
    
#     for tab in nested_tabs:
#         try:
#             if tab == "MICE":
#                 nested_data_dict = nested_data_dict | make_nested_tab_variables(survey[tab].iloc[5:, :], key_depth_mapping[tab], name_mapping[tab])
#             else:
#                 nested_data_dict = nested_data_dict | make_nested_tab_variables(survey[tab], key_depth_mapping[tab], name_mapping[tab])
#         except Exception as e:
#             print(f'Index Error at tab {tab}')
#             raise e
    
#     return nested_data_dict

def get_list_from_parameters(full_data_dict, category, variable_listed):
    return [full_data_dict[category][elt][variable_listed]['value'] for elt in full_data_dict[category]]

# def get_mice_hp_list_variables(full_data_dict):
#     mice_hp_list_variables = {}
    
#     wedding_instances = [key for key in full_data_dict["MICE HP"].keys() if "wedding" in list(full_data_dict['MICE HP'][key].keys())[0]]
#     event_instances = [key for key in full_data_dict['MICE HP'].keys() if "event" in list(full_data_dict['MICE HP'][key].keys())[0]]
        
#     # Event case
#     mice_hp_list_variables["list_event_name"] = {
#         "value": [full_data_dict['MICE HP'][event_key]["event_name"]['value'] for event_key in event_instances],
#         "description": "list of event names proposed by the hotel"
#     }
#     mice_hp_list_variables["list_event_usp"] = {
#         "value": [full_data_dict['MICE HP'][event_key]["event_usp"]['value'] for event_key in event_instances],
#         "description": "list of event usp proposed by the hotel"
#     }
#     mice_hp_list_variables["list_event_type"] = {
#         "value": [full_data_dict['MICE HP'][event_key]["event_type"]['value'] for event_key in event_instances],
#         "description": "list of event type proposed by the hotel"      
#         }
#     mice_hp_list_variables["list_event_services"] = {
#         "value": [full_data_dict['MICE HP'][event_key]["event_services"]['value'] for event_key in event_instances],
#         "description": "list of event services proposed by the hotel"      
#     }
#     mice_hp_list_variables["list_event_services_usp"] = {
#         "value": [full_data_dict['MICE HP'][event_key]["event_services_usp"]['value'] for event_key in event_instances],
#         "description": "list of the usp of the event services proposed by the hotel"      
#     }
#     mice_hp_list_variables["list_event_catering"] = {
#         "value": [full_data_dict['MICE HP'][event_key]["event_catering"]['value'] for event_key in event_instances],
#         "description": "list of the catering services available for the events proposed by the hotel"      
#     }
#     mice_hp_list_variables["list_event_accomodation"] = {
#         "value": [full_data_dict['MICE HP'][event_key]["event_accomodation"]['value'] for event_key in event_instances],
#         "description": "list of event accomodation proposed by the hotel"      
#     }
    
#     # Wedding case
#     mice_hp_list_variables["list_wedding_name"] = {
#         "value": [full_data_dict['MICE HP'][wedding_key]["wedding_name"]['value'] for wedding_key in wedding_instances],
#         "description": "list of the names of the different weddings proposed by the hotel"
#     }
#     mice_hp_list_variables["list_wedding_event_usp"] = {
#         "value": [full_data_dict['MICE HP'][wedding_key]["wedding_event_usp"]['value'] for wedding_key in wedding_instances],
#         "description": "list of the usp of the different weddings proposed by the hotel"
#     }
#     mice_hp_list_variables["list_wedding_type"] = {
#         "value": [full_data_dict['MICE HP'][wedding_key]["wedding_type"]['value'] for wedding_key in wedding_instances],
#         "description": "list of the types of the different weddings proposed by the hotel"
#     }
#     mice_hp_list_variables["list_wedding_services"] = {
#         "value": [full_data_dict['MICE HP'][wedding_key]["wedding_services"]['value'] for wedding_key in wedding_instances],
#         "description": "list of the services of the different weddings proposed by the hotel"
#     }
#     mice_hp_list_variables["list_wedding_services_usp"] = {
#         "value": [full_data_dict['MICE HP'][wedding_key]["wedding_services_usp"]['value'] for wedding_key in wedding_instances],
#         "description": "list of the service usp of the different wedding services proposed by the hotel"
#     }
#     mice_hp_list_variables["list_wedding_catering"] = {
#         "value": [full_data_dict['MICE HP'][wedding_key]["wedding_event_usp"]['value'] for wedding_key in wedding_instances],
#         "description": "list of the catering services of the different weddings proposed by the hotel"
#     }
#     mice_hp_list_variables["list_wedding_accomodation"] = {
#         "value": [full_data_dict['MICE HP'][wedding_key]["wedding_event_usp"]['value'] for wedding_key in wedding_instances],
#         "description": "list of the accomodation available for the different weddings proposed by the hotel"
#     }
    
#     return mice_hp_list_variables

# def get_mice_hp_list_variables(full_data_dict):
#     def get_value_or_blank(data, key, instance):
#         """Helper function to get the value or return a blank if the key is missing."""
#         if key in data['MICE HP'][instance]:
#             return data['MICE HP'][instance][key]['value']
#         else:
#             print(f"Missing '{key}' for {instance}")
#             return ''

#     mice_hp_list_variables = {}
    
#     wedding_instances = [key for key in full_data_dict["MICE HP"].keys() if "wedding" in list(full_data_dict['MICE HP'][key].keys())[0]]
#     event_instances = [key for key in full_data_dict['MICE HP'].keys() if "event" in list(full_data_dict['MICE HP'][key].keys())[0]]
    
#     # Event case
#     mice_hp_list_variables["list_event_name"] = {
#         "value": [get_value_or_blank(full_data_dict, "event_name", event_key) for event_key in event_instances],
#         "description": "list of event names proposed by the hotel"
#     }
#     mice_hp_list_variables["list_event_usp"] = {
#         "value": [get_value_or_blank(full_data_dict, "event_usp", event_key) for event_key in event_instances],
#         "description": "list of event usp proposed by the hotel"
#     }
#     mice_hp_list_variables["list_event_type"] = {
#         "value": [get_value_or_blank(full_data_dict, "event_type", event_key) for event_key in event_instances],
#         "description": "list of event type proposed by the hotel"      
#     }
#     mice_hp_list_variables["list_event_services"] = {
#         "value": [get_value_or_blank(full_data_dict, "event_services", event_key) for event_key in event_instances],
#         "description": "list of event services proposed by the hotel"      
#     }
#     mice_hp_list_variables["list_event_services_usp"] = {
#         "value": [get_value_or_blank(full_data_dict, "event_services_usp", event_key) for event_key in event_instances],
#         "description": "list of the usp of the event services proposed by the hotel"      
#     }
#     mice_hp_list_variables["list_event_catering"] = {
#         "value": [get_value_or_blank(full_data_dict, "event_catering", event_key) for event_key in event_instances],
#         "description": "list of the catering services available for the events proposed by the hotel"      
#     }
#     mice_hp_list_variables["list_event_accomodation"] = {
#         "value": [get_value_or_blank(full_data_dict, "event_accomodation", event_key) for event_key in event_instances],
#         "description": "list of event accomodation proposed by the hotel"      
#     }
    
#     # Wedding case
#     mice_hp_list_variables["list_wedding_name"] = {
#         "value": [get_value_or_blank(full_data_dict, "wedding_name", wedding_key) for wedding_key in wedding_instances],
#         "description": "list of the names of the different weddings proposed by the hotel"
#     }
#     mice_hp_list_variables["list_wedding_event_usp"] = {
#         "value": [get_value_or_blank(full_data_dict, "wedding_event_usp", wedding_key) for wedding_key in wedding_instances],
#         "description": "list of the usp of the different weddings proposed by the hotel"
#     }
#     mice_hp_list_variables["list_wedding_type"] = {
#         "value": [get_value_or_blank(full_data_dict, "wedding_type", wedding_key) for wedding_key in wedding_instances],
#         "description": "list of the types of the different weddings proposed by the hotel"
#     }
#     mice_hp_list_variables["list_wedding_services"] = {
#         "value": [get_value_or_blank(full_data_dict, "wedding_services", wedding_key) for wedding_key in wedding_instances],
#         "description": "list of the services of the different weddings proposed by the hotel"
#     }
#     mice_hp_list_variables["list_wedding_services_usp"] = {
#         "value": [get_value_or_blank(full_data_dict, "wedding_services_usp", wedding_key) for wedding_key in wedding_instances],
#         "description": "list of the service usp of the different wedding services proposed by the hotel"
#     }
#     mice_hp_list_variables["list_wedding_catering"] = {
#         "value": [get_value_or_blank(full_data_dict, "wedding_catering", wedding_key) for wedding_key in wedding_instances],
#         "description": "list of the catering services of the different weddings proposed by the hotel"
#     }
#     mice_hp_list_variables["list_wedding_accomodation"] = {
#         "value": [get_value_or_blank(full_data_dict, "wedding_accomodation", wedding_key) for wedding_key in wedding_instances],
#         "description": "list of the accomodation available for the different weddings proposed by the hotel"
#     }
#     return mice_hp_list_variables

# def get_additional_list_variables(full_data_dict):    
#     added_variable_list = {
#         'list_restaurant_name': {
#             'value': get_list_from_parameters(full_data_dict, 'RESTAURANT', 'restaurant_name'),
#             'description': "Full list of restaurants of the hotel"
#         },
#         'list_restaurant_athmosphere': {
#             'value': get_list_from_parameters(full_data_dict, 'RESTAURANT', "restaurant_athmosphere"),
#             'description': "Full list of restaurant athmosphere of the hotel"
#         },
#         'list_restaurant_usp': {
#             "value": get_list_from_parameters(full_data_dict, 'RESTAURANT', 'restaurant_usp'),
#             "description": "List of all restaurant usp of the hotel"
#         },
#         'list_service_type': {
#             "value": get_list_from_parameters(full_data_dict, 'OTHER SERVICE HP', 'service_type'),
#             "description": 'list of all service type of the hotel'
#         },
#         'list_service_usp': {
#             "value": get_list_from_parameters(full_data_dict, 'OTHER SERVICE HP', 'service_usp'),
#             "description": "list of all the usp for every service proposed by the hotel"
#         },
#         'list_room_name': {
#             "value": get_list_from_parameters(full_data_dict, 'ROOM', 'room_name'),
#             'description': 'list of all room names of the hotel'
#         },
#         'list_room_usp': {
#             "value": get_list_from_parameters(full_data_dict, 'ROOM', 'room_usp'),
#             "description": "list of the usp for every room of the hotel"
#         },
#         'list_room_view': {
#             "value": get_list_from_parameters(full_data_dict, 'ROOM', 'room_view'),
#             'description': 'list of all different room views for every room of the hotel'
#         },
#         'list_mice_name': {
#             'value': get_list_from_parameters(full_data_dict, 'MICE', 'mice_name'),
#             "description": "list of the name for every MICE in the hotel"
#         },
#         'list_mice_usp': {
#             'value': get_list_from_parameters(full_data_dict, 'MICE', 'meeting_room_usp'),
#             'description': 'list of the usp for every MICE of the hotel'
#         },
#         'list_mice_amenities': {
#             'value': get_list_from_parameters(full_data_dict, 'MICE', 'mice_amenities'),
#             'description': 'list of the amenities for every MICE of the hotel'
#         },
#         'list_mice_type': {
#             'value': get_list_from_parameters(full_data_dict, 'MICE', 'meeting_room_type'),
#             'description': 'list of all types of MICE available at the hotel'
#         },
#         'sustainability_usp': {
#             'value': "",
#             'description': "sustainability usp of the hotel"
#         },
#         'brand_level_loyalty': {
#             'value': 'UNKNOWN',
#             'description': 'loyalty program and perks for Pullman hotels'
#         }
#     } | get_mice_hp_list_variables(full_data_dict)
#     return added_variable_list

# def reprocess_featured_venues_list(value):
#     class CorrectedList(BaseModel):
#         corrected_list: list[str] = Field(description="The extracted list of hotel venues.")

#     output_parser = JsonOutputParser(pydantic_object=CorrectedList)
    
#     reprocessing_system_prompt = "You are a helpful assistant. Your task is to extract a list of venue names from the text provided."
#     reprocessing_human_prompt = """Please extract the list of venue names from the provided hotel information. The list should contain 4 venues in it unless it obviously has less or none. 
#     <hotel_information>
#     {value}
#     </hotel_information>
    
    
#     {format_instructions}
#     """
#     prompt = ChatPromptTemplate(
#         messages=[
#             SystemMessagePromptTemplate.from_template(reprocessing_system_prompt),
#             HumanMessagePromptTemplate.from_template(reprocessing_human_prompt)
#         ],
#         input_variables=["value"],
#         partial_variables={"format_instructions": output_parser.get_format_instructions()}
#     ) 
#     # processed_featured_venues_list_chain_fallback = prompt | ChatOpenAI(model_name="gpt-4-turbo", temperature=0) | output_parser
#     processed_featured_venues_list_chain_base = prompt | choose_model("4-turbo") | output_parser
#     # processed_featured_venues_list_chain = processed_featured_venues_list_chain_base.with_fallbacks([processed_featured_venues_list_chain_fallback])
#     processed_featured_venues_list_output = processed_featured_venues_list_chain_base.invoke({"value": value})
#     return processed_featured_venues_list_output['corrected_list']


# def make_data_dict(survey, save=True):
#     # Add Nested and Non Nested Variables from Survey
#     full_data_dict = make_non_nested_data_dict(survey) | make_nested_data_dict(survey)

#     # FIX SPELLING
#     if "restaurant_atmosphere" in full_data_dict['RESTAURANT'][list(full_data_dict['RESTAURANT'].keys())[0]]:
#         for instance in full_data_dict['RESTAURANT']:
#             full_data_dict['RESTAURANT'][instance]['restaurant_athmosphere'] = full_data_dict['RESTAURANT'][instance]['restaurant_athmosphere']
#             del full_data_dict['RESTAURANT'][instance]['restaurant_atmosphere']
            
#     if "major_rail_station" in full_data_dict:
#         full_data_dict["major_rail_stations"] = full_data_dict['major_rail_station']
#         del full_data_dict['major_rail_station']
    
#     if "taxi_or_shuttle_availabilty" in full_data_dict:
#         full_data_dict["taxi_or_shuttle_availability"] = full_data_dict["taxi_or_shuttle_availabilty"]
#         del full_data_dict["taxi_or_shuttle_availabilty"]
        
#     if "check_if_room_is_accessible_yesno" in full_data_dict["ROOM"][list(full_data_dict['ROOM'].keys())[0]]:
#         for instance in full_data_dict['ROOM']:
#             full_data_dict['ROOM'][instance]["check_if_room_is_accessible_(yes_/_no)"] = full_data_dict['ROOM'][instance]["check_if_room_is_accessible_yesno"]
#             del full_data_dict['ROOM'][instance]["check_if_room_is_accessible_yesno"]
    
#     # Add aditional list variables
#     full_data_dict = full_data_dict | get_additional_list_variables(full_data_dict)
#     full_data_dict['mice_featured_venues_list']['value'] = reprocess_featured_venues_list(full_data_dict['mice_featured_venues_list']['value'])
#     # Save data dict
#     if save:
#         with open(os.path.join(os.getcwd(), "data", "data_dict", "data_dict.json"), "w") as f:
#             json.dump(full_data_dict, f)
    
#     return full_data_dict
    

# # Make Hotel Data Template
# EXCEL_FOLDER = os.path.join(os.getcwd(), "data", "excels")
# assert os.path.join(EXCEL_FOLDER)

# DMT_PATH = os.path.join(EXCEL_FOLDER, "data_mapping_template.xlsx")
# assert os.path.exists(DMT_PATH)

# def get_page_dmt(dmt, page):
#     return dmt[dmt['Page'] == page]

# def get_section_dmt(dmt, page, section):
#     page_dmt = get_page_dmt(dmt, page)
#     return page_dmt[page_dmt['SECTION.1'] == section]

# # Make Bloc Structure
# def make_section_structure(dmt, page, section):
#     section_dmt = get_section_dmt(dmt, page, section)
#     elements = section_dmt['Content Name'].unique()
#     return {
#         element.lower().strip(' ').replace(' ', '_'): {} 
#         for element in elements
#         }
    
# def make_reference_structure(dmt, save=True):
#     reference_structure = {}
#     for page in dmt['Page'].unique():
#         tmp_page = {}
#         for section in dmt[dmt['Page'] == page]['SECTION.1'].unique():
#             tmp_page[section] = make_section_structure(dmt, page, section)
#         reference_structure[page] = tmp_page
    
#     if save:
#         with open(os.path.join(os.getcwd(), "data", "structure", "reference_structure.json"), "w") as f:
#             json.dump(reference_structure, f)

#     return reference_structure

def make_bloc_structure(bloc):
    nested_structure = ""
    non_nested_structure = ""
    for element in bloc:
        if "item" in element or "carousel" in element:
            nested_structure += element + "-"
            
            # Add carousel or item to the non nested structure
            if "item" in element:
                if not "item" in non_nested_structure:
                    non_nested_structure += "item" + "-"
            elif "carousel" in element:
                if not "carousel" in non_nested_structure:
                    non_nested_structure += "carousel" + "-"
            else: 
                raise NotImplementedError
        else:
            non_nested_structure += element + "-"
    return {
        "non_nested_structure": non_nested_structure.strip('-'),
        "nested_structure": nested_structure.strip('-')
    }

# def get_bloc_structure(data_structure, reference_structure):
#     bloc_structure_enriched_structure = deepcopy(data_structure)
#     for page in reference_structure:
#         for section in reference_structure[page]:
#             bloc_structure_enriched_structure[page][section]['bloc_structure_string'] = make_bloc_structure(reference_structure[page][section])
#     return bloc_structure_enriched_structure

# def nettoyer_texte(texte):
#     """Fonction pour nettoyer le texte, en remplaçant les sauts de ligne et les guillemets."""
#     return texte.replace('\n', ' ').replace('"', "'")

# # Make bloc
# def get_element_guidelines(dmt, page, section, element):
#     element_guidelines = dmt[(dmt['Page'] == page) & (dmt['SECTION.1'] == section) & (dmt['Content Name'] == element)]
#     if len(element_guidelines) == 0:
#         raise ValueError(f"Problem found at page {page} and section {section} and element {element}")
            
#     return {
#         "nb_characters": nettoyer_texte(element_guidelines['Content Length'].values[0]),
#         "content_guidelines": nettoyer_texte(element_guidelines['Content Guidelines'].values[0]),
#         "reference_content": nettoyer_texte(element_guidelines['Reference Content'].values[0])
#     }

# def get_guidelines(dmt, reference_structure):
#     guidelines = {}
#     for page in reference_structure:
#         tmp_page = {}
#         for section in reference_structure[page]:
#             tmp_section = {}
#             for element in reference_structure[page][section]:
#                 tmp_section[element] = get_element_guidelines(dmt, page, section, element)
#             tmp_page[section] = tmp_section
#         guidelines[page] = tmp_page
#     return guidelines

# def make_guidelines(dmt, reference_structure):
#     enriched_structure = {}
#     guidelines = get_guidelines(dmt, reference_structure)
#     for page in reference_structure:
#         tmp_page = {}
#         for section in reference_structure[page]:
#             tmp_page[section] = {'bloc_guidelines': guidelines[page][section]}
#         enriched_structure[page] = tmp_page
#     return enriched_structure

# # Make Bloc Data
# def make_list_bloc_data_variable(dmt, page, section):
#     dmt_page = dmt[dmt['Page'] == page]
#     dmt_section = dmt_page[dmt_page['SECTION.1'] == section]
#     tmp_list = [elt for elt in dmt_section['Variables'].unique().tolist() if elt]
#     bloc_data_variable_list = []
#     for elt in tmp_list:
#         if ',' in elt:
#             sub_elts = [sub_elt.strip(' ') for sub_elt in elt.split(',')]
#             bloc_data_variable_list.extend(sub_elts)
#         else:
#             bloc_data_variable_list.append(elt)
#     return bloc_data_variable_list
            
# def make_bloc_data(dmt, structure):
#     bloc_data_enriched_structure = deepcopy(structure)
#     for page in bloc_data_enriched_structure:
#         for section in bloc_data_enriched_structure[page]:
#             bloc_data_enriched_structure[page][section]['bloc_data'] = {}
             
#             bloc_variable_list = make_list_bloc_data_variable(dmt, page, section)
            
#             if len(bloc_variable_list):
#                 for variable in bloc_variable_list:
#                     bloc_data_enriched_structure[page][section]['bloc_data'][variable] = {}
    
#     return bloc_data_enriched_structure

# # Make Hotel Data Template
# def make_hotel_data_template(dmt_structure, dmt_guidelines, dmt_variables, save=True):
#     # Base structure
#     reference_structure = make_reference_structure(dmt_structure)
    
#     # Add guidelines
#     hotel_data_template = make_guidelines(dmt_guidelines, reference_structure)
    
#     # Add bloc structure
#     hotel_data_template = get_bloc_structure(hotel_data_template, reference_structure)
    
#     # Add bloc data
#     hotel_data_template = make_bloc_data(dmt_variables, hotel_data_template)
    
#     # Save
#     if save:
#         with open(os.path.join(os.getcwd(), "data", "hotel_data_template", "hotel_data_template.json"), "w") as f:
#             json.dump(hotel_data_template, f)
    
#     return hotel_data_template
