import os
from copy import deepcopy
from tqdm import tqdm
from .utils import character_limit_check_section, load_message_prompts
from .chain import choose_model, make_bloc_model_from_structure, make_bloc_guidelines_prompt_formating_chain, make_bloc_data_prompt_formating_chain, make_BM_review_feedback_chain, make_CW_review_feedback_chain, make_writing_chain, make_rewriting_chain, make_bloc_generation_chain, make_bloc_regeneration_chain, make_TOV_review_feedback_chain
# TODO : re add later
#from .chain import make_seo_section_generation_chain, make_lexicon_post_processing_chain


def get_section_data(content_data, page, section=None, instance_name=None):
    if not content_data[page][section]['bloc_data']:
        return content_data[page][section]
    return content_data[page][section]

    # multi_instance_pages = ['ROOM DP', 'RESTAURANT DP', 'MICE DP']
    # if page not in multi_instance_pages:
    #     return hotel_data[page][section]
    # else:
    #     if not instance_name:
    #         instance_list = get_instance_list(hotel_data, page)
    #         instance_name = instance_list[0]

    #     section_data = deepcopy(hotel_data[page][section])
    #     for variable_name in hotel_data[page][section]['bloc_data']:
    #         if not 'value' in section_data['bloc_data'][variable_name]:
    #             section_data['bloc_data'][variable_name] = section_data['bloc_data'][variable_name][instance_name]
    #         else:
    #             continue
    #     return section_data
    
