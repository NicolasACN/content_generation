import os 
from typing import List
from operator import itemgetter
import openai
from dotenv import find_dotenv, load_dotenv
# from .utils import load_message_prompts, read_file, make_variable_sentence
from langchain_core.pydantic_v1 import BaseModel, Field, create_model
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import JsonOutputParser


load_dotenv(find_dotenv())
openai.api_key = os.getenv("OPENAI_API_KEY")

# # PROMPT LOADING
# PROMPT_FOLDER_PATH = os.path.join(os.getcwd(), 'prompts')
# assert os.path.exists(PROMPT_FOLDER_PATH)
# ## Path
# writing_prompt_path = os.path.join(PROMPT_FOLDER_PATH, 'Copywriting')
# rewriting_prompt_path = os.path.join(PROMPT_FOLDER_PATH, 'Rewriter')
# bm_review_and_feedback_prompt_path = os.path.join(PROMPT_FOLDER_PATH, 'BMReview')
# cw_review_and_feedback_prompt_path = os.path.join(PROMPT_FOLDER_PATH, 'CWReview')
# tov_review_and_feedback_prompt_path = os.path.join(PROMPT_FOLDER_PATH, "TOVReview")
# # validation_prompt_path = os.path.join(PROMPT_FOLDER_PATH, 'Validation')
# seo_keywords_prompt_path = os.path.join(PROMPT_FOLDER_PATH, "SEOKeywords")
# seo_writer_prompt_path = os.path.join(PROMPT_FOLDER_PATH, "SEOWriter")
# lexicon_post_processing_prompt_path = os.path.join(PROMPT_FOLDER_PATH, "LexiconPostProcessor")
# ## Prompts
# bm_review_and_feedback_system_message_prompt, bm_review_and_feedback_human_message_prompt  = load_message_prompts(bm_review_and_feedback_prompt_path)
# cw_review_and_feedback_system_message_prompt, cw_review_and_feedback_human_message_prompt = load_message_prompts(cw_review_and_feedback_prompt_path)
# tov_review_and_feedback_system_message_prompt, tov_review_and_feedback_human_message_prompt = load_message_prompts(tov_review_and_feedback_prompt_path)
# writing_system_message_prompt, writing_human_message_prompt = load_message_prompts(writing_prompt_path)
# rewriting_system_message_prompt, rewriting_human_message_prompt = load_message_prompts(rewriting_prompt_path)
# #validation_system_message_prompt, validation_human_message_prompt = load_message_prompts(validation_prompt_path)
# seo_keywords_system_message_prompt, seo_keywords_human_message_prompt = load_message_prompts(seo_keywords_prompt_path)
# seo_writer_system_message_prompt, seo_writer_human_message_prompt = load_message_prompts(seo_writer_prompt_path)
# lexicon_post_processing_system_message_prompt_template, lexicon_post_processing_human_message_prompt_template = load_message_prompts(lexicon_post_processing_prompt_path)

# # SECTION CW GUIDELINES LOADING
# GUIDELINES_FOLDER = os.path.join(os.getcwd(), 'data', "guidelines")
# assert os.path.exists(GUIDELINES_FOLDER)
# # CW Guidelines
# with open(os.path.join(GUIDELINES_FOLDER, "cw", "cw_guidelines_general.txt"), "r") as f: 
#     cw_guidelines_general = f.read()

# with open(os.path.join(GUIDELINES_FOLDER, "cw", "cw_guidelines_mice.txt"), "r") as f:
#     cw_guidelines_mice = f.read()

# with open(os.path.join(GUIDELINES_FOLDER, "cw", 'cw_guidelines_room.txt'), "r") as f:
#     cw_guidelines_room = f.read()

# with open(os.path.join(GUIDELINES_FOLDER, "cw", "cw_guidelines_restaurant.txt"), "r") as f:
#     cw_guidelines_restaurant = f.read()

# with open(os.path.join(GUIDELINES_FOLDER, "cw", "cw_guidelines_wellness.txt"), "r") as f: 
#     cw_guidelines_wellness = f.read()

# # PAGE CW GUIDELINES LOADING 
# PAGE_CW_GUIDELINES_FOLDER = os.path.join(os.getcwd(), "data", "guidelines", "page_guidelines")
# assert os.path.exists(PAGE_CW_GUIDELINES_FOLDER)

