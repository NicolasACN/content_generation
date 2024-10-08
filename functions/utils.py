import os
import json
from dotenv import find_dotenv, load_dotenv
import openai
# from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
# from langchain_core.pydantic_v1 import BaseModel, Field
# from langchain_core.output_parsers import JsonOutputParser
# from langchain_openai.chat_models import ChatOpenAI
# from langchain_core.runnables import RunnablePassthrough, RunnableLambda
# from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from operator import itemgetter

import streamlit as st

#openai.api_key = st.secrets["OPENAI_API_KEY"]
# load_dotenv(find_dotenv())
# openai.api_key = os.environ['OPENAI_API_KEY']

# # Instantiate GPT Model 
# model = ChatOpenAI(model="gpt-4-turbo")

# # DATA LOADING
# DATA_FOLDER_PATH = os.path.join(os.getcwd(), "data")
# assert os.path.exists(DATA_FOLDER_PATH)

# # Load brand knowledge 
# with open(os.path.join(DATA_FOLDER_PATH, "brand_data", "brand_knowledge.txt"), "r") as f:
#     brand_knowledge = f.read()
    
# # Load persona
# with open(os.path.join(DATA_FOLDER_PATH, "persona", "persona.txt"), "r") as f:
#     persona = f.read()
    
# # Load copywriting guidelines
# with open(os.path.join(DATA_FOLDER_PATH, "brand_data", "copywriting_guidelines.txt"), "r") as f:
#     copywriting_guidelines = f.read()
    
# # Load Plateform Specs
# with open(os.path.join(DATA_FOLDER_PATH, "platform_specs", "hermes.txt"), "r") as f:
#     hermes_specs = f.read()
    
# with open(os.path.join(DATA_FOLDER_PATH, "platform_specs", "sephora.txt"), "r") as f:
#     sephora_specs = f.read()
    
# # Load product data
# product_data = {}  

# languages = os.listdir(os.path.join(DATA_FOLDER_PATH, "product_data"))

# product_data = {
#     language: {
#         product[:-4].replace('_', ' ').capitalize(): open(os.path.join(DATA_FOLDER_PATH, "product_data", language, product), "r").read() for product in os.listdir(os.path.join(DATA_FOLDER_PATH, "product_data", language))
#     } for language in languages
# }

# if len(os.listdir(os.path.join(DATA_FOLDER_PATH, "retailer_product_data"))):
#     retailer_product_data = {
#         retailer: {
#             lang: {
#                 product.capitalize().replace('_', ' ')[:-4]: open(os.path.join(DATA_FOLDER_PATH, "retailer_product_data", retailer, lang, product), "r").read() for product in os.listdir(os.path.join(DATA_FOLDER_PATH, "retailer_product_data", retailer, lang))
#             } for lang in ["en", "fr"]
#         } for retailer in os.listdir(os.path.join(DATA_FOLDER_PATH, "retailer_product_data"))
#     }
    

# PROMPT_FOLDER_PATH = os.path.join(os.getcwd(), 'prompts')
# assert os.path.exists(PROMPT_FOLDER_PATH)

def choose_model(model_name: str):
    if model_name == "3.5":
        return ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    elif model_name == "4":
        return ChatOpenAI(model_name="gpt-4-0125-preview", temperature=0)
    elif model_name == "4-turbo":
        return ChatOpenAI(model_name="gpt-4-turbo", temperature=0)
    elif model_name == "4o":
        return ChatOpenAI(model_name="gpt-4o", temperature=0)
    else:
        raise ValueError("Invalid model_name ")

def load_prompts(prompt_folder_path):
    with open(os.path.join(prompt_folder_path, "system_prompt.txt"), "r") as f:
        system_prompt = f.read()
    with open(os.path.join(prompt_folder_path, "human_prompt.txt"), "r") as f:
        human_prompt = f.read()
    return system_prompt, human_prompt

def read_file(file_path):
    assert os.path.exists(file_path)
    with open(file_path, 'r') as file:
        return file.read()

def standardize(string):
    # if string
    if isinstance(string, str):
        return string.strip(' ').replace('_', ' ').capitalize()
    # if list
    elif isinstance(string, list):
        return ' '.join([standardize(list_element) for list_element in string])
    # else shouldn't happen
    elif isinstance(string, dict):
        if 'value' in string:
            return standardize(string['value'])
        else:
            print(f"Problem found with dict string : {string}")
    else:
        print(f'Problem foud with string : {string}')
        raise ValueError
     
