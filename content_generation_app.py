import streamlit as st
import json
import os
import shutil
from functions.old.data_processing import make_bloc_structure, fill_hotel_data
# from functions.custom_generation import choose_model, generate_content
from functions.utils import choose_model
from functions.utils import dict_to_markdown
# from functions.chain import make_simple_harmonizer_chain

# App name and header
st.title("Content Generation")

# Tabs for project setup and data upload
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Project Setup", "Data", "Structure", "Data Factory", "Content Generation"])

# Initialize session state variables
if "project_name" not in st.session_state:
    st.session_state.project_name = ""
if "project_brief" not in st.session_state:
    st.session_state.project_brief = ""
if "project_action" not in st.session_state:
    st.session_state.project_action = "Select Existing Project"
if "selected_existing_project" not in st.session_state:
    st.session_state.selected_existing_project = ""
if "brand_knowledge_files" not in st.session_state:
    st.session_state.brand_knowledge_files = []
if "copywriting_guidelines_files" not in st.session_state:
    st.session_state.copywriting_guidelines_files = []
if "reference_examples_files" not in st.session_state:
    st.session_state.reference_examples_files = []
if 'structure_dict' not in st.session_state:
    st.session_state['structure_dict'] = {}
if 'data_dict' not in st.session_state:
    st.session_state['data_dict'] = {}
if 'filled_data' not in st.session_state:
    st.session_state['filled_data'] = {}

# Function to create project directory structure
def create_project_structure(project_name, project_brief):
    project_path = os.path.join(os.getcwd(), "projects", project_name)
    folders = [
        "data/brand_data",
        "data/persona",
        "data/platform_specs",
        "data/product_data",
        "data/reference_examples",
        "data/project_info",
        "prompts"
    ]

    for folder in folders:
        os.makedirs(os.path.join(project_path, folder), exist_ok=True)

    # Save project name and brief
    with open(os.path.join(project_path, "data/project_info/project_name.txt"), "w") as f:
        f.write(project_name)
    with open(os.path.join(project_path, "data/project_info/project_brief.txt"), "w") as f:
        f.write(project_brief)

    # Copy the prompts folder and its content
    source_prompts_path = os.path.join(os.getcwd(), "reference", "prompts")
    dest_prompts_path = os.path.join(project_path, "prompts")
    
    try:
        shutil.copytree(source_prompts_path, dest_prompts_path, dirs_exist_ok=True)
        st.success(f"Project '{project_name}' created successfully!")
    except Exception as e:
        st.error(f"Error copying prompts folder: {e}")

# Function to load existing project details
def load_project_details(project_name):
    project_path = os.path.join(os.getcwd(), "projects", project_name)
    project_info_path = os.path.join(project_path, "data", "project_info")

    try:
        with open(os.path.join(project_info_path, "project_name.txt"), "r") as f:
            st.session_state.project_name = f.read()
        with open(os.path.join(project_info_path, "project_brief.txt"), "r") as f:
            st.session_state.project_brief = f.read()
        st.success(f"Project '{project_name}' loaded successfully!")
    except Exception as e:
        st.error(f"Error loading project details: {e}")

with tab1:
    st.header("Project Setup")

    # Select existing project or create a new one
    st.session_state.project_action = st.radio("Select an action", ("Select Existing Project", "New Project"), index=("Select Existing Project", "New Project").index(st.session_state.project_action))

    if st.session_state.project_action == "New Project":
        st.subheader("Create New Project")

        # New project form
        with st.form(key='new_project_form'):
            st.session_state.project_name = st.text_input("Project Name", value=st.session_state.project_name)
            st.session_state.project_brief = st.text_area("Project Brief", value=st.session_state.project_brief)
            create_button = st.form_submit_button(label="Create")

        if create_button:
            if st.session_state.project_name:
                create_project_structure(st.session_state.project_name, st.session_state.project_brief)
            else:
                st.error("Project name is required.")
    else:
        st.subheader("Select Existing Project")
        project_dir = os.path.join(os.getcwd(), "projects")
        if os.path.exists(project_dir):
            projects = [d for d in os.listdir(project_dir) if os.path.isdir(os.path.join(project_dir, d))]
            st.session_state.selected_existing_project = st.selectbox("Select a project", projects, index=projects.index(st.session_state.selected_existing_project) if st.session_state.selected_existing_project in projects else 0)
            load_button = st.button("Load Project")

            if load_button:
                if st.session_state.selected_existing_project:
                    load_project_details(st.session_state.selected_existing_project)
                else:
                    st.error("Please select a project.")
        else:
            st.error("No projects directory found.")