# with open(os.path.join(PAGE_CW_GUIDELINES_FOLDER, "HOMEPAGE_cw_guidelines.txt"), "r") as f:
#     homepage_cw_guidelines = f.read()
    
# with open(os.path.join(PAGE_CW_GUIDELINES_FOLDER, "MICE_DP_cw_guidelines.txt"), "r") as f:
#     mice_dp_cw_guidelines = f.read()

# with open(os.path.join(PAGE_CW_GUIDELINES_FOLDER, "MICE_LP_cw_guidelines.txt"), "r") as f:
#     mice_lp_cw_guidelines = f.read()
     
# with open(os.path.join(PAGE_CW_GUIDELINES_FOLDER, "RESTAURANT_DP_cw_guidelines.txt"), "r") as f:
#     restaurant_dp_cw_guidelines = f.read()

# with open(os.path.join(PAGE_CW_GUIDELINES_FOLDER, "ROOM_DP_cw_guidelines.txt"), "r") as f:
#     room_dp_cw_guidelines = f.read()

# with open(os.path.join(PAGE_CW_GUIDELINES_FOLDER, "WELLNESS_LP_cw_guidelines.txt"), "r") as f:
#     wellness_lp_cw_guidelines = f.read()

# with open(os.path.join(PAGE_CW_GUIDELINES_FOLDER, "WEDDINGS_LP_cw_guidelines.txt"), "r") as f:
#     weddings_lp_cw_guidelines = f.read()

# # KEYWORD GUIDELINES LOADING
# KEYWORD_GUIDELINES_FOLDER = os.path.join(os.getcwd(), "data", "guidelines", "seo", "keywords")
# assert os.path.exists(KEYWORD_GUIDELINES_FOLDER)

# with open(os.path.join(KEYWORD_GUIDELINES_FOLDER, "homepage.txt"), "r") as f:
#     homepage_keywords_guidelines = f.read()
    
# with open(os.path.join(KEYWORD_GUIDELINES_FOLDER, "mice_dp.txt"), "r") as f:
#     mice_dp_keywords_guidelines = f.read()

# with open(os.path.join(KEYWORD_GUIDELINES_FOLDER, "mice_lp.txt"), "r") as f:
#     mice_lp_keywords_guidelines = f.read()
     
# with open(os.path.join(KEYWORD_GUIDELINES_FOLDER, "restaurant_dp.txt"), "r") as f:
#     restaurant_dp_keywords_guidelines = f.read()

# with open(os.path.join(KEYWORD_GUIDELINES_FOLDER, "room_dp.txt"), "r") as f:
#     room_dp_keywords_guidelines = f.read()

# with open(os.path.join(KEYWORD_GUIDELINES_FOLDER, "wellness_lp.txt"), "r") as f:
#     wellness_lp_keywords_guidelines = f.read()

# with open(os.path.join(KEYWORD_GUIDELINES_FOLDER, "weddings_lp.txt"), "r") as f:
#     weddings_lp_keywords_guidelines = f.read()

# # SEO GUIDELINES LOADING
# SEO_GUIDELINES_FOLDER = os.path.join(os.getcwd(), "data", "guidelines", "seo", "guidelines")
# assert os.path.exists(SEO_GUIDELINES_FOLDER)

# with open(os.path.join(SEO_GUIDELINES_FOLDER, "seo_guidelines.txt"), "r") as f:
#     seo_guidelines = f.read()

# # REFERENCE CONTENT LOADING
# REFERENCE_COPY_FOLDER = os.path.join(os.getcwd(), "data", "reference_copies")
# assert os.path.exists(REFERENCE_COPY_FOLDER)

# with open(os.path.join(REFERENCE_COPY_FOLDER, "reference_homepage.txt"), "r") as f:
#     reference_homepage = f.read()

# with open(os.path.join(REFERENCE_COPY_FOLDER, "reference_mice_dp.txt"), "r") as f:
#     reference_mice_dp = f.read()

# with open(os.path.join(REFERENCE_COPY_FOLDER, "reference_mice_lp.txt"), "r") as f:
#     reference_mice_lp = f.read()
    
# with open(os.path.join(REFERENCE_COPY_FOLDER, "reference_restaurant_dp.txt"), "r") as f:
#     reference_restaurant_dp = f.read()