def make_variable_sentence(variable_name, variable_dict):
    try:
        if isinstance(variable_dict['value'], int):
            variable_dict['value'] = str(variable_dict['value'])
        variable_sentence =  f"{standardize(variable_name)} ({standardize(variable_dict['description'])}): {standardize(variable_dict['value'])}"
        return variable_sentence
    except KeyError as e:
        print(f"MAKE VARIABLE SENTENCE ERROR: for variable {variable_name} \nwith dict {variable_dict}")
        raise e
    

# copywriting_system_prompt, copywriting_human_prompt = load_prompts(os.path.join(PROMPT_FOLDER_PATH, "Copywriting"))
# brand_review_system_prompt, brand_review_human_prompt = load_prompts(os.path.join(PROMPT_FOLDER_PATH, "BrandReview"))
# copywriting_review_system_prompt, copywriting_review_human_prompt = load_prompts(os.path.join(PROMPT_FOLDER_PATH, "CopywritingReview"))
# tov_review_system_prompt, tov_review_human_prompt = load_prompts(os.path.join(PROMPT_FOLDER_PATH, "TOVReview"))
# editor_system_prompt, editor_human_prompt = load_prompts(os.path.join(PROMPT_FOLDER_PATH, "Editor"))
# role =  open(os.path.join(PROMPT_FOLDER_PATH, "Role", "role.txt"), "r").read()

# # Customization Prompt
# customization_system_prompt, customization_human_prompt = load_prompts(os.path.join(PROMPT_FOLDER_PATH, "Customization"))
# edition_customization_system_prompt, edition_customization_human_prompt = load_prompts(os.path.join(PROMPT_FOLDER_PATH, "CustomizationEditor"))