with tab2:
    st.header("Data Upload")
    
    # Brand Knowledge Upload
    st.subheader("Brand Knowledge")
    brand_knowledge_files = st.file_uploader("Upload Brand Knowledge Files", type=["txt"], accept_multiple_files=True)
    if st.button("Digest Brand Knowledge"):
        if brand_knowledge_files:
            st.session_state.brand_knowledge_files = brand_knowledge_files
            st.success("Brand knowledge files digested successfully.")
        else:
            st.error("Please upload brand knowledge files first.")
    
    # Copywriting Guidelines Upload
    st.subheader("Copywriting Guidelines")
    copywriting_guidelines_files = st.file_uploader("Upload Copywriting Guidelines Files", type=["txt"], accept_multiple_files=True)
    if st.button("Digest Copywriting Guidelines"):
        if copywriting_guidelines_files:
            st.session_state.copywriting_guidelines_files = copywriting_guidelines_files
            st.success("Copywriting guidelines files digested successfully.")
        else:
            st.error("Please upload copywriting guidelines files first.")
    
    # Reference Examples Upload
    st.subheader("Reference Examples")
    reference_examples_files = st.file_uploader("Upload Reference Examples Files", type=["txt"], accept_multiple_files=True)
    if st.button("Digest Reference Examples"):
        if reference_examples_files:
            st.session_state.reference_examples_files = reference_examples_files
            st.success("Reference examples files digested successfully.")
        else:
            st.error("Please upload reference examples files first.")

# Tab 3: Structure
with tab3:
    st.header("Create Content Structure")
    
    # Loading a predefined structure
    st.subheader("Import a predefined structure")
    uploaded_file = st.file_uploader("Upload a content structure JSON file", type="json")
    if uploaded_file is not None:
        try:
            content_structure = json.load(uploaded_file)
            st.session_state['structure_dict'] = content_structure
            st.success("JSON file loaded successfully!")
        except json.JSONDecodeError:
            st.error("Failed to decode JSON file. Please upload a valid JSON file.")  
              
    # Create or edit the structure
    st.subheader("Add Pages")
    with st.form("add_page_form"):
        page_name = st.text_input("Enter new page name", key="page_input")
        submitted = st.form_submit_button("Add new page")
        if submitted and page_name:
            st.session_state['structure_dict'][page_name] = {}
            st.success(f"Page '{page_name}' added")

    st.subheader("Add Sections")
    if st.session_state['structure_dict']:
        with st.form("add_section_form"):
            selected_page = st.selectbox("Select a page to add sections and elements", list(st.session_state['structure_dict'].keys()))
            section_name = st.text_input("Enter new section name")
            submitted = st.form_submit_button("Add new section")
            if submitted and section_name:
                if selected_page and section_name:
                    st.session_state['structure_dict'][selected_page][section_name] = {
                        'bloc_guidelines': {},
                        'bloc_data': {},
                        'bloc_structure_string': {}
                    }
                    st.success(f"Section '{section_name}' added under page '{selected_page}'")
    else:
        st.write("Please add a page before adding sections.")

    st.subheader("Add Elements")
    if st.session_state['structure_dict']:
        with st.form("add_element_form", clear_on_submit=True):
            page_list = list(st.session_state['structure_dict'].keys())
            selected_page = st.selectbox("Select a page", page_list, key="element_page_select")
            section_list = []
            if selected_page:
                section_list = list(st.session_state['structure_dict'][selected_page].keys())
            selected_section = st.selectbox("Select a section", section_list, key="element_section_select")
            element_name = st.text_input("New element name")
            nb_characters = st.text_input("Max number of characters")
            content_guidelines = st.text_area("What is the content about ?")
            reference_content = st.text_area("Example content")
            data = st.text_input("Add data")
            submitted_element = st.form_submit_button("Add new element")
            if submitted_element and element_name and selected_section:
                element_info = {
                    "nb_characters": nb_characters,
                    "content_guidelines": content_guidelines,
                    "reference_content": reference_content
                }
                # Add to bloc guidelines
                st.session_state['structure_dict'][selected_page][selected_section]['bloc_guidelines'][element_name] = element_info
                # Add to bloc data
                if data:
                    data_list = [elt.strip(' ') for elt in data.split(',')]
                    for data_element in data_list:
                        if data_element and data_element not in st.session_state['structure_dict'][selected_page][selected_section]['bloc_data']:
                            st.session_state['structure_dict'][selected_page][selected_section]['bloc_data'][data_element] = {}
                            if not data_element in st.session_state['data_dict']:
                                st.session_state['data_dict'][data_element] = {}
                # Add bloc structure string
                st.session_state['structure_dict'][selected_page][selected_section]['bloc_structure_string'] = make_bloc_structure(st.session_state['structure_dict'][selected_page][selected_section]['bloc_guidelines'])

                st.success(f"Element '{element_name}' added under section '{selected_section}'")

    st.subheader("Debug")
    st.write("Current Structure Dictionary:", st.session_state['structure_dict'])
    st.write("Current Data Dictionary:", st.session_state['data_dict'])

