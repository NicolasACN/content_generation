import os 
import json 
import pandas as pd
import openpyxl
import streamlit as st
from copy import deepcopy

def read_file(file_path):
    assert os.path.exists(file_path)
    with open(file_path, 'r') as file:
        return file.read()

def load_prompt(file_path):
    return read_file(file_path)

def load_message_prompts(file_path):
    system_prompt = load_prompt(os.path.join(file_path, 'system_message.txt'))
    human_prompt = load_prompt(os.path.join(file_path, 'human_message.txt'))
    return system_prompt, human_prompt

def to_serializable(val):
    """Fonction helper pour convertir les objets personnalisés en dictionnaires."""
    if hasattr(val, "dict"):
        return val.dict()  # Pour les modèles Pydantic
    elif isinstance(val, (list, tuple)):
        return [to_serializable(item) for item in val]
    elif isinstance(val, dict):
        return {key: to_serializable(value) for key, value in val.items()}
    else:
        return val
    
def save_versioned_data(file_path, data_dict, version_count):
    """
    Enregistre les blocs générés et les feedbacks dans un fichier texte, 
    avec un versioning et séparés par des underscores.
    """
    with open(file_path, "a") as file:  # Utilisez "a" pour append au fichier existant
        # Header de version
        file.write(f"\n\n{'_' * 10} Version {version_count} {'_' * 10}\n\n")
        
        # Enregistre les données spécifiques
        for key in ["generated_bloc", "bm_review", "cw_review"]:
            value = data_dict.get(key, "No data")

            # Vérifie si la valeur est un dictionnaire et convertit en str si nécessaire
            if isinstance(value, dict) or isinstance(value, list):
                value = json.dumps(value, ensure_ascii=False, indent=4)
            file.write(f"{key}:\n{value}\n\n")
            
def make_variable_sentence(variable_name, variable_dict):
    try:
        if isinstance(variable_dict['value'], int):
            variable_dict['value'] = str(variable_dict['value'])
        variable_sentence =  f"{standardize(variable_name)} ({standardize(variable_dict['description'])}): {standardize(variable_dict['value'])}"
        return variable_sentence
    except KeyError as e:
        print(f"MAKE VARIABLE SENTENCE ERROR: for variable {variable_name} \nwith dict {variable_dict}")
        raise e
    
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

def update_excel_with_json_data(workbook_path, guidelines_dic):
    workbook = openpyxl.load_workbook(workbook_path)

    # Dictionnaire pour gérer les cas spéciaux des positions multiples
    special_cases = {
        "AWARDS": ["HOMEPAGE", "RESTAURANT DP"],
        "SUSTAINABILITY": ["HOMEPAGE", "MICE LP", "WEDDINGS LP"],
        "GETTING THERE": ["HOMEPAGE", "RESTAURANT DP"]
    }

    for page in guidelines_dic.keys(): # iterate over the key page in the json 
        if page in workbook.sheetnames:
            data = guidelines_dic.get(page, {}) # get the value of the key page in the json ( resto,hompage,etc..)
            for section, details in data.items(): # iterate over the key 'section' in the json
                guidelines = details.get("excel_guidelines", {}) # get the value of the key 'excel_guidelines' in the json
                for key, value in guidelines.items(): # in each section iterate over the keys ( output_position, enforced_value, generated_value) to get the value
                    output_positions = value["output_position"].split(",") 
                    text = value["enforced_value"] if value["enforced_value"] else value["generated_value"] # if there is a value in 'enforced_value' then take it else take the value in 'generated_value'
                    
                    # Cas général pour les positions uniques
                    if section not in special_cases:
                        for position in output_positions:
                            if position:
                                workbook[page][position].value = text
                    else:
                        # cas spéciaux pour les positions multiples
                        special_pages = special_cases[section]
                        for i, position in enumerate(output_positions):
                            if position and i < len(special_pages):
                                target_page = special_pages[i]
                                workbook[target_page][position].value = text
        else:
            print(f"La feuille {page} n'existe pas dans le fichier Excel.")
    
    # Sauvegarde du fichier Excel mis à jour
    updated_excel_path = os.path.join(os.path.dirname(workbook_path), 'Excel_generated.xlsx')
    workbook.save(updated_excel_path)
    print(f"Sucess : Fichier Excel mis à jour enregistré sous : {updated_excel_path}")