def generate_section(content_data, page, section, content_brief="", reference_examples="", prompt_folder="./reference/prompts", language="British English", project="", role="world recognized copywriter", instance_name=None, cw_guidelines="", brand_knowledge="", intermediate_output_folder="./output/intermediate-output", max_iter=1, model=choose_model("4o"), version=0, max_attempts=2, log_intermediate=False):
    # Load Prompts
    assert os.path.exists(prompt_folder)
    writing_prompt_path = os.path.join(prompt_folder, 'Copywriting')
    rewriting_prompt_path = os.path.join(prompt_folder, 'Rewriting')
    #bm_review_prompt_path = os.path.join(prompt_folder, 'BrandReview')
    cw_review_prompt_path = os.path.join(prompt_folder, 'CopywritingReview')
    tov_review_prompt_path = os.path.join(prompt_folder, "TOVReview")
    # seo_keywords_prompt_path = os.path.join(prompt_folder, 'SEOKeywords')
    # seo_writer_prompt_path = os.path.join(prompt_folder, 'SEOWriter')
    
    ## Prompts
    #brand_review_and_feedback_system_message_prompt, brand_review_and_feedback_human_message_prompt  = load_message_prompts(bm_review_prompt_path)
    cw_review_and_feedback_system_message_prompt, cw_review_and_feedback_human_message_prompt = load_message_prompts(cw_review_prompt_path)
    tov_review_and_feedback_system_message_prompt, tov_review_and_feedback_human_message_prompt = load_message_prompts(tov_review_prompt_path)
    writing_system_message_prompt, writing_human_message_prompt = load_message_prompts(writing_prompt_path)
    rewriting_system_message_prompt, rewriting_human_message_prompt = load_message_prompts(rewriting_prompt_path)
    # seo_keywords_system_message_prompt, seo_keywords_human_message_prompt = load_message_prompts(seo_keywords_prompt_path)
    # seo_writer_system_message_prompt, seo_writer_human_message_prompt = load_message_prompts(seo_writer_prompt_path)
        
    # Load Section Data & Structure Model
    section_data = get_section_data(content_data, page, section, instance_name)
    section_structure_model = make_bloc_model_from_structure(section_data['bloc_structure_string'])
    

    input_data = section_data | {
        "bm_guidelines": brand_knowledge,
        "cw_guidelines": cw_guidelines,
        "page": page, 
        "section": section, 
        "instance_name": instance_name,
        "language": language,
        "project": project, 
        "role": role,
        "reference_examples": reference_examples,
        "content_brief": content_brief
    }
    
    #print(input_data)
    # Make chains
    ## Base chains
    #bloc_CW_guidelines_prompt_formating_chain = make_bloc_cw_guidelines_prompt_formating_chain()
    bloc_data_prompt_formating_chain = make_bloc_data_prompt_formating_chain()
    bloc_guidelines_prompt_formating_chain = make_bloc_guidelines_prompt_formating_chain()
    #bloc_content_prompt_formating_chain = make_bloc_context_prompt_formating_chain() ## new
    
    # Without prompt as Global Variables
    #BM_review_feedback_chain = make_BM_review_feedback_chain(model, bm_review_prompt)
    #CW_review_feedback_chain = make_CW_review_feedback_chain(model, cw_review_prompt)
    #validation_chain = make_validation_chain(model, validation_prompt)
    #first_draft_writing_chain = make_writing_chain(model, writing_prompt, section_structure_model)
    #rewriting_chain = make_rewriting_chain(model, rewriting_prompt, section_structure_model)        
    
    #BM_review_feedback_chain = make_BM_review_feedback_chain(model, brand_review_and_feedback_system_message_prompt, brand_review_and_feedback_human_message_prompt)
    CW_review_feedback_chain = make_CW_review_feedback_chain(model, cw_review_and_feedback_system_message_prompt, cw_review_and_feedback_human_message_prompt)
    TOV_review_feedback_chain = make_TOV_review_feedback_chain(model, tov_review_and_feedback_system_message_prompt, tov_review_and_feedback_human_message_prompt)
    first_draft_writing_chain = make_writing_chain(model, section_structure_model, writing_system_message_prompt, writing_human_message_prompt)
    rewriting_chain = make_rewriting_chain(model, section_structure_model, rewriting_system_message_prompt, rewriting_human_message_prompt)
    #TODO : If needed add lexicon post processing chain
    #lexicon_post_processing_chain = make_lexicon_post_processing_chain(model)
    
    ## Generation Chains
    ### write first draft chain
    write_first_draft_chain = make_bloc_generation_chain(
        bloc_data_prompt_formating_chain,
        bloc_guidelines_prompt_formating_chain,
        first_draft_writing_chain,
        #BM_review_feedback_chain,
        CW_review_feedback_chain,
        TOV_review_feedback_chain,
        )
    
    ### rewriting chain
    improve_draft_chain = make_bloc_regeneration_chain(
        rewriting_chain,
        #BM_review_feedback_chain,
        CW_review_feedback_chain,
        TOV_review_feedback_chain,
        )
    
    # Préparation du fichier et du dossier de sortie
    # if log_intermediate:
    #     os.makedirs(intermediate_output_folder, exist_ok=True)
    #     draft_file_path = os.path.join(intermediate_output_folder, f"bloc_draft_and_feedbacks_{version}.txt")

    
    # version_count = 0
    
    # GENERATE SECTION
    #attempts = 0
    
    character_limit = {element: input_data['bloc_guidelines'][element]["nb_characters"] for element in input_data['bloc_guidelines']}
    # TODO : faked for now : to smooth later
    passed_content_length_check = False
    while not passed_content_length_check:
    #     try: 
            # Create input_dict
            #input_dict = section_data | {
            #    "persona": input_dict['persona'],
            #    "cw_guidelines": input_dict['cw_guidelines'],
            #    "bm_guidelines": input_dict['bm_guidelines'],
            #}
            
            # Write first draft
        output_dict = write_first_draft_chain.invoke(input_data)
        # validation = output_dict['validation']['validation']
        #print(output_dict)

        # if log_intermediate:
        #     save_versioned_data(draft_file_path, output_dict, version_count)
        
        # version_count += 1
        
        # Rewrite section loop
        #intermediate_output = deepcopy(output_dict)
        # While starts at version count = 1 
        intermediate_input_data = {
            "formated_bloc_data": output_dict['formated_bloc_data'],
            "formated_bloc_guidelines": output_dict['formated_bloc_guidelines'],
            #"formated_bloc_context": output_dict['formated_bloc_context'], ## new
            #"bm_review": output_dict['bm_review'],
            "cw_review": output_dict['cw_review'],
            "tov_review": output_dict['tov_review'],
            "generated_text": output_dict['generated_text'],
            "bloc_data": input_data['bloc_data'],
            "bloc_guidelines": input_data['bloc_guidelines'],
            # "cw_guidelines": input_data['cw_guidelines'],
            # NEW 
            "cw_guidelines": cw_guidelines,
            "bm_guidelines": brand_knowledge,
            "page": input_data['page'],
            "language": language,
            "project": project, 
            "role": role,
            "reference_examples": reference_examples,
            "content_brief": content_brief
        }
        
        # Regenerate section
        output_dict = improve_draft_chain.invoke(intermediate_input_data)
        #validation = output_dict['validation']['validation']
        
        generated_section = output_dict['generated_text']
        
        # Content Length Check
        try:
            #TODO : do the check for real (add tolerance)
            # passed_content_length_check = character_limit_check_section(generated_section, character_limit)
            passed_content_length_check = True
        except Exception as e:
            print(f"ERROR AT {generated_section} with char limit {character_limit}")
            raise e
        
        # DEBUG
        if not passed_content_length_check:
            print("Didnt pass content length check. Rewriting")

        # except Exception as e:
        #     print(f"An error has occured: {e}")
        #     if attempts == max_attempts:
        #         print("Function failed after maximum retries")
        #     else:
        #         attempts += 1
        #         print(f"Retrying... Attempt {attempts + 1}")
        #     raise e
    
    # TODO : if needed add lexicon post processing (use Pullman's)
    # No Lexicon Post Processing at this stage
    # # Lexicon Post Processing 
    # for element in generated_section:
    #     if isinstance(generated_section[element], str):
    #         generated_section[element] = lexicon_post_processing_chain.invoke({
    #             'page': page, 
    #             'section': section,
    #             'generated_text': generated_section[element]
    #         })
    #     elif isinstance(generated_section[element], list):
    #         formated_list = []
    #         for nested_element in generated_section[element]:
    #             formated_dict = {}
    #             for sub_nested_element in nested_element:
    #                 if isinstance(nested_element[sub_nested_element], str):
    #                     formated_dict[sub_nested_element] = lexicon_post_processing_chain.invoke({
    #                         "page": page,
    #                         "section": section,
    #                         "generated_text": nested_element[sub_nested_element]
    #                     })
    #             formated_list.append(formated_dict)
    #         generated_section[element] = formated_list
            
    
    # # ENFORCE VALUE 
    # if generated_section and page and section:
    #     generated_section = enforce_section_item_values(generated_section, page, section, section_data)
    
    # # Remove Title and kicker ponctuation
    # if 'title' in generated_section:
    #     generated_section['title'] = remove_punctuation(generated_section['title'])
    # if 'kicker' in generated_section:
    #     generated_section['kicker'] = remove_punctuation(generated_section['kicker'])
    return generated_section