# with open(os.path.join(REFERENCE_COPY_FOLDER, "reference_room_dp.txt"), "r") as f:
#     reference_room_dp = f.read()
    
# with open(os.path.join(REFERENCE_COPY_FOLDER, "reference_wellness_lp.txt"), "r") as f:
#     reference_wellness_lp = f.read()

# with open(os.path.join(REFERENCE_COPY_FOLDER, "reference_weddings_lp.txt"), "r") as f:
#     reference_weddings_lp = f.read()

# # BM GUIDELINES LOADING
# bm_guidelines = read_file(os.path.join(os.getcwd(), GUIDELINES_FOLDER, "bm", 'bm_guidelines.txt'))

# Pydantic Models 
class Feedback(BaseModel):
    general_feedback: str = Field(description="General feedback on the copywriter's written copy")
    specific_feedback: str = Field(description="Specific feedback on precise parts of the copywriter's written copy")
    improvement_directions: str = Field(description="List of clear directive instructions for the copywriter to improve the next copy")
    
#class Validation(BaseModel):
#    validation: bool = Field(description="True for  if feedback corresponds to validation and False for rejection. If unsure then False.")
    
class SEOKeywords(BaseModel):
    keyword_list: List[str] = Field(description="List of target SEO keywords for the hotel page")

class SEOSection(BaseModel):
    meta_title: str = Field(description="The Meta Title of the page")
    meta_description: str = Field(description="The Meta Description of the page")

class CorrectedText(BaseModel):
    corrected_text: str = Field(description="The corrected text")

    
def choose_model(model_name: str):
    if model_name == "3.5" or model_name == "3.5-turbo" or model_name == "gpt-3.5-turbo":
        return ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    elif model_name == "4":
        return ChatOpenAI(model_name="gpt-4", temperature=0)
    elif model_name == "4-turbo" or model_name == "gpt-4-turbo":
        return ChatOpenAI(model_name="gpt-4-turbo", temperature=0)
    elif model_name == "4o":
        return ChatOpenAI(model_name="gpt-4o", temperature=0).with_fallbacks([choose_model("4-turbo")])
    else:
        raise ValueError("Invalid model_name ")
    
def make_bloc_model_from_structure(structure):
    # TODO add missing section from trial and error
    field_dict = {
        'title': "The title of the section",
        'description': "The description of the section",
        'kicker': "The kicker of the section",
        'cta': "The CTA text label of the section",
        'image_label': "The text label of the image of the section",
        'carousel': f"The item list of the section. Composed of carousel items eached one composed of a {structure['nested_structure'].replace('-', 'a ')}",
        'carousel_title': "The title of the carousel item",
        'carousel_description': "The description of the carousel item",
        'carousel_kicker': "The kicker of the carousel item",
        'carousel_cta': "The CTA text label of the carousel item ",
        'item': f"The item list of the section. Composed of carousel items eached one composed of a {structure['nested_structure'].replace('-', 'a ')}",
        'item_title': "The title of an individual item of the item list",
        'item_value': "The value of an individual item of the item list",
        'details_room_accessibility': "The room accessibility information for the room",
        'details_room_capacity': "The room capacity information for the room"
    }  
     
    # Nested case 
    if structure['nested_structure']:
        nested_fields = structure['nested_structure'].split('-')
        nested_model_fields = {nested_field: (str, Field(description=field_dict.get(nested_field, ""))) for nested_field in nested_fields}
        
        # Carousel case
        if 'carousel' in structure['non_nested_structure']:
            nested_item_model = create_model(
                'CarouselItemStructureModel',
                **nested_model_fields,
                __base__=BaseModel
            )

        # Item list case
        elif 'item' in structure['non_nested_structure']:
            nested_item_model = create_model(
                'ItemListItemStructureModel',
                **nested_model_fields,
                __base__=BaseModel
            )

        else:
            print(f"WARNING: found odd case for structure: {structure}")
            raise NotImplementedError
        
        # model fields creation
        model_fields = {}
        non_nested_fields = structure['non_nested_structure'].split('-')
        for field in non_nested_fields:
            # Nested field
            if field == 'carousel' or field == 'item':
                model_fields[field] = (List[nested_item_model], Field(description=field_dict.get(field, "")))
            else:
                model_fields[field] = (str, Field(description=field_dict.get(field, "")))
    
    # Non Nested case    
    else:
        fields = structure['non_nested_structure'].split('-')
        model_fields = {field: (str, Field(description=field_dict.get(field, ""))) for field in fields}
    
    bloc_model = create_model(
        'BlockStructureModel',
        **model_fields,
        __base__=BaseModel
    )
    return bloc_model