def convert_dict_values_to_string(data_dict):
    """
    Convert each nested dictionary in the main dictionary to a JSON string.
    
    :param data_dict: Dictionary with values that are dictionaries.
    :return: Dictionary with the same keys but stringified values.
    """
    return {key: json.dumps(value, indent=4) for key, value in data_dict.items()}

def website_to_excel(data_dict, output_dir="./output"):
    """
    Writes each key's dictionary to a separate Excel file.
    
    :param data_dict: Dictionary where each key contains another dictionary meant for different Excel files.
    :param output_dir: The directory where the Excel files will be saved.
    """
    
    writer = pd.ExcelWriter(f'{output_dir}/website_content/website_content.xlsx', engine='openpyxl')

    for page, sections in data_dict.items():
        # Create a Pandas Excel writer using openpyxl as the engine
        string_sections = convert_dict_values_to_string(sections)
        df = pd.DataFrame(string_sections, index=[0])
        #print(df.head())
        # Iterate through each section in the dictionary
        #for section, values in sections.items():
        #    # Convert the section dictionary to a DataFrame
        #    df = pd.DataFrame(values, index=[0])  # Creating a single row DataFrame from the dictionary
        df = df.T  # Transpose to swap rows and columns
        #    df.columns = ['Value']  # Setting column header
            
        # Write the DataFrame to a named sheet in the Excel file
        df.to_excel(writer, sheet_name=page)
        
        # Save the workbook
    writer.close()

    #print("All pages have been written successfully.")

def excel_to_website_dict(excel_path):
    """
    Reads an Excel workbook where each sheet corresponds to a different key in the dictionary.
    Parses JSON strings in the cells back into dictionaries and extensively cleans up formatting characters.

    :param excel_path: Path to the Excel file.
    :return: Nested dictionary with keys as sheet names and values as dictionaries of the data.
    """
    def clean_json_string(s):
        """ Recursively cleans JSON strings, removing unnecessary white spaces and newlines. """
        try:
            data = json.loads(s)
            if isinstance(data, dict):
                return {k: clean_json_string(json.dumps(v)) for k, v in data.items()}
            elif isinstance(data, list):
                return [clean_json_string(json.dumps(item)) for item in data]
            else:
                return data
        except json.JSONDecodeError:
            return s.strip()

    # Load the workbook
    xls = pd.ExcelFile(excel_path)
    
    # Initialize the main dictionary
    data_dict = {}

    # Iterate over each sheet in the workbook
    for sheet_name in xls.sheet_names:
        # Read the sheet into a DataFrame with the first column as the index
        df = pd.read_excel(xls, sheet_name=sheet_name, index_col=0)
        
        # Parse JSON strings in the DataFrame cells back into dictionaries
        section_dict = {}
        for index, row in df.iterrows():
            cell_value = row[0]
            # Clean and parse JSON string
            cleaned_value = ' '.join(cell_value.replace('\n', ' ').split())
            # Attempt recursive parsing and cleaning
            section_dict[index] = clean_json_string(cleaned_value)

        # Assign the parsed dictionary to the corresponding sheet name key
        data_dict[sheet_name] = section_dict
        
    return data_dict


def json_to_website_dict(json_path):
    """
    Reads a JSON file where each key corresponds to a different section in the dictionary.
    Parses JSON data extensively and cleans up formatting characters.

    :param json_path: Path to the JSON file.
    :return: Nested dictionary with keys as section names and values as dictionaries of the data.
    """
    def clean_json_data(data):
        """ Recursively cleans JSON data, removing unnecessary white spaces and newlines. """
        if isinstance(data, dict):
            return {k: clean_json_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [clean_json_data(item) for item in data]
        elif isinstance(data, str):
            return ' '.join(data.replace('\n', ' ').split())
        else:
            return data

    # Load the JSON data
    with open(json_path, 'r') as file:
        raw_data = json.load(file)

    # Clean and parse the JSON data recursively
    clean_data = {section: clean_json_data(contents) for section, contents in raw_data.items()}
    
    return clean_data



def page_to_excel(data_dict, page, output_dir="./output_excel"):
    """
    Writes each key's dictionary to a separate Excel file.
    
    :param data_dict: Dictionary where each key contains another dictionary meant for different Excel files.
    :param output_dir: The directory where the Excel files will be saved.
    """
    
    writer = pd.ExcelWriter(f'{output_dir}/page_content/{page}_content.xlsx', engine='openpyxl')

    for section, section_content in data_dict.items():
        # Create a Pandas Excel writer using openpyxl as the engine
        string_content = convert_dict_values_to_string(section_content)
        #df = pd.DataFrame(string_sections, index=[0])
        df = pd.DataFrame(string_content, index=[0])

        #print(df.head())
        # Iterate through each section in the dictionary
        #for section, values in sections.items():
        #    # Convert the section dictionary to a DataFrame
        #    df = pd.DataFrame(values, index=[0])  # Creating a single row DataFrame from the dictionary
        df = df.T  # Transpose to swap rows and columns
        #    df.columns = ['Value']  # Setting column header
            
        # Write the DataFrame to a named sheet in the Excel file
        df.to_excel(writer, sheet_name=section)
        
        # Save the workbook
    writer.close()

    #print("Page have been written successfully.")
    
def section_to_excel(data_dict, page, section, output_dir="./output_excel"):
    """
    Writes each key's dictionary to a separate Excel file.
    
    :param data_dict: Dictionary where each key contains another dictionary meant for different Excel files.
    :param output_dir: The directory where the Excel files will be saved.
    """
    
    writer = pd.ExcelWriter(f'{output_dir}/section_content/{page}_{section}_content.xlsx', engine='openpyxl')

    #for section, section_content in data_dict.items():
        # Create a Pandas Excel writer using openpyxl as the engine
        #string_content = convert_dict_values_to_string(section_content)
        #df = pd.DataFrame(string_sections, index=[0])
    df = pd.DataFrame(data_dict, index=[0])

        #print(df.head())
        # Iterate through each section in the dictionary
        #for section, values in sections.items():
        #    # Convert the section dictionary to a DataFrame
        #    df = pd.DataFrame(values, index=[0])  # Creating a single row DataFrame from the dictionary
    df = df.T  # Transpose to swap rows and columns
        #    df.columns = ['Value']  # Setting column header
            
        # Write the DataFrame to a named sheet in the Excel file
    df.to_excel(writer, sheet_name=section)
        
        # Save the workbook
    writer.close()

# TODO : Implement nice formating and reordering of dict (title > kicker > description > nested items123 (title > kicker > desc > item_title > item_value))
def format_generation_output(data):
    # Define the priority for sorting elements within the dictionary
    priority_dict = {
        "title": 1, "kicker": 2, "description": 3, "cta": 4,
        "image_label": 5,
        "item_1_item_title": 6, "item_1_item_value": 7,
        "item_2_item_title": 8, "item_2_item_value": 9,
        "item_3_item_title": 10, "item_3_item_value": 11,
        "item_4_item_title": 12, "item_4_item_value": 13,
        "item_5_item_title": 14, "item_5_item_value": 15,
        "item_6_item_title": 16, "item_6_item_value": 17,
        "item_7_item_title": 18, "item_7_item_value": 19,
        "item_8_item_title": 20, "item_8_item_value": 21,
        "item_9_item_title": 22, "item_9_item_value": 23,
        "item_10_item_title": 24, "item_10_item_value": 25,
        "item_1_carousel_title": 26, "item_1_carousel_description": 27,
        "item_1_carousel_cta": 28, "item_1_carousel_kicker": 29,
        "item_2_carousel_title": 30, "item_2_carousel_description": 31,
        "item_2_carousel_cta": 32, "item_2_carousel_kicker": 33,
        "item_3_carousel_title": 34, "item_3_carousel_description": 35,
        "item_3_carousel_cta": 36, "item_3_carousel_kicker": 37,
        "details_room_accessibility": 38,
        "details_room_capacity": 39,
        "carousel": 40, "carousel_title": 41, "carousel_description": 42,
        "carousel_cta": 43, "carousel_kicker": 44, "item": 45, "item_title": 46,
        "item_value": 47
    }

    if isinstance(data, dict):
        sorted_dict = {}
        sorted_keys = sorted(data.keys(), key=lambda x: priority_dict.get(x, float('inf')))
        for key in sorted_keys:
            sorted_dict[key] = format_generation_output(data[key])
        return sorted_dict
    elif isinstance(data, list):
        return [format_generation_output(item) for item in data]
    else:
        return data

def reorder_sections(data):
    """
    Reorder the sections of all pages in a data dictionary based on predefined orders.
    
    Parameters:
        data (dict): The main dictionary containing all the data.
        
    Returns:
        dict: A dictionary with all pages reordered according to specified orders.
    """
    # Predefined orders for each section
    orders = {
        'HOMEPAGE': [
            'HERO', 'INTRO', 'SUITES + ROOMS + APPARTMENTS', 'FOOD + BEVERAGE', 'MEETINGS + EVENTS', 'OTHER SERVICES', 'LOYALTY', 'GETTING THERE', 'SUSTAINABILITY', 'AWARDS', 'SOCIAL MEDIA', 'FAQ', 'DISCOVER OTHER HOTELS'
        ],
        'MICE DP': [
            'HERO', 'INTRO', 'DOWNLOADS', 'AMENITIES', 'EDITORIAL USP', 'DISCOVER OTHER VENUES'
        ],
        'MICE LP': [
            'HERO', 'INTRO', 'MEETINGS AT HOTEL NAME', 'OUR MEETING ROOMS', 'FEATURED VENUES', 
            'SERVICE EXPERTISE', 'MEETING PACKAGES + OFFERS',  
            'SPACES FOR ALL EVENTS'
        ],
        'RESTAURANT DP': [
            'HERO', 'INTRO', 'DOWNLOADS', 'MEET THE CHEF', 'DISCOVER OUR OFFERS', 'DISCOVER OTHER VENUES',
        ],
        'ROOM DP': [
            'HERO', 'INTRO', 'SUITES + ROOMS + APPARTMENTS OVERVIEW'
        ],
        'WEDDINGS LP': [
        #    'HERO', 'INTRO', 'PULLMAN WEDDINGS', 'SERVICE EXPERTISE', 'WEDDING PACKAGES', 'FOR EVERY OCCASION'
        ],
        'WELLNESS LP': [
            'HERO', 'INTRO', 'MENUES', 'OTHER WELLNESS FACILITIES'
        ]
    }

    # Apply ordering for each page if it exists in the data dictionary
    reordered_data = {}
    for page, order in orders.items():
        if page in data:
            page_data = data[page]
            reordered_page = {key: page_data[key] for key in order if key in page_data}
            reordered_data[page] = reordered_page
        else:
            print(f"No data found for {page}, skipping reordering.")

    return reordered_data

def flatten_dict(website_content_data):
    def flatten_nested_dict(items):
        # This function flattens lists of dictionaries by appending the item index to the keys
        flattened_dict = {}
        for index, item in enumerate(items, start=1):
            for nested_key, nested_value in item.items():
                flattened_dict[f"item {index}_{nested_key}"] = nested_value
        return flattened_dict

    website_content_data_modified = website_content_data.copy()  # Make a copy of content_test to avoid modifying the original

    # Process to flatten the items directly under each section
    for section_key, section_value in website_content_data_modified.items():
        for key, value in section_value.items():
            if isinstance(value, dict) and "item" in value:  # Check if the section has an 'item' key
                flattened_items = flatten_nested_dict(value["item"])  # Apply the flatten function
                value.update(flattened_items)  # Update the section with flattened items directly
                del value["item"]  # Remove the original 'item' key
            elif isinstance(value, dict) and "carousel" in value:
                flattened_items = flatten_nested_dict(value["carousel"])
                value.update(flattened_items)
                del value["carousel"]

    return website_content_data_modified

# def st_display_content(data):
#    if isinstance(data, dict):
#        # Display each key-value pair with the format "Key : Value"
#        for key, value in data.items():
#            st.markdown(f"**{key.capitalize()} :** {value}")
#    elif isinstance(data, list):
#        # If it's a list, process each item individually
#        for item in data:
#            display_content(item)
#    else:
#        # Write plain data directly
#        st.write(data)

def format_dictionary(dictionary):
    formatted_text = ""
    for page, sections in dictionary.items():
        formatted_text += page.upper() + "\n"
        for section, elements in sections.items():
            formatted_text += section.upper() + "\n"
            formatted_text += format_elements(elements)
            formatted_text += "\n"  # Add newline after each section
        formatted_text += "\n"  # Add newline after each page
    return formatted_text

def format_elements(elements):
    formatted_text = ""
    for key, value in elements.items():
        if isinstance(value, list):
            for item in value:
                formatted_text += format_nested_elements(item)
        elif isinstance(value, dict):
            formatted_text += key.upper() + "\n"
            formatted_text += format_nested_elements(value)
        else:
            formatted_text += key.capitalize().replace("_", " ") + ": " + value + "\n"
    return formatted_text

def format_nested_elements(nested_elements):
    formatted_text = ""
    for key, value in nested_elements.items():
        formatted_text += "\t" + key.capitalize().replace("_", " ") + ": " + value + "\n"
    return formatted_text


def reorder_elements(section_dict):
    priority_dict = {
        "title": 1, 
        "kicker": 2, 
        "description": 3,
        "carousel": 4, 
        "carousel_title": 5,
        "carousel_kicker": 6,
        "carousel_description": 7, 
        "carousel_image": 8,
        "carousel_image_title": 8,
        "carousel_cta": 9,
        "item": 10,
        "item_title": 11,
        "item_kicker": 12, 
        "item_description": 13,
        "item_image": 14,
        "item_image_label": 14,
        "item_cta": 15,
        "details_room_accessibility": 16,
        "details_room_capacity": 17,
        "image": 18, 
        "image_label": 18,
        "cta": 19
    }
    sorted_elements = sorted(section_dict.items(), key=lambda x: priority_dict.get(x[0], float('inf')))
    return dict(sorted_elements)

def reorder_dictionary(initial_dict):
    ordered_sections = {
        'HOMEPAGE': [
            'HERO', 'INTRO', 'SUITES + ROOMS + APPARTMENTS', 'FOOD + BEVERAGE', 'MEETINGS + EVENTS', 'OTHER SERVICES', 'LOYALTY', 'GETTING THERE', 'SUSTAINABILITY', 'AWARDS', 'SOCIAL MEDIA', 'FAQ', 'DISCOVER OTHER HOTELS', "SEO"
        ],
        'MICE DP': [
            'HERO', 'INTRO', 'DOWNLOADS', 'AMENITIES', 'EDITORIAL USP', 'DISCOVER OTHER VENUES', "SEO"
        ],
        'MICE LP': [
            'HERO', 'INTRO', 'MEETINGS AT HOTEL NAME', 'OUR MEETING ROOMS', 'FEATURED VENUES', 
            'SERVICE EXPERTISE', 'MEETING PACKAGES + OFFERS',  
            'SPACES FOR ALL EVENTS', "SEO"
        ],
        'RESTAURANT DP': [
            'HERO', 'INTRO', 'DOWNLOADS', 'MEET THE CHEF', 'DISCOVER OUR OFFERS', 'DISCOVER OTHER VENUES', "SEO"
        ],
        'ROOM DP': [
            'HERO', 'INTRO', 'SUITES + ROOMS + APPARTMENTS OVERVIEW', "SEO"
        ],
        'WEDDINGS LP': [
            'HERO', 'INTRO', 'PULLMAN WEDDINGS', 'SERVICE EXPERTISE', 'WEDDING PACKAGES', 'FOR EVERY OCCASION'
        ],
        'WELLNESS LP': [
            'HERO', 'INTRO', 'MENUES', 'OTHER WELLNESS FACILITIES', "SEO"
        ]
    }
    reordered_dict = {}
    for page, sections_list in ordered_sections.items():
        reordered_dict[page] = {}
        for section in sections_list:
            if section in initial_dict[page]:
                reordered_dict[page][section] = reorder_elements(initial_dict[page][section])
    return reordered_dict

def format_page(page_content):
    formatted_text = ""
    for section, elements in page_content.items():
        formatted_text += section.upper() + "\n"
        formatted_text += format_elements(elements)
        formatted_text += "\n"  # Add newline after each section
    return formatted_text

def format_pages(dictionary):
    formatted_dict = {}
    for page, sections in dictionary.items():
        formatted_text = ""
        for section, elements in sections.items():
            formatted_text += section.upper() + "\n"
            formatted_text += format_elements(elements)
            formatted_text += "\n"  # Add newline after each section
        formatted_dict[page] = formatted_text
    return formatted_dict

def format_section(section_content):
    formatted_text = ""
    for element, value in section_content.items():
        if isinstance(value, list):
            for item in value:
                formatted_text += format_nested_elements(item)
        elif isinstance(value, dict):
            formatted_text += element.upper() + "\n"
            formatted_text += format_nested_elements(value)
        else:
            formatted_text += element.capitalize().replace("_", " ") + ": " + value + "\n"
    return formatted_text

def enforce_section_item_values(generated_section, page, section):
    replacement_mapping = {
        "HOMEPAGE": {
            "AWARDS": {
                "title": "Collective Progress",
                "kicker": "Recognition"
            },
            "DISCOVER OTHER HOTELS": {
                "title": "The Pullman Collection"
            },
            "FAQ": {
                "title": "Your Questions, Answered"
            },
            "FOOD + BEVERAGE":{
                "title": "Dining + Nightlife"
            },
            "GETTING THERE":{
                "title": "Getting Here"
            },
            "INTRO":{
                "cta": "Virtual Tour"
            },
            "LOYALTY": {
                "title": "ALL The Perks",
                "kicker": "Loyalty"
            },
            "MEETINGS + EVENTS":{
                "title": "Meetings + Events"
            },
            "OFFERS": {
                "title": "Discover Our Offers"
            },
            "SUITES + ROOMS + APPARTMENTS": {
                "title": "Suites + Rooms + Appartments"
            },
            "SUSTAINABILITY": {
                "title": "Conscious Pioneers",
                "kicker": "Sustainability"
            },
        }, 
        "MICE DP": {
            "AMENITIES": {
                "title": "Thoughtful Amenities"
            },
            "DOWNLOADS": {
                "title": "All The Details"
            },
            "INTRO": {
                "cta": "Virtual Tour"
            },
            "FEATURED VENUES":{
                "title": "Visionary Venues",
                "carousel_cta": "Explore Venue"
            }
        },
        "MICE LP": {
            "INTRO": {
                "cta": "Meeting Brochure"
            },
            "MEETING PACKAGES + OFFERS" : {
                "title": "Exclusive Packages + Offers"
            },
            "MEETINGS AT HOTEL NAME": {
                "carousel_cta": "Explore"
            },
            "OUR MEETING ROOMS": {
                "title": "Our Meeting Rooms"
            },
            "SERVICE EXPERTISE": {
                "title": "Service Expertise"
            },
        },
        "RESTAURANT DP": {
            "DISCOVER OUR OFFERS":{
                "title": "Discover Our Offers"
            },
            "DOWNLOADS": {
                "title": "Seasonal Menus"
            },
            "MEET THE CHEF": {
                "kicker": "Meet The Chef"
            }
        },
        "ROOM DP": {
            "INTRO": {
                "cta": "Virtual Tour"
            },
            "SUITES + ROOMS + APPARTMENTS OVERVIEW": {
                "title": "Suites + Rooms + Appartments"
            }
        },
        "WELLNESS LP": {},
        "WEDDINGS LP": {
            "INTRO": {
                "cta": "Wedding Brochure"
            },
            "FOR EVERY OCCASION": {
                "title": "For Every Occasion"
            },
            "PULLMAN WEDDINGS": {
                "carousel_cta": "Explore Venue"
            },
            "WEDDING PACKAGES": {
                "title": "Tailored Wedding Packages"
            },
            "MENUES": {
                "title": "Our Offerings"
            }
        }
    }
    
    enforced_generated_section = deepcopy(generated_section)
    
    for item in generated_section:
        if section in replacement_mapping[page] and item in replacement_mapping[page][section]:
            enforced_generated_section[item] = replacement_mapping[page][section][item]
    
    return enforced_generated_section

def remove_excluded_page(website_content):
    page_exclusion_list = ["WEDDINGS LP"]
    page_removed_website_content = deepcopy(website_content)
    
    for page in page_exclusion_list:
        if page in website_content:
            del page_removed_website_content[page]
    return page_removed_website_content

# Fonction pour afficher un dictionnaire en Markdown avec une mise en forme spécifique
def st_display_dict_markdown(data_dict):
    for key, value in data_dict.items():
        if isinstance(value, dict):
            st.markdown(
                f"<span style='color: #7AA95C; text-decoration: underline;'>{key.capitalize()}</span>:<br>",
                unsafe_allow_html=True
            )
            st_display_dict_markdown(value)  # Recursively display sub-dictionaries
        elif isinstance(value, str):
            st.markdown(
                f"<span style='color: #7AA95C; text-decoration: underline;'>{key.capitalize()}</span>: {value}<br>",
                unsafe_allow_html=True
            )
        else:
            st.warning(f"Unexpected value type for key '{key}': {type(value)}")


# Fonction pour afficher un dictionnaire en Markdown avec une mise en forme spécifique (avec retour à la ligne après chaque clé)
def st_display_dict_markdown2(data_dict):
    for key, value in data_dict.items():
        # Utilisation de Markdown avec des balises span et du style CSS pour colorer en rouge et souligner
        st.markdown(
            f"<span style='color: #7AA95C; text-decoration: underline;'>{key.capitalize()}</span>: {value}<br>",
            unsafe_allow_html=True
        )
        
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