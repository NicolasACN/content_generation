import os
from copy import deepcopy
from tqdm import tqdm
from .chain import choose_model, make_bloc_model_from_structure, make_bloc_guidelines_prompt_formating_chain, make_bloc_data_prompt_formating_chain, make_BM_review_feedback_chain, make_CW_review_feedback_chain, make_writing_chain, make_rewriting_chain, make_bloc_generation_chain, make_bloc_regeneration_chain, make_validation_chain, make_bloc_cw_guidelines_prompt_formating_chain, make_bloc_context_prompt_formating_chain, make_seo_section_generation_chain, make_TOV_review_feedback_chain, make_lexicon_post_processing_chain

def get_instance_list(data, page):
    sections = list(data[page].keys())
    for section in sections:
        if not data[page][section]['bloc_data']:
            continue
        for variable_name in data[page][section]['bloc_data'].keys():
            if not 'value' in data[page][section]['bloc_data'][variable_name].keys():
                return list(data[page][section]['bloc_data'][variable_name].keys())
    print(f"GET INSTANCE LIST ERROR: found an empty list of instance for the DP Page : {page}")
    return {}

def get_section_data(data, page, section=None, instance_name=None):
    # Empty bloc data case
    if not data[page][section]['bloc_data']:
        return data[page][section]
    # Non empty bloc data case
    # multi_instance_pages = ['ROOM DP', 'RESTAURANT DP', 'MICE DP']    
    # if page not in multi_instance_pages:
    #     return hotel_data[page][section]
    # else:
    #     if not instance_name:
    #         instance_list = get_instance_list(hotel_data, page)
    #         instance_name = instance_list[0]

    #     section_data = deepcopy(hotel_data[page][section])
    #     for variable_name in hotel_data[page][section]['bloc_data']:
    #         # not instanced variable case
    #         if not 'value' in section_data['bloc_data'][variable_name]:
    #             section_data['bloc_data'][variable_name] = section_data['bloc_data'][variable_name][instance_name]
    #         # multi instance variable case
    #         else:
    #             # keep the variable as it is
    #             continue
    #        return section_data

    return data[page][section]
    