def generate_page(content_data, page, content_brief="", reference_examples="", project="", role="world recognized copywriter", language="British English", prompt_folder="./reference/prompts", brand_knowledge="", cw_guidelines="", instance_name=None, intermediate_output_folder="./intermediate-output", max_iter=1, model=choose_model("4o"), version=0, log_intermediate=False):
    generated_sections = {}
    for section in tqdm(content_data[page]):
        generated_sections[section] = generate_section(content_data=content_data, content_brief=content_brief, reference_examples=reference_examples, page=page, section=section, project=project, role=role, language=language, prompt_folder=prompt_folder, brand_knowledge=brand_knowledge, cw_guidelines=cw_guidelines, intermediate_output_folder=intermediate_output_folder, max_iter=max_iter, model=model, version=version, log_intermediate=log_intermediate)

    # multi_instance_pages = ['ROOM DP', 'MICE DP', 'RESTAURANT DP']
    
    # if page not in multi_instance_pages:
    #     for section in tqdm(content_data[page]):
    #         generated_sections[section] = generate_section(content_data=content_data, page=page, section=section, brand_knowledge=brand_knowledge, cw_guidelines=cw_guidelines, intermediate_output_folder=intermediate_output_folder, max_iter=max_iter, model=model, version=version, log_intermediate=log_intermediate)
    # else:
    #     instance_list = get_instance_list(hotel_data, page)
    #     for instance in instance_list:
    #         instance_generated_sections = {}
    #         for section in tqdm(hotel_data[page]):
    #             instance_generated_sections[section] = generate_section(hotel_data=hotel_data, page=page, section=section, instance_name=instance, intermediate_output_folder=intermediate_output_folder, max_iter=max_iter, model=model, version=version, log_intermediate=log_intermediate)
    #         generated_sections[instance] = instance_generated_sections
    
    # TODO : SEO add later
    #generated_sections["SEO"] = generate_page_seo_section(generated_sections, page, model)
    return generated_sections

# TODO : SEO add later
# def generate_page_seo_section(generated_page, page, model):
#     seo_section_generation_chain = make_seo_section_generation_chain(model)
#     return seo_section_generation_chain.invoke({
#         "page": page, 
#         "page_content": generated_page,
#     })
    
# def generate_seo_sections(generated_content, model):
#     seo_enriched_content = deepcopy(generated_content)
#     for page in generated_content:
#         seo_enriched_content[page]["SEO"] = generate_page_seo_section(generated_content[page], page, model)
#     return seo_enriched_content

def generate_content(content_data, content_brief="", reference_examples="", project="", role="world recognized copywriter", language="British English", prompt_folder="./reference/prompts", brand_knowledge="", cw_guidelines="", output_folder="./output", intermediate_output_folder="./intermediate-output", max_iter=1, model=choose_model("4o"), version=0, log_intermediate=False):
    generated_content = {}
    
    for page in tqdm(content_data):
        # if page == 'WEDDINGS LP':
        #     continue
        # else:
        #     website_content[page] = generate_page(content_data=content_data, page=page, intermediate_output_folder=intermediate_output_folder, max_iter=max_iter, model=model, version=version, log_intermediate=log_intermediate)
        generated_content[page] = generate_page(content_data=content_data, page=page, content_brief=content_brief, reference_examples=reference_examples, project=project, role=role, language=language, prompt_folder=prompt_folder, brand_knowledge=brand_knowledge, cw_guidelines=cw_guidelines, intermediate_output_folder=intermediate_output_folder, max_iter=max_iter, model=model, version=version, log_intermediate=log_intermediate)
    
    #oos_page_removed_website_content = remove_excluded_page(website_content)
    
    return generated_content