def make_bloc_generation_chain(bloc_data_prompt_formating_chain, bloc_guidelines_prompt_formating_chain, writing_chain, BM_review_feedback_chain, CW_review_feedback_chain, TOV_review_feedback_chain):
    bloc_generation_chain = (
        RunnablePassthrough.assign(
            formated_bloc_data=bloc_data_prompt_formating_chain,
            formated_bloc_guidelines=bloc_guidelines_prompt_formating_chain)
            #formated_bloc_context=bloc_context_prompt_formating_chain)
        #| RunnablePassthrough.assign(formated_bloc_data=bloc_data_prompt_formating_chain)
        #| RunnablePassthrough.assign(formated_bloc_guidelines=bloc_guidelines_prompt_formating_chain)
        #| RunnablePassthrough.assign(formated_bloc_context=bloc_context_prompt_formating_chain) # Add context
        | RunnablePassthrough.assign(generated_text=writing_chain)
        | RunnablePassthrough.assign(
            bm_review=BM_review_feedback_chain, 
            cw_review=CW_review_feedback_chain,
            tov_review=TOV_review_feedback_chain)
    )
    return bloc_generation_chain

def make_bloc_regeneration_chain(rewriting_chain, BM_review_feedback_chain, CW_review_feedback_chain, TOV_review_feedback_chain):
    bloc_regeneration_chain = (
        RunnablePassthrough.assign(generated_text=rewriting_chain)
        | RunnablePassthrough.assign(
            bm_review=BM_review_feedback_chain,
            cw_review=CW_review_feedback_chain,
            tov_review=TOV_review_feedback_chain)
    )
    return bloc_regeneration_chain

# def make_bloc_cw_guidelines_prompt_formating_chain():
#     def format_cw_guidelines(page_section):
#         page = page_section[0]
#         section = page_section[1]
        
#         # Guidelines mapping 
#         cw_guidelines = {
#             "general": cw_guidelines_general,
#             "mice": cw_guidelines_mice,
#             "restaurant": cw_guidelines_restaurant,
#             "room": cw_guidelines_room,
#             "wellness": cw_guidelines_wellness
#         }
#         # Page section mapping
#         page_section_guidelines_mapping = {
#             'HOMEPAGE': {
#                 'AWARDS': 'general',
#                 'DISCOVER OTHER HOTELS': 'general',
#                 'FAQ': 'general',
#                 'FOOD + BEVERAGE': 'restaurant',
#                 'GETTING THERE': 'general',
#                 'HERO': 'general',
#                 'INTRO': 'general',
#                 'LOYALTY': 'general',
#                 'MEETINGS + EVENTS': 'mice',
#                 'OTHER SERVICES': 'mice',
#                 'SOCIAL MEDIA': 'general',
#                 'SUITES + ROOMS + APPARTMENTS': 'room',
#                 'SUSTAINABILITY': 'general'
#             },
#             'MICE DP': {
#                 'AMENITIES': 'mice',
#                 'DISCOVER OTHER VENUES': 'mice',
#                 'DOWNLOADS': 'mice',
#                 'EDITORIAL USP': 'mice',
#                 'HERO': 'mice',
#                 'INTRO': 'mice'
#             },
#             'MICE LP': {
#                 'FEATURED VENUES': 'mice',
#                 'INTRO': 'mice',
#                 'HERO': 'mice',
#                 'MEETING PACKAGES + OFFERS': 'mice',
#                 'MEETINGS AT HOTEL NAME': 'mice',
#                 'OUR MEETING ROOMS': 'mice',
#                 'SERVICE EXPERTISE': 'mice',
#                 'SPACES FOR ALL EVENTS': 'mice'
#             },
#             'RESTAURANT DP': {
#                 'DISCOVER OTHER VENUES': 'restaurant',
#                 'DISCOVER OUR OFFERS': 'restaurant',
#                 'DOWNLOADS': 'restaurant',
#                 'HERO': 'restaurant',
#                 'INTRO': 'restaurant',
#                 'MEET THE CHEF': 'restaurant'
#             },
#         'ROOM DP': {
#             'HERO': 'room',
#             'INTRO': 'room',
#             'SUITES + ROOMS + APPARTMENTS OVERVIEW': 'room'
#             },
#         'WEDDINGS LP': {
#             'INTRO': 'mice',
#             'FOR EVERY OCCASION': 'mice',
#             'PULLMAN WEDDINGS': 'mice',
#             'SERVICE EXPERTISE': 'mice',
#             'WEDDING PACKAGES': 'mice',
#             'HERO': 'mice'
#             },
#         'WELLNESS LP': {
#             'HERO': 'wellness',
#         'INTRO': 'wellness',
#         'MENUES': 'wellness',
#         'OTHER WELLNESS FACILITIES': 'wellness'
#             }
#         }
#         guidelines_style = page_section_guidelines_mapping[page][section]
#         guidelines = cw_guidelines[guidelines_style]
#         if guidelines_style != "general":
#             guidelines += cw_guidelines_general
#         return guidelines
#     return itemgetter('page', 'section') | RunnableLambda(format_cw_guidelines)
     