def generate_section(data, page, section, cw_guidelines="", bm_guidelines="", reference_content="", instance_name=None, intermediate_output_folder="./output/intermediate-output", max_iter=1, model=choose_model("3.5"), version=0, max_attempts=2, log_intermediate=False):
        #PROMPT_FOLDER_PATH = os.path.join(os.getcwd(), 'prompts')
        #writing_prompt = os.path.join(PROMPT_FOLDER_PATH, 'Copywriting')
        #rewriting_prompt = os.path.join(PROMPT_FOLDER_PATH, 'Rewriter')
        #bm_review_prompt = os.path.join(PROMPT_FOLDER_PATH, 'BMReview')
        #cw_review_prompt = os.path.join(PROMPT_FOLDER_PATH, 'CWReview')
        #validation_prompt = os.path.join(PROMPT_FOLDER_PATH, 'Validation')
        
        #multi_instance_pages = ['ROOM DP', 'MICE DP', 'RESTAURANT DP']
        
        
        section_data = get_section_data(data, page, section, instance_name)
        section_structure_model = make_bloc_model_from_structure(section_data['bloc_structure_string'])
        
        # Make input data
        #persona = read_file(os.path.join(os.getcwd(), 'data', 'persona.txt'))
        #bm_guidelines = read_file(os.path.join(os.getcwd(), 'data', 'bm_guidelines.txt'))
        #cw_guidelines = read_file(os.path.join(os.getcwd(), 'data', 'cw_guidelines.txt'))

        input_data = section_data | {
            "bm_guidelines": bm_guidelines,
            # NEW : CW_GUIDELINES NOW RUNNABLE IN CHAIN
            "cw_guidelines": cw_guidelines,
            "page": page, 
            "section": section, 
            "instance_name": instance_name
        }
        
        # Make chains
        ## Base chains
        bloc_CW_guidelines_prompt_formating_chain = make_bloc_cw_guidelines_prompt_formating_chain()
        bloc_data_prompt_formating_chain = make_bloc_data_prompt_formating_chain()
        bloc_guidelines_prompt_formating_chain = make_bloc_guidelines_prompt_formating_chain()
        bloc_content_prompt_formating_chain = make_bloc_context_prompt_formating_chain() ## new
        
        # Without prompt as Global Variables
        #BM_review_feedback_chain = make_BM_review_feedback_chain(model, bm_review_prompt)
        #CW_review_feedback_chain = make_CW_review_feedback_chain(model, cw_review_prompt)
        #validation_chain = make_validation_chain(model, validation_prompt)
        #first_draft_writing_chain = make_writing_chain(model, writing_prompt, section_structure_model)
        #rewriting_chain = make_rewriting_chain(model, rewriting_prompt, section_structure_model)        
        
        # With prompt as Global Variables
        BM_review_feedback_chain = make_BM_review_feedback_chain(model)
        CW_review_feedback_chain = make_CW_review_feedback_chain(model)
        TOV_review_feedback_chain = make_TOV_review_feedback_chain(model, reference_content)
        validation_chain = make_validation_chain(model)
        first_draft_writing_chain = make_writing_chain(model, section_structure_model)
        rewriting_chain = make_rewriting_chain(model, section_structure_model)
        lexicon_post_processing_chain = make_lexicon_post_processing_chain(model, cw_guidelines)
        
        ## Generation Chains
        ### write first draft chain
        write_first_draft_chain = make_bloc_generation_chain(
            bloc_CW_guidelines_prompt_formating_chain,
            bloc_data_prompt_formating_chain,
            bloc_guidelines_prompt_formating_chain,
            bloc_content_prompt_formating_chain,
            first_draft_writing_chain,
            BM_review_feedback_chain,
            CW_review_feedback_chain,
            TOV_review_feedback_chain,
            validation_chain
            )
        
        ### rewriting chain
        improve_draft_chain = make_bloc_regeneration_chain(
            rewriting_chain,
            BM_review_feedback_chain,
            CW_review_feedback_chain,
            TOV_review_feedback_chain,
            validation_chain
            )
        
        # Préparation du fichier et du dossier de sortie
        if log_intermediate:
            os.makedirs(intermediate_output_folder, exist_ok=True)
            draft_file_path = os.path.join(intermediate_output_folder, f"bloc_draft_and_feedbacks_{version}.txt")

        
        version_count = 0
        
        # GENERATE SECTION
        attempts = 0
        while attempts < max_attempts:
            try: 
                # Create input_dict
                #input_dict = section_data | {
                #    "persona": input_dict['persona'],
                #    "cw_guidelines": input_dict['cw_guidelines'],
                #    "bm_guidelines": input_dict['bm_guidelines'],
                #}
                
                # Write first draft
                output_dict = write_first_draft_chain.invoke(input_data)
                print(f'FIRST OUTPUT DICT: {output_dict}')
                #validation = output_dict['validation']['validation']
                # TODO DEBUG REMOVE
                validation = False
                #print(output_dict)

                # if log_intermediate:
                #     save_versioned_data(draft_file_path, output_dict, version_count)
                
                version_count += 1
                
                # Rewrite section loop
                #intermediate_output = deepcopy(output_dict)
                # While starts at version count = 1 
                while not validation and version_count < max_iter + 1:
                    intermediate_input_data = {
                        "formated_bloc_data": output_dict['formated_bloc_data'],
                        "formated_bloc_guidelines": output_dict['formated_bloc_guidelines'],
                        "formated_bloc_context": output_dict['formated_bloc_context'], ## new
                        "bm_review": output_dict['bm_review'],
                        "cw_review": output_dict['cw_review'],
                        "tov_review": output_dict['tov_review'],
                        "generated_bloc": output_dict['generated_bloc'],
                        "bloc_data": input_data['bloc_data'],
                        "bloc_guidelines": input_data['bloc_guidelines'],
                        # "cw_guidelines": input_data['cw_guidelines'],
                        # NEW 
                        "cw_guidelines": output_dict['cw_guidelines'],
                        "bm_guidelines": input_data['bm_guidelines'],
                        "page": input_data['page']
                    }
                    
                    # Regenerate section
                    output_dict = improve_draft_chain.invoke(intermediate_input_data)
                    # TODO : remove debug !
                    print(f"OUTPUT DICT: {output_dict}")
                    
                    #validation = output_dict['validation']['validation']
                    
                    # if log_intermediate:
                    #     save_versioned_data(draft_file_path, output_dict, version_count)
                    
                    version_count += 1
                
                generated_section = output_dict['generated_bloc']
                break
            
            except Exception as e:
                print(f"An error has occured: {e}")
                if attempts == max_attempts:
                    print("Function failed after maximum retries")
                else:
                    attempts += 1
                    print(f"Retrying... Attempt {attempts + 1}")
                raise e
        
        # Lexicon Post Processing 
        for element in generated_section:
            if isinstance(generated_section[element], str):
                generated_section[element] = lexicon_post_processing_chain.invoke({
                    'page': page, 
                    'section': section,
                    'generated_text': generated_section[element]
                })
            elif isinstance(generated_section[element], list):
                formated_list = []
                for nested_element in generated_section[element]:
                    formated_dict = {}
                    for sub_nested_element in nested_element:
                        if isinstance(nested_element[sub_nested_element], str):
                            formated_dict[sub_nested_element] = lexicon_post_processing_chain.invoke({
                                "page": page,
                                "section": section,
                                "generated_text": nested_element[sub_nested_element]
                            })
                    formated_list.append(formated_dict)
                generated_section[element] = formated_list
                
        
        # ENFORCE VALUE 
        #if generated_section and page and section:
        #    generated_section = enforce_section_item_values(generated_section, page, section)
        
        return generated_section 