# Tab 4: Data Factory
with tab4:
    st.header("Data Factory")
    
    st.subheader("Import existing data")
    uploaded_file = st.file_uploader("Upload existing data as JSON file", type="json")
    if uploaded_file is not None:
        try:
            existing_data = json.load(uploaded_file)
            st.session_state['data_dict'] = existing_data
            st.success("JSON file loaded successfully!")
        except json.JSONDecodeError:
            st.error("Failed to decode JSON file. Please upload a valid JSON file.") 
            
    for data in list(st.session_state['data_dict'].keys()):
        with st.form(f"data_form_{data}"):
            # Create fields to enter value and description
            value = st.text_input(f"Value for {data}", key=f"value_{data}")
            description = st.text_area(f"Description for {data}", key=f"description_{data}")
            # Submit button for each form
            submitted = st.form_submit_button(f"Save {data}")
            if submitted:
                st.session_state['data_dict'][data]['value'] = value
                st.session_state['data_dict'][data]['description'] = description
                st.success(f"Data for {data} saved!")
    
    st.subheader("Debug")
    st.write("Current Data Dictionary:", st.session_state['data_dict'])
    
    # Saving the dictionaries
    with st.sidebar:
        st.header("Save Data")
        built_data_path = os.path.join(os.getcwd(), 'data', 'built_data')
        os.makedirs(built_data_path, exist_ok=True)
        
        if st.button("Save Data Structures"):
            if built_data_path:
                # Save structure dictionary
                with open(os.path.join(built_data_path, 'template', 'hotel_data_template.json'), 'w') as f:
                    json.dump(st.session_state['structure_dict'], f, indent=4)
                # Save data dictionary
                with open(os.path.join(built_data_path, 'data_dict', 'data_dict.json'), 'w') as f:
                    json.dump(st.session_state['data_dict'], f, indent=4)
                
                # Fill data and save it
                st.session_state['filled_data'] = fill_hotel_data(st.session_state['structure_dict'], st.session_state['data_dict'])
                with open(os.path.join(built_data_path, 'filled_data', 'filled_data.json'), "w") as f:
                    json.dump(st.session_state['filled_data'], f, indent=4)
                st.success(f"Files saved successfully at {built_data_path}")

# Tab 5: Content Generation
with tab5:
    st.header("Content Generation")
    if st.session_state['filled_data'] == {}:
        st.warning("No filled data available. Please go to the Structure tab and save data structures first.")
    else:
        if st.button("Generate Content"):
            # Assuming generate_content takes filled data and returns content
            model = choose_model("4-turbo")
            generated_content = generate_content(st.session_state['filled_data'], model=model)
            st.session_state['generated_content'] = generated_content
            # format and print content
            formated_content = dict_to_markdown(generated_content)
            
            # # Harmonize Content
            # with open(os.path.join(os.getcwd(), "data", "experiments", "cw_guidelines", "cw_guidelines.txt"), "r") as f:
            #     cw_guidelines = f.read()
            # harmonizer = make_simple_harmonizer_chain(model)
            # harmonized_content = harmonizer.invoke({"input_text": formated_content, "cw_guidelines": cw_guidelines})
            # st.markdown(harmonized_content)
            
            st.markdown(formated_content)
            
        if 'generated_content' in st.session_state and st.session_state['generated_content']:
            # Folder selection and saving content
            st.subheader("Save Generated Content")
            save_path = st.text_input("Enter the folder path to save the content", key="save_folder")
            if st.button("Save Content"):
                if save_path:
                    if not os.path.exists(save_path):
                        os.makedirs(save_path, exist_ok=True)
                    with open(os.path.join(save_path, 'generated_content.json'), 'w') as f:
                        json.dump(st.session_state['generated_content'], f, indent=4)
                    st.success(f"Content saved successfully in {save_path}")