def make_bloc_data_prompt_formating_chain():
    def format_data_prompt(section_data_dict):
        if section_data_dict:
            data_prompt = "Here are the information available:"
            for variable_name, variable_dict in section_data_dict.items():
                try:
                    value = variable_dict['value']
                    description = variable_dict['description']
                    
                    if isinstance(value, list):
                        formatted_value = ", ".join(value)
                    else:
                        formatted_value = value
                    
                    data_prompt += f"\n{variable_name.replace('_', ' ').title()} ({description}): {formatted_value}"
                except TypeError as e:
                    print(f"FORMAT DATA PROMPT TYPEERROR: at variable {variable_name}\nwith variable_dict {variable_dict}")
                    raise e
        else:
            data_prompt = ""
        
        return data_prompt

    bloc_data_prompt_formating = itemgetter("bloc_data") | RunnableLambda(format_data_prompt)
    return bloc_data_prompt_formating

# TODO: change bullet points ? (check impact on structure)
def make_bloc_guidelines_prompt_formating_chain():
    # Format guidelines prompt
    def format_guidelines_prompt(bloc_guidelines: dict):
        formatted_sections = []
        
        # Directement itérer sur les bloc_guidelines
        for field_name, guidelines in bloc_guidelines.items():
            nb_characters = guidelines.get('nb_characters', 'N/A')  # N/A si non défini
            content_guidelines = guidelines.get('content_guidelines', 'N/A')
            reference_content = guidelines.get('reference_content', 'N/A')

            section = (
                f"{field_name}:\n"
                f"Guidelines: {content_guidelines}\n"
                f"Maximum of characters or words: {nb_characters}\n"
                f"Here is some reference example content for {field_name} that perfectly applies the guidelines on another Pullman hotel, the copywriting style and tone of voice. Reproduce the same tone of voice and get inspiration from it without taking any hotel specific information. When creating content, make sure to tailor the content specifically to the new hotel using the information available in <section_information>, while avoiding direct references to specific services, locations, or features unique to the example provided:\n{reference_content}\n\n"
            )

            formatted_sections.append(section)

        # Création du string formaté final
        return "\n".join(formatted_sections)
    
    bloc_guidelines_prompt_formating = itemgetter("bloc_guidelines") | RunnableLambda(format_guidelines_prompt)
    return bloc_guidelines_prompt_formating

# # NEW FUNCTION chain for the context prompt
# def make_bloc_context_prompt_formating_chain():
#     # Directly define the about_what_mapping inside the function

#     def format_bloc_context(context_info):
#         page = context_info[0]
#         section = context_info[1]
#         instance_name = context_info[2]