def generate_page_seo_section(generated_page, page, model):
    seo_section_generation_chain = make_seo_section_generation_chain(model)
    return seo_section_generation_chain.invoke({
        "page": page, 
        "page_content": generated_page,
    })
    
def generate_seo_sections(generated_page, model):
    seo_enriched_website = deepcopy(generated_page)
    for page in generated_page:
        seo_enriched_website[page]["SEO"] = generate_page_seo_section(generated_page[page], page, model)
    return seo_enriched_website

def generate_page(data, page, cw_guidelines="", bm_guidelines="", reference_content="", instance_name=None, intermediate_output_folder="./intermediate-output", max_iter=1, model=choose_model("3.5"), version=0, log_intermediate=False, include_seo=False):
    generated_sections = {}
    
    # multi_instance_pages = ['ROOM DP', 'MICE DP', 'RESTAURANT DP']
    # Il pourrait y avoir un probleme avec page MICE LP a la section OUR MEETING ROOMS (ou un truc du genre): TO BE CONFIRMED
    
    # cas ou c'est une page simple (pas de différentes instances de la page)
    for section in tqdm(data[page]):
        generated_sections[section] = generate_section(data=data, page=page, section=section, intermediate_output_folder=intermediate_output_folder, max_iter=max_iter, model=model, version=version, log_intermediate=log_intermediate, cw_guidelines=cw_guidelines, bm_guidelines=bm_guidelines, reference_content=reference_content)
    
    # else:
    #     if not instance_name:
    #         instance_list = get_instance_list(data, page)
    #         # Ce qu'il faudrait faire (si on a le temps): itérer sur toutes les instances et créer la page
    #         #for instance in instance_list:
    #         #    generate_section(hotel_data, page, section, instance)
            
    #         # ce qu'on fait plutôt: on prend la premiere instance pour l'instant et on génère seulement cette page
    #         instance_name = instance_list[0]
    #     for section in tqdm(data[page]):
    #         generated_sections[section] = generate_section(hotel_data=data, page=page, section=section, instance_name=instance_name, intermediate_output_folder=intermediate_output_folder, max_iter=max_iter, model=model, version=version, log_intermediate=log_intermediate)
    
    # TODO : Add Page Harmonizer
    
    # TODO : Add SEO
    if include_seo:
        generated_sections["SEO"] = generate_page_seo_section(generated_sections, page, model)
    return generated_sections

def generate_content(data, cw_guidelines='', bm_guidelines='', reference_content="", output_folder="./output", intermediate_output_folder="./intermediate-output", max_iter=1, model=choose_model("3.5"), version=0, log_intermediate=False):
    website_content = {}
    # loop sur toutes les pages pour écrire la page 
    for page in tqdm(data):
        website_content[page] = generate_page(data=data, page=page, intermediate_output_folder=intermediate_output_folder, max_iter=max_iter, model=model, version=version, log_intermediate=log_intermediate, cw_guidelines=cw_guidelines, bm_guidelines=bm_guidelines, reference_content=reference_content)
            # page_to_excel(website_content[page], page, output_dir=output_folder)
        # update to json
    # Remove out of scope pages
    #oos_page_removed_website_content = remove_excluded_page(website_content)
    
    # TMP
    oos_page_removed_website_content = website_content
    
    return oos_page_removed_website_content