def generate_pdp(product_name, product_details, language, prompt_folder, model, product_data, data_folder):
    # Output parser creation
    class Copywriting(BaseModel):
        generated_text: str = Field(description="The written product detail page.")

    class Feedback(BaseModel):
        feedback: str = Field(description="The feedback on the copy.")

    class Edition(BaseModel):
        edited_text: str = Field(description="The edited and improved version of the product detail page.")

    copywriting_output_parser = JsonOutputParser(pydantic_object=Copywriting)
    review_output_parser = JsonOutputParser(pydantic_object=Feedback)
    edition_output_parser = JsonOutputParser(pydantic_object=Edition)

    
    # Chains
    ## Copywriting
    # Load Prompts
    copywriting_prompt_path = os.path.join(prompt_folder, "Copywriting")
    assert os.path.exists(copywriting_prompt_path)
    copywriting_system_prompt, copywriting_human_prompt = load_prompts(copywriting_prompt_path)
    
    copywriting_prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(copywriting_system_prompt),
            HumanMessagePromptTemplate.from_template(copywriting_human_prompt)
        ],
        input_variables=["role", "persona", "language", "product_data", "brand_knowledge", "copywriting_guidelines", "platform_specs"],
        partial_variables={"format_instructions": copywriting_output_parser.get_format_instructions()}
    )

    copywriting_chain = copywriting_prompt | model | copywriting_output_parser

    ## Brand Review
    # Load Prompts
    brand_review_prompt_path = os.path.join(prompt_folder, "BrandReview")
    assert os.path.exists(brand_review_prompt_path)
    brand_review_system_prompt, brand_review_human_prompt = load_prompts(brand_review_prompt_path)
    brand_review_prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(brand_review_system_prompt),
            HumanMessagePromptTemplate.from_template(brand_review_human_prompt)
        ],
        input_variables=["role", "brand_knowledge", "generated_text"],
        partial_variables={"format_instructions": review_output_parser.get_format_instructions()}
    )
    brand_review_chain = brand_review_prompt | model | review_output_parser

    ## Copywriting Review
    # Load Prompts
    copywriting_review_prompt_path = os.path.join(prompt_folder, "CopywritingReview")
    assert os.path.exists(copywriting_review_prompt_path)
    copywriting_review_system_prompt, copywriting_review_human_prompt = load_prompts(copywriting_review_prompt_path)
    
    copywriting_review_prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(copywriting_review_system_prompt),
            HumanMessagePromptTemplate.from_template(copywriting_review_human_prompt)
        ],
        input_variables=["role", "copywriting_guidelines", "generated_text"],
        partial_variables={"format_instructions": review_output_parser.get_format_instructions()}
    )
    copywriting_review_chain = copywriting_review_prompt | model | review_output_parser

    ## TOV Review 
    def format_examples(example_dict):
        formated_text = ""
        for product in example_dict.keys():
            formated_text += str(product.upper()) + "\n"
            formated_text +=  str(example_dict[product]) + "\n"
            formated_text += "-" * 10 + "\n"
        return formated_text
    
    # Load Prompts
    tov_review_prompt_path = os.path.join(prompt_folder, "TOVReview")
    assert os.path.exists(tov_review_prompt_path)
    tov_review_system_prompt, tov_review_human_prompt = load_prompts(tov_review_prompt_path)
          
    tov_review_prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(tov_review_system_prompt),
            HumanMessagePromptTemplate.from_template(tov_review_human_prompt)
        ],
        input_variables=["role", "reference_examples", "generated_text"],
        partial_variables={"format_instructions": review_output_parser.get_format_instructions()}
    )
    tov_review_chain = tov_review_prompt | model | review_output_parser

    ## Edition
    # Load Prompts
    edition_prompt_path = os.path.join(prompt_folder, "Editor")
    assert os.path.exists(edition_prompt_path)
    editor_system_prompt, editor_human_prompt = load_prompts(edition_prompt_path)
          
    edition_prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(editor_system_prompt),
            HumanMessagePromptTemplate.from_template(editor_human_prompt)
        ],
        input_variables=["role", "perona", "generated_text", "feedback", "brand_knowledge", "copywriting_guidelines", "reference_examples", "platform_specs"], 
        partial_variables={"format_instructions": edition_output_parser.get_format_instructions()}
    )
    edition_chain = edition_prompt | model | edition_output_parser
    
    def format_feedback(reviews):
        brand_review, copywriting_review, tov_review = reviews
        return f"""Brand Feedback:
    {brand_review}

    Copywriting Feedback:
    {copywriting_review}

    Tone of Voice Feedback:
    {tov_review}

    """

    write_product_description_chain = (
        RunnablePassthrough.assign(generated_text=copywriting_chain)
        | RunnablePassthrough.assign(reference_examples=itemgetter("reference_examples") | RunnableLambda(format_examples))
        | RunnablePassthrough.assign(
            brand_review=brand_review_chain | itemgetter("feedback"),
            copywriting_review=copywriting_review_chain | itemgetter("feedback"),
            tov_review=tov_review_chain | itemgetter("feedback")
        ) | RunnablePassthrough.assign(feedback=itemgetter("brand_review", "copywriting_review", "tov_review") | RunnableLambda(format_feedback))
        | RunnablePassthrough.assign(edited_text=edition_chain | itemgetter("edited_text"))
        | itemgetter("edited_text")
    )   
    
    if product_name in product_data[language]:
        product_details = product_data[language][product_name]
    else:
        def format_product_details(product_detail_list):
            return  f"PRODUCT DESCRIPTION:\n{product_detail_list[0]}\n\nOBJECT DESCRIPTION:\n{product_detail_list[1]}\n\nADDITIONAL INFO:\n{product_detail_list[2]}"
        product_details = format_product_details(product_details)

    # Load guidelines 
    brand_guidelines_path = os.path.join(data_folder, "brand_data", "brand_knowledge.txt")
    assert os.path.exists(brand_guidelines_path)
    with open(brand_guidelines_path, "r") as f:
        brand_knowledge = f.read()
        
    copywriting_guidelines_path = os.path.join(data_folder, "brand_data", "copywriting_guidelines.txt")
    assert os.path.exists(copywriting_guidelines_path)
    with open(copywriting_guidelines_path, "r") as f:
        copywriting_guidelines = f.read()
    
    persona_path = os.path.join(data_folder, "persona", "persona.txt")
    assert os.path.exists(persona_path)
    with open(persona_path, "r") as f:
        persona = f.read()
        
    role_path = os.path.join(prompt_folder, "Role", "role.txt")
    assert os.path.exists(role_path)
    with open(role_path, 'r') as f:
        role = f.read()
        
    return write_product_description_chain.invoke({
        "role": role, 
        "persona": persona, 
        "language": language,
        "product_name": product_name,
        "product_data": product_details,
        "brand_knowledge": brand_knowledge,
        "copywriting_guidelines": copywriting_guidelines,
        "reference_examples": product_data[language],
        "existing_product_dp": product_data[language][product_name] 
    })
    
def format_pdp_text(pdp_text):
    # Split the input text by double newlines to separate the paragraphs
    paragraphs = pdp_text.strip().split("\n\n")
    
    # Initialize an empty list to hold the formatted paragraphs
    formatted_paragraphs = []
    
    for paragraph in paragraphs:
        # Split each paragraph by the first newline to separate the title from the content
        lines = paragraph.split("\n", 1)  # Only split on the first newline
        title = lines[0].strip()  # First line is the title
        
        # Check if there is any content after the title
        content = lines[1].strip() if len(lines) > 1 else ""

        # Format the title in bold with a line break if there is content
        if title != "---":
            formatted_paragraph = f"**{title}**"
        else:
            formatted_paragraph = title
        if content:
            formatted_paragraph += f"  \n{content}"
        
        formatted_paragraphs.append(formatted_paragraph)
    
    # Join the formatted paragraphs with double newlines
    formatted_text = "\n\n".join(formatted_paragraphs)
    
    return formatted_text

def load_product_details(product_name, language):
    product_name = product_name.lower().replace(' ', '_').replace('è', 'e')
    if not ".txt" in product_name:
        product_name += ".txt"
        
    with open(os.path.join(os.getcwd(), "data", "product_details", language, "product_description", product_name), 'r') as f:
        product_description = f.read()
    with open(os.path.join(os.getcwd(), "data", "product_details", language, "object_description", product_name), 'r') as f:
        object_description = f.read()
    with open(os.path.join(os.getcwd(), "data", "product_details", language, "additional_info", product_name), 'r') as f:
        additional_info = f.read()
    return product_description, object_description, additional_info

def format_product_details(product_description, object_description, additional_info):
    return f"PRODUCT DESCRIPTION:\n{product_description}\n\nOBJECT DESCRIPTION:\n{object_description}\n\nADDITIONAL INFO:\n{additional_info}\n\n"

# def retailer_customize_pdp(product_name, language): 
#     # Output parser creation
#     class Customization(BaseModel):
#         customized_text: str = Field(description="The retailer customized product detail page.")

#     class Feedback(BaseModel):
#         feedback: str = Field(description="The feedback on the copy.")

#     class Edition(BaseModel):
#         edited_text: str = Field(description="The edited and improved version of the customized product detail page.")

#     customization_output_parser = JsonOutputParser(pydantic_object=Customization)
#     review_output_parser = JsonOutputParser(pydantic_object=Feedback)
#     edition_output_parser = JsonOutputParser(pydantic_object=Edition)

#     # Chains
#     ## Copywriting
#     customization_prompt = ChatPromptTemplate(
#         messages=[
#             SystemMessagePromptTemplate.from_template(customization_system_prompt),
#             HumanMessagePromptTemplate.from_template(customization_human_prompt)
#         ],
#         input_variables=["role", "persona", "language", "existing_product_dp", "brand_knowledge", "copywriting_guidelines", "reference_examples", "platform_specs"],
#         partial_variables={"format_instructions": customization_output_parser.get_format_instructions()}
#     )

#     customization_chain = customization_prompt | model | customization_output_parser

#     ## Brand Review
#     brand_review_prompt = ChatPromptTemplate(
#         messages=[
#             SystemMessagePromptTemplate.from_template(brand_review_system_prompt),
#             HumanMessagePromptTemplate.from_template(brand_review_human_prompt)
#         ],
#         input_variables=["role", "brand_knowledge", "generated_text"],
#         partial_variables={"format_instructions": review_output_parser.get_format_instructions()}
#     )
#     brand_review_chain = brand_review_prompt | model | review_output_parser

#     ## Copywriting Review
#     copywriting_review_prompt = ChatPromptTemplate(
#         messages=[
#             SystemMessagePromptTemplate.from_template(copywriting_review_system_prompt),
#             HumanMessagePromptTemplate.from_template(copywriting_human_prompt)
#         ],
#         input_variables=["role", "copywriting_guidelines", "generated_text"],
#         partial_variables={"format_instructions": review_output_parser.get_format_instructions()}
#     )
#     copywriting_review_chain = copywriting_review_prompt | model | review_output_parser

#         ## TOV & Platform Specs Review 
#     def format_examples(example_dict):
#         formated_text = ""
#         for language in ["en", "fr"]:
#             formated_text += f"\nLanguage: {language}\n\n"
#             for product in example_dict["hermes"][language]:
#                 formated_text += f"Original text:\n{example_dict['hermes'][language][product]}\n\nAdapted text:\n{example_dict['sephora'][language][product]}\n\n"
#         return formated_text
            
#     tov_review_prompt = ChatPromptTemplate(
#         messages=[
#             SystemMessagePromptTemplate.from_template(tov_review_system_prompt),
#             HumanMessagePromptTemplate.from_template(tov_review_human_prompt)
#         ],
#         input_variables=["role", "reference_examples", "generated_text"],
#         partial_variables={"format_instructions": review_output_parser.get_format_instructions()}
#     )
#     tov_review_chain = tov_review_prompt | model | review_output_parser

#     ## Edition
#     edition_customization_prompt = ChatPromptTemplate(
#         messages=[
#             SystemMessagePromptTemplate.from_template(edition_customization_system_prompt),
#             HumanMessagePromptTemplate.from_template(edition_customization_human_prompt)
#         ],
#         input_variables=["role", "persona", "generated_text", "feedback", "brand_knowledge", "copywriting_guidelines", "reference_examples", "existing_product_dp", "platform_specs"], 
#         partial_variables={"format_instructions": edition_output_parser.get_format_instructions()}
#     )
#     edition_customization_chain = edition_customization_prompt | model | edition_output_parser

#     def format_feedback(reviews):
#         brand_review, copywriting_review, tov_review = reviews
#         return f"""Brand Feedback:
#     {brand_review}

#     Copywriting Feedback:
#     {copywriting_review}

#     Tone of Voice and Platform specs compliance Feedback:
#     {tov_review}

#     """

#     customize_product_description_chain = (
#         RunnablePassthrough.assign(generated_text=customization_chain)
#         | RunnablePassthrough.assign(reference_examples=itemgetter("reference_examples") | RunnableLambda(format_examples))
#         | RunnablePassthrough.assign(
#             brand_review=brand_review_chain | itemgetter("feedback"),
#             copywriting_review=copywriting_review_chain | itemgetter("feedback"),
#             tov_review=tov_review_chain | itemgetter("feedback")
#         ) | RunnablePassthrough.assign(feedback=itemgetter("brand_review", "copywriting_review", "tov_review") | RunnableLambda(format_feedback))
#         | RunnablePassthrough.assign(edited_text=edition_customization_chain | itemgetter('edited_text'))
#         | itemgetter("edited_text")
#     )   
#     if product_name in product_data[language]:
#         product_details = product_data[language][product_name]
#     else:
#         def format_product_details(product_detail_list):
#             return  f"PRODUCT DESCRIPTION:\n{product_detail_list[0]}\n\nOBJECT DESCRIPTION:\n{product_detail_list[1]}\n\nADDITIONAL INFO:\n{product_detail_list[2]}"
#         product_details = format_product_details(product_details)

#     customize_product_description_chain.invoke({
#         "role": role, 
#         "persona": persona, 
#         "language": language,
#         "product_name": product_name,
#         "brand_knowledge": brand_knowledge,
#         "copywriting_guidelines": copywriting_guidelines,
#         "reference_examples": retailer_product_data,
#         "platform_specs": sephora_specs,   
#         "existing_product_dp": product_data[language]["Terre d Hermès"], 
#         "product_data": retailer_product_data["sephora"][language]["Terre d hermes"] 
#     })
    
#     return customize_product_description_chain.invoke({
#         "role": role, 
#         "persona": persona, 
#         "language": language,
#         "product_name": product_name,
#         "product_data": product_details,
#         "brand_knowledge": brand_knowledge,
#         "copywriting_guidelines": copywriting_guidelines,
#         "reference_examples": retailer_product_data,
#         "platform_specs": sephora_specs,   
#         "existing_product_dp": product_data[language][product_name] 
#     })

def dict_to_markdown(data):
    markdown_lines = []

    def parse_dict(d, level=0):
        for key, value in d.items():
            if isinstance(value, dict):
                markdown_lines.append(f"{'#' * (level + 1)} {key}")
                parse_dict(value, level + 1)
            else:
                markdown_lines.append(f"**{key.capitalize()}:** {value}")

    parse_dict(data)
    return "\n\n".join(markdown_lines)

def extract_brand_knowledge(brand_docs: st, model: str = "4-turbo"):
    model = choose_model(model)
    
    system_message = """You are an expert in branding and marketing. 
    You are working with a team of copywriters and you help them understand the brand, its identity, concepts, culture and heritage. 
    You have received several documents about the brand. 
    Your task is to condense those documents into a concise branding brief that will help and guide the copywriters produce on brand content.
    """

    human_message = """Here are the brand documents separated by ---. Please condense them into a concise brand brief.
    <brand_documents>
    {brand_documents}
    </brand_documents>

    {format_instructions}
    """
    
    class BrandKnowledge(BaseModel):
        brand_knowledge: str = Field(description="The condensed brand knowledge extracted from the documents to help copywriters.")

    output_parser = JsonOutputParser(pydantic_object=BrandKnowledge)
    
    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(system_message),
            HumanMessagePromptTemplate.from_template(human_message),
        ],
        input_variables=["brand_documents"],
        partial_variables={'format_instructions': output_parser.get_format_instructions()}
    )
    
    brand_knowledge_extraction_chain = prompt | model | output_parser | itemgetter("brand_knowledge")
    
    return brand_knowledge_extraction_chain.invoke({"brand_documents": brand_docs})

def extract_copywriting_guidelines(copywriting_docs: str, model: str = "4-turbo"):
    model = choose_model(model)
    system_message = """You are a journalist expert in writing on brand text. 
    You are working with a team of copywriters and you role is to guide them to produce perfect copies by providing them an understandable set of copywriting guidelines based on the provided documents.
    You have received several copywriting guidelines related documents . 
    Your task is to condense those documents into concise copywriting guidelines that will help and guide the copywriters produce perfect content.
    """

    human_message = """Here are the copywriting documents separated by ---. Please condense them into concise copywriting guidelines.
    <copywriting_guidelines_documents>
    {copywriting_guidelines_documents}
    </copywriting_guidelines_documents>

    {format_instructions}
    """
    
    class CopywritingGuidelines(BaseModel):
        copywriting_guidelines: str = Field(description="The condensed copywriting guidelines extracted from the documents to help copywriters.")

    output_parser = JsonOutputParser(pydantic_object=CopywritingGuidelines)
    
    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(system_message),
            HumanMessagePromptTemplate.from_template(human_message),
        ],
        input_variables=["copywriting_guidelines_documents"],
        partial_variables={'format_instructions': output_parser.get_format_instructions()}
    )
    copywriting_guidelines_extraction_chain = prompt | model | output_parser | itemgetter("copywriting_guidelines")

    return copywriting_guidelines_extraction_chain.invoke({"copywriting_guidelines_documents": copywriting_docs})

def character_limit_check_section(section, character_limit):
    for element in section:
        try:
            # Exclude image_labell
            if "image_label" in element:
                continue

            # Nested
            elif isinstance(section[element], list):
                for nested_item in section[element]:
                    for nested_element in nested_item:
                        if len(nested_item[nested_element]) > get_character_limit(character_limit[nested_element]) * 1.5:
                            return False
            # Non Nested
            elif len(section[element]) > get_character_limit(character_limit[element]) * 1.5:
                return False
        except Exception as e:
            print(f"Found error {e} at section : \n{section} and character limit: \n{character_limit}")
    return True

def get_character_limit(limit):
    if "words" in limit:
        return 60
    return int(limit.split(' ')[0])

def load_prompt(file_path):
    return read_file(file_path)

def load_message_prompts(file_path):
    system_prompt = load_prompt(os.path.join(file_path, 'system_prompt.txt'))
    human_prompt = load_prompt(os.path.join(file_path, 'human_prompt.txt'))
    return system_prompt, human_prompt