#         about_what_mapping = {
#             "HOMEPAGE": {
#                 "AWARDS": "awards",
#                 "DISCOVER OTHER HOTELS": " s brand other hotels and resorts",
#                 "FAQ": "FAQ",
#                 "FOOD + BEVERAGE": "restaurants and food and beverage offering",
#                 "GETTING THERE": "location and how to get there",
#                 "HERO": "general info and positioning",
#                 "INTRO": "general info and positioning",
#                 "LOYALTY": "loyalty program",
#                 "MEETINGS + EVENTS": "meetings and events",
#                 "OTHER SERVICES": "services",
#                 "SOCIAL MEDIA": "social media",
#                 "SUITES + ROOMS + APPARTMENTS": "suites rooms and appartments",
#                 "SUSTAINABILITY": "sustainability efforts "
#             },
#             "MICE DP": {
#                 "AMENITIES": "MICE",
#                 "DISCOVER OTHER VENUES": "MICE",
#                 "DOWNLOADS": "MICE",
#                 "EDITORIAL USP": "MICE",
#                 "HERO": "MICE",
#                 "INTRO": "MICE"
#             },
#             "MICE LP": {
#                 "FEATURED VENUES": "MICE venues",
#                 "INTRO": "MICEs",
#                 "HERO": "MICEs",
#                 "MEETING PACKAGES + OFFERS": "MICE meeting packages and offers",
#                 "MEETINGS AT HOTEL NAME": "MICE meeting offering",
#                 "OUR MEETING ROOMS": "meeting rooms",
#                 "SERVICE EXPERTISE": "MICE service expertise",
#                 "SPACES FOR ALL EVENTS": "MICE venues and events"
#             },
#             "RESTAURANT DP": {
#                 "DISCOVER OTHER VENUES": "restaurant",
#                 "DISCOVER OUR OFFERS": "restaurant",
#                 "DOWNLOADS": "restaurant",
#                 "HERO": "restaurant",
#                 "INTRO": "restaurant",
#                 "MEET THE CHEF": "restaurant"
#             },
#             "ROOM DP": {
#                 "HERO": "room / suite / appartment",
#                 "INTRO": "room / suite / appartment",
#                 "SUITES + ROOMS + APPARTMENTS OVERVIEW": "room / suite / appartment"
#             },
#             "WEDDINGS LP": {
#                 "INTRO": "weddings offering",
#                 "FOR EVERY OCCASION": "weddings offering",
#                 "PULLMAN WEDDINGS": "weddings offering",
#                 "SERVICE EXPERTISE": "weddings service expertise",
#                 "WEDDING PACKAGES": "wedding packages",
#                 "HERO": "weddings general info"
#             },
#             "WELLNESS LP": {
#                 "HERO": "wellness and wellbeing offering",
#                 "INTRO": "wellness and wellbeing general info",
#                 "MENUES": "wellness and wellbeing downloadables",
#                 "OTHER WELLNESS FACILITIES": "wellness and wellbeing facilities"
#             }
#         }
#        # Access the specific information for the provided page and section
#         about_what = about_what_mapping.get(page, {}).get(section, 'information')

#         # Format the output string based on whether an instance name is provided
#         if instance_name:
#             formatted_text = f"{about_what} named {instance_name.lower()}"
#         else:
#             formatted_text = f"{about_what}"

#         return formatted_text
    
#     # Return a lambda that can be applied directly to generate formatted text
#     return itemgetter("page", "section", "instance_name") | RunnableLambda(format_bloc_context)

def make_writing_chain(model, bloc_structure_model, writing_system_message_prompt, writing_human_message_prompt):
    
    parser = JsonOutputParser(pydantic_object=bloc_structure_model)
    
    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(writing_system_message_prompt),
            HumanMessagePromptTemplate.from_template(writing_human_message_prompt),
        ],
        input_variables=["formated_hotel_data", "formated_bloc_guidelines", "cw_guidelines", "bm_guidelines"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    writing_chain = prompt | model | parser
    return writing_chain

def make_rewriting_chain(model, bloc_structure_model, writing_system_message_prompt, writing_human_message_prompt):
    
    parser = JsonOutputParser(pydantic_object=bloc_structure_model)
    
    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(writing_system_message_prompt),
            HumanMessagePromptTemplate.from_template(writing_human_message_prompt),
        ],
        input_variables=["bm_review", "cw_review", "tov_review", "generated_text", "formated_hotel_data", "formated_bloc_guidelines", "cw_guidelines", "bm_guidelines"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    rewriting_chain = prompt | model | parser
    return rewriting_chain

def make_BM_review_feedback_chain(model, bm_review_and_feedback_system_message_prompt, bm_review_and_feedback_human_message_prompt):
    
    parser = JsonOutputParser(pydantic_object=Feedback)

    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(bm_review_and_feedback_system_message_prompt),
            HumanMessagePromptTemplate.from_template(bm_review_and_feedback_human_message_prompt),
    ],
    input_variables=["formated_bloc_guidelines", "generated_text", "bm_guidelines"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    runnable_bm = prompt | model | parser
    runnable_bm_fallback = prompt | choose_model("4-turbo") | parser
    return runnable_bm.with_fallbacks([runnable_bm_fallback])

def make_CW_review_feedback_chain(model, cw_review_and_feedback_system_message_prompt, cw_review_and_feedback_human_message_prompt):
    
    parser = JsonOutputParser(pydantic_object=Feedback)

    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(cw_review_and_feedback_system_message_prompt),
            HumanMessagePromptTemplate.from_template(cw_review_and_feedback_human_message_prompt),
    ],
    input_variables=["formated_bloc_guidelines", "generated_text", "cw_guidelines"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    runnable_cw = prompt | model | parser
    runnable_cw_fallback = prompt | choose_model("4-turbo") | parser
    return runnable_cw.with_fallbacks([runnable_cw_fallback])

def make_TOV_review_feedback_chain(model, tov_review_and_feedback_system_message_prompt, tov_review_and_feedback_human_message_prompt):
    # def get_reference_page_copy(page):
    #     reference_copy_mapping = {
    #         "HOMEPAGE": reference_homepage,
    #         "MICE DP": reference_mice_dp,
    #         "MICE LP": reference_mice_lp,
    #         "RESTAURANT DP": reference_restaurant_dp,
    #         "ROOM DP": reference_room_dp,
    #         "WELLNESS LP": reference_wellness_lp,
    #         "WEDDINGS LP": reference_weddings_lp
    #     }
    #     return reference_copy_mapping[page]
    
    parser = JsonOutputParser(pydantic_object=Feedback)

    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(tov_review_and_feedback_system_message_prompt),
            HumanMessagePromptTemplate.from_template(tov_review_and_feedback_human_message_prompt),
    ],
    input_variables=["generated_text", "reference_content"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    #runnable_tov = RunnablePassthrough.assign(reference_content=itemgetter("page") | RunnableLambda(get_reference_page_copy)) | prompt | model | parser 
    
    runnable_tov = prompt | model | parser 

    return runnable_tov

# def make_validation_chain():
#     model = ChatOpenAI(model_name="gpt-4-0125-preview", temperature=0) # enforced gpt 4 turbo because of formating problems. DO NOT CHANGE.
#     parser = JsonOutputParser(pydantic_object=Validation)

#     prompt = ChatPromptTemplate(
#         messages=[
#             SystemMessagePromptTemplate.from_template(validation_system_message_prompt),
#             HumanMessagePromptTemplate.from_template(validation_human_message_prompt),
#         ],
#         input_variables=["generated_text", "cw_review", "bm_review", "tov_review"],
#         partial_variables={"format_instructions": parser.get_format_instructions()},
#         )
#     validation_chain = prompt | model | parser
#     return validation_chain

# TODO : SEO Related add later
# def format_keyword_guidelines(page):
#     keywords_guidelines = {
#         "HOMEPAGE": homepage_keywords_guidelines,
#         "MICE DP": mice_dp_keywords_guidelines,
#         "MICE LP": mice_lp_keywords_guidelines,
#         "RESTAURANT DP": restaurant_dp_keywords_guidelines,
#         "ROOM DP": room_dp_keywords_guidelines,
#         "WELLNESS LP": wellness_lp_cw_guidelines,
#         "WEDDINGS LP": weddings_lp_keywords_guidelines
#     }
#     return keywords_guidelines[page]

# def format_page_cw_guidelines(page):
#     cw_guidelines = {
#         "HOMEPAGE": homepage_cw_guidelines,
#         "MICE DP": mice_dp_cw_guidelines,
#         "MICE LP": mice_lp_cw_guidelines,
#         "RESTAURANT DP": restaurant_dp_cw_guidelines,
#         "ROOM DP": room_dp_cw_guidelines,
#         "WELLNESS LP": wellness_lp_cw_guidelines,
#         "WEDDINGS LP": weddings_lp_cw_guidelines 
#     }
#     return cw_guidelines[page]

# TODO : SEO add later
# def make_seo_keywords_generation_chain(model):

#     output_parser = JsonOutputParser(pydantic_object=SEOKeywords)
    
#     prompt = ChatPromptTemplate(
#         messages=[
#             SystemMessagePromptTemplate.from_template(seo_keywords_system_message_prompt),
#             HumanMessagePromptTemplate.from_template(seo_keywords_human_message_prompt)
#         ],
#         input_variables=["cw_guidelines", "keywords_guidelines", "page", "formated_page_content"],
#         partial_variables={"format_instructions": output_parser.get_format_instructions()}
#     )
    
#     return (
#         RunnablePassthrough.assign(
#             formated_page_content= itemgetter("page_content") | RunnableLambda(format_page), 
#             cw_guidelines = itemgetter('page') | RunnableLambda(format_page_cw_guidelines),
#             keywords_guidelines = itemgetter('page') | RunnableLambda(format_keyword_guidelines), 
#         ) | RunnablePassthrough.assign(keyword_list=prompt | model | output_parser | itemgetter('keyword_list'))
#     ) 
    
# def make_seo_section_generation_chain(model):
#     seo_section_output_parser = JsonOutputParser(pydantic_object=SEOSection)

#     seo_section_prompt = ChatPromptTemplate(
#         messages=[
#             SystemMessagePromptTemplate.from_template(seo_writer_system_message_prompt),
#             HumanMessagePromptTemplate.from_template(seo_writer_human_message_prompt)
#         ],
#         input_variables=["page", "formated_page_content", "keyword_list", "seo_guidelines", "cw_guidelines"],
#         partial_variables={"format_instructions": seo_section_output_parser.get_format_instructions()}
#     )
    
#     seo_keywords_generation_chain = make_seo_keywords_generation_chain(model)
    
#     return (
#         RunnablePassthrough.assign(seo_guidelines=lambda x: seo_guidelines)
#         | seo_keywords_generation_chain
#         | seo_section_prompt | model | seo_section_output_parser
#     )

# TODO : Lexicon post processing add later    
# def make_lexicon_post_processing_chain(model):
#     output_parser = JsonOutputParser(pydantic_object=CorrectedText)
    
#     prompt = ChatPromptTemplate(
#         messages=[
#             SystemMessagePromptTemplate.from_template(lexicon_post_processing_system_message_prompt_template),
#             HumanMessagePromptTemplate.from_template(lexicon_post_processing_human_message_prompt_template)
#         ],
#         input_variables=["cw_guidelines", "generated_text"],
#         partial_variables={"format_instructions": output_parser.get_format_instructions()}
#     )
#     cw_guideline_maper = make_bloc_cw_guidelines_prompt_formating_chain()
    
#     lexicon_post_processing_chain_base = RunnablePassthrough.assign(cw_guidelines=lambda x: cw_guideline_maper) | prompt | model | output_parser | itemgetter("corrected_text")
#     lexicon_post_processing_chain_fallback = RunnablePassthrough.assign(cw_guidelines=lambda x: cw_guideline_maper) | prompt | choose_model("4") | output_parser | itemgetter("corrected_text")

    
#     return lexicon_post_processing_chain_base.with_fallbacks([lexicon_post_processing_chain_fallback])

# def process_featured_venues_chain(featured_venues):
#     class FeaturedVenuesList(BaseModel):
#         list: List[str] = Field(description="List containing all featured venues")
        
#     model = ChatOpenAI(model_name="gpt-4-0125-preview", temperature=0)
    
#     parser = JsonOutputParser(pydantic_object=FeaturedVenuesList)
    
#     prompt = ChatPromptTemplate(
#         messages=[
#             SystemMessagePromptTemplate.from_template("""You are a helpful assistant. You will be provided an input list of featured venues. Provide back the list in a formatted way. The output must look like the following 'Item1, Item2, Item3, Item4, ...' \n\n {format_instructions}"""),
#             HumanMessagePromptTemplate.from_template("{value}"),
#         ],
#         input_variables=["value"],
#         partial_variables={"format_instructions": parser.get_format_instructions()},
#     )
#     process_featured_venues_chain = prompt | model | parser
#     reprocessed_featured_venues = process_featured_venues_chain.invoke({"value":featured_venues})
#     return reprocessed_featured_venues['list']