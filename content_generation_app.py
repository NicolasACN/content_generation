import streamlit as st
import json
import os
import shutil
from functions.old.data_processing import make_bloc_structure, fill_hotel_data
from functions.utils import choose_model, dict_to_markdown
from functions.utils import extract_brand_knowledge, extract_copywriting_guidelines

# App name and header
st.title("Content Generation")

# Tabs for project setup and data upload
tab1, tab2, tab3 = st.tabs(["Project Setup", "Data", "Content Generation"])

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
if "reference_examples" not in st.session_state:
    st.session_state.reference_examples_files = []
if "brand_docs" not in st.session_state:
    st.session_state.brand_docs = ""
if "copywriting_docs" not in st.session_state:
    st.session_state.copywriting_docs = ""
if "brand_knowledge" not in st.session_state:
    st.session_state['brand_knowledge'] = ""
if "copywriting_guidelines" not in st.session_state:
    st.session_state['copywriting_guidelines'] = ""
if 'structure_dict' not in st.session_state:
    st.session_state['structure_dict'] = {}
if 'data_dict' not in st.session_state:
    st.session_state['data_dict'] = {}
if 'filled_data' not in st.session_state:
    st.session_state['filled_data'] = {}
if 'generated_content' not in st.session_state:
    st.session_state['generated_content'] = {}

# Function to create project directory structure
def create_project_structure(project_name, project_brief):
    project_path = os.path.join(os.getcwd(), "projects", project_name)
    folders = [
        "data/brand_data",
        "data/persona",
        "data/copywriting",
        #"data/product_data",
        "data/reference_examples",
        "data/project_info",
        "prompts",
        "content"  # Create content folder as part of project creation
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
        
        # Load brand knowledge, copywriting guidelines, and reference examples
        load_brand_knowledge(project_name)
        load_copywriting_guidelines(project_name)
        load_reference_examples(project_name)

        st.success(f"Project '{project_name}' loaded successfully!")
    except Exception as e:
        st.error(f"Error loading project details: {e}")

# Function to setup content template
def setup_content_template(template_name, content_templates_path):
    new_template_path = os.path.join(content_templates_path, template_name)
    os.makedirs(new_template_path, exist_ok=True)
    os.makedirs(os.path.join(new_template_path, "content_data"), exist_ok=True)
    return new_template_path

# Functions to load brand knowledge, copywriting guidelines, and reference examples
def load_brand_knowledge(project_name):
    brand_knowledge_path = os.path.join(os.getcwd(), "projects", project_name, "data", "brand_data", "brand_knowledge.txt")
    if os.path.exists(brand_knowledge_path):
        with open(brand_knowledge_path, "r") as f:
            st.session_state.brand_docs = f.read()
    else:
        st.session_state.brand_docs = ""
        st.warning("No brand knowledge found.")
        
def load_copywriting_guidelines(project_name):
    copywriting_guidelines_path = os.path.join(os.getcwd(), "projects", project_name, "data", "copywriting", "copywriting_guidelines.txt")
    if os.path.exists(copywriting_guidelines_path):
        with open(copywriting_guidelines_path, "r") as f:
            st.session_state.copywriting_docs = f.read()
    else:
        st.session_state.copywriting_docs = ""
        st.warning("No copywriting guidelines found.")
        
def load_reference_examples(project_name):
    reference_examples_path = os.path.join(os.getcwd(), "projects", project_name, "data", "reference_examples", "reference_examples.txt")
    if os.path.exists(reference_examples_path):
        with open(reference_examples_path, "r") as f:
            st.session_state.reference_examples_files = f.read()
    else:
        st.session_state.reference_examples_files = ""
        st.warning("No reference examples found.")
        
def create_brand_knowledge():
    # Concatenate brand docs
    concatenated_docs = "\n\n---\n\n".join([file.read().decode("utf-8") for file in st.session_state.brand_knowledge_files])
    st.session_state.brand_docs = concatenated_docs
    # Extract brand knowledge
    st.session_state['brand_knowledge'] = extract_brand_knowledge(st.session_state.brand_docs)  

def create_copywriting_guidelines():
    concatenated_docs = "\n\n---\n\n".join([file.read().decode("utf-8") for file in st.session_state.copywriting_guidelines_files])
    st.session_state.copywriting_docs = concatenated_docs
    # Extract brand knowledge
    st.session_state['copywriting_guidelines'] = extract_copywriting_guidelines(st.session_state.copywriting_docs)  

def import_from_another_project(data_type):
    project_dir = os.path.join(os.getcwd(), "projects")
    projects = [d for d in os.listdir(project_dir) if os.path.isdir(os.path.join(project_dir, d))]
    selected_project = st.selectbox(f"Select a project to import {data_type} from", projects)

    if st.button(f"Import {data_type}"):
        if selected_project:
            if data_type == "brand knowledge":
                load_brand_knowledge(selected_project)
            elif data_type == "copywriting guidelines":
                load_copywriting_guidelines(selected_project)
            elif data_type == "reference examples":
                load_reference_examples(selected_project)
            st.success(f"{data_type.capitalize()} imported successfully from project '{selected_project}'!")
        else:
            st.error(f"Please select a project to import {data_type} from.")

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
    with st.expander("Brand Knowledge", expanded=False):
        import_from_another_project("brand knowledge")

        st.subheader("Create New Brand Knowledge")
        brand_knowledge_files = st.file_uploader("Upload Brand Knowledge Files", type=["txt"], accept_multiple_files=True)
        if st.button("Digest Brand Knowledge"):
            if brand_knowledge_files:
                st.session_state.brand_knowledge_files = brand_knowledge_files
                create_brand_knowledge()
                st.success("Brand knowledge files digested successfully.")
            else:
                st.error("Please upload brand knowledge files first.")
        
        if st.session_state.brand_docs:
            st.text_area("Brand Knowledge Preview", value=st.session_state.brand_docs, height=200)
            if st.button("Save Brand Knowledge"):
                brand_knowledge_path = os.path.join(os.getcwd(), "projects", st.session_state.project_name, "data", "brand_data", "brand_knowledge.txt")
                with open(brand_knowledge_path, "w") as f:
                    f.write(st.session_state.brand_docs)
                st.success("Brand knowledge saved successfully.")

    # Copywriting Guidelines Upload
    with st.expander("Copywriting Guidelines", expanded=False):
        import_from_another_project("copywriting guidelines")

        st.subheader("Create New Copywriting Guidelines")
        copywriting_guidelines_files = st.file_uploader("Upload Copywriting Guidelines Files", type=["txt"], accept_multiple_files=True)
        if st.button("Digest Copywriting Guidelines"):
            if copywriting_guidelines_files:
                st.session_state.copywriting_guidelines_files = copywriting_guidelines_files
                create_copywriting_guidelines()
                st.success("Copywriting guidelines files digested successfully.")
            else:
                st.error("Please upload copywriting guidelines files first.")
        
        if st.session_state.copywriting_docs:
            st.text_area("Copywriting Guidelines Preview", value=st.session_state.copywriting_docs, height=200)
            if st.button("Save Copywriting Guidelines"):
                copywriting_guidelines_path = os.path.join(os.getcwd(), "projects", st.session_state.project_name, "data", "copywriting", "copywriting_guidelines.txt")
                with open(copywriting_guidelines_path, "w") as f:
                    f.write(st.session_state.copywriting_docs)
                st.success("Copywriting guidelines saved successfully.")

    # Reference Examples Upload
    with st.expander("Reference Examples", expanded=False):
        import_from_another_project("reference examples")

        st.subheader("Create New Reference Examples")
        reference_examples_files = st.file_uploader("Upload Reference Examples Files", type=["txt"], accept_multiple_files=True)
        if st.button("Digest Reference Examples"):
            if reference_examples_files:
                concatenated_docs = "\n\n---\n\n".join([file.read().decode("utf-8") for file in reference_examples_files])
                st.session_state.reference_examples = concatenated_docs
                st.success("Reference examples files digested successfully.")
            else:
                st.error("Please upload reference examples files first.")
        
        if st.session_state.reference_examples_files:
            st.text_area("Reference Examples Preview", value=st.session_state.reference_examples_files, height=200)
            if st.button("Save Reference Examples"):
                reference_examples_path = os.path.join(os.getcwd(), "projects", st.session_state.project_name, "data", "reference_examples", "reference_examples.txt")
                with open(reference_examples_path, "w") as f:
                    f.write(st.session_state.reference_examples_files)
                st.success("Reference examples saved successfully.")

    # Debug Section
    with st.expander("Debug", expanded=False):
        st.subheader("Current Brand Knowledge")
        st.write(st.session_state['brand_knowledge'])
        st.subheader("Current Copywriting Guidelines")
        st.write(st.session_state['copywriting_guidelines'])
        st.subheader("Current Reference Examples")
        st.write(st.session_state['reference_examples'])

# New Tab 3: Content Generation
with tab3:
    st.header("Content Generation")
    
    # Section for selecting or creating a content template
    with st.expander("Select or Create Content Template", expanded=True):
        # Path for the content templates
        if st.session_state.project_name:
            content_templates_path = os.path.join(os.getcwd(), "projects", st.session_state.project_name, "content")
        else:
            content_templates_path = ""
        
        if content_templates_path and not os.path.exists(content_templates_path):
            os.makedirs(content_templates_path, exist_ok=True)
        
        if content_templates_path:
            # List existing templates
            content_templates = [d for d in os.listdir(content_templates_path) if os.path.isdir(os.path.join(content_templates_path, d))]
            content_templates.append("Create New Template")  # Option to create a new template

            selected_template = st.selectbox("Select an existing content template or create a new one", content_templates)
        
            if selected_template == "Create New Template":
                new_template_name = st.text_input("Enter new template name")
                create_template_button = st.button("Create Template")
                if create_template_button and new_template_name:
                    new_template_path = setup_content_template(new_template_name, content_templates_path)
                    
                    # Create empty JSON files
                    with open(os.path.join(new_template_path, 'content_data', 'content_structure.json'), 'w') as f:
                        json.dump({}, f)
                    with open(os.path.join(new_template_path, 'content_data', 'data_dict.json'), 'w') as f:
                        json.dump({}, f)
                    
                    st.success(f"Template '{new_template_name}' created successfully!")
                    st.session_state['structure_dict'] = {}  # Clear the structure dictionary for new template
                    st.session_state['data_dict'] = {}  # Clear the data dictionary for new template
            else:
                load_template_button = st.button("Load Template")
                if load_template_button:
                    # Load the selected template
                    template_path = os.path.join(content_templates_path, selected_template)
                    try:
                        if os.path.exists(os.path.join(template_path, 'content_data', 'content_structure.json')):
                            with open(os.path.join(template_path, 'content_data', 'content_structure.json'), 'r') as f:
                                st.session_state['structure_dict'] = json.load(f)
                        if os.path.exists(os.path.join(template_path, 'content_data', 'data_dict.json')):
                            with open(os.path.join(template_path, 'content_data', 'data_dict.json'), 'r') as f:
                                st.session_state['data_dict'] = json.load(f)
                        st.success(f"Template '{selected_template}' loaded successfully!")
                    except Exception as e:
                        st.error(f"Error loading template '{selected_template}': {e}")

    # Structure Section
    with st.expander("Create Content Structure", expanded=False):
        # Loading a predefined structure
        st.subheader("Import a predefined structure")
        if content_templates_path:
            templates = [d for d in os.listdir(content_templates_path) if os.path.isdir(os.path.join(content_templates_path, d))]
            selected_template_for_import = st.selectbox("Select a template folder", templates)
            import_structure_button = st.button("Load Structure")
            if import_structure_button:
                try:
                    template_path = os.path.join(content_templates_path, selected_template_for_import)
                    if os.path.exists(os.path.join(template_path, 'content_data', 'content_structure.json')):
                        with open(os.path.join(template_path, 'content_data', 'content_structure.json'), 'r') as f:
                            st.session_state['structure_dict'] = json.load(f)
                    if os.path.exists(os.path.join(template_path, 'content_data', 'data_dict.json')):
                        with open(os.path.join(template_path, 'content_data', 'data_dict.json'), 'r') as f:
                            st.session_state['data_dict'] = json.load(f)
                    st.success(f"Structure and data loaded successfully from '{selected_template_for_import}'!")
                except Exception as e:
                    st.error(f"Error loading structure and data from '{selected_template_for_import}': {e}")
                
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
                selected_page = st.selectbox("Select a page to add sections and elements", list(st.session_state['structure_dict'].keys()), key="section_page_select")
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
            page_list = list(st.session_state['structure_dict'].keys())
            selected_page = st.selectbox("Select a page", page_list, key="element_page_select")

            if selected_page:
                section_list = list(st.session_state['structure_dict'][selected_page].keys())
                selected_section = st.selectbox("Select a section", section_list, key="element_section_select")

                with st.form("add_element_form", clear_on_submit=True):
                    element_name = st.text_input("New element name")
                    nb_characters = st.text_input("Max number of characters")
                    content_guidelines = st.text_area("What is the content about?")
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

        if st.button("Save Structure"):
            template_path = os.path.join(content_templates_path, selected_template if selected_template != "Create New Template" else new_template_name)
            # Save structure dictionary
            with open(os.path.join(template_path, 'content_data', 'content_structure.json'), 'w') as f:
                json.dump(st.session_state['structure_dict'], f, indent=4)
            # Save data dictionary
            with open(os.path.join(template_path, 'content_data', 'data_dict.json'), 'w') as f:
                json.dump(st.session_state['data_dict'], f, indent=4)
            st.success(f"Structure and data saved successfully at {template_path}/content_data/content_structure.json and {template_path}/content_data/data_dict.json")

    # Data Factory Section
    with st.expander("Data Factory", expanded=False):
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
        
        if st.button("Save Content Data"):
            template_path = os.path.join(content_templates_path, selected_template if selected_template != "Create New Template" else new_template_name)
            # Save data dictionary
            with open(os.path.join(template_path, 'content_data', 'data_dict.json'), 'w') as f:
                json.dump(st.session_state['data_dict'], f, indent=4)
            
            # Fill data and save it
            st.session_state['filled_data'] = fill_hotel_data(st.session_state['structure_dict'], st.session_state['data_dict'])
            filled_data_path = os.path.join(template_path, 'content_data', 'filled_data.json')
            with open(filled_data_path, "w") as f:
                json.dump(st.session_state['filled_data'], f, indent=4)
            st.success(f"Content data saved successfully at {filled_data_path}")

    # Content Generation Section
    with st.expander("Generate Content", expanded=False):
        if st.session_state['filled_data'] == {}:
            st.warning("No filled data available. Please go to the Structure section and save data structures first.")
        else:
            if st.button("Generate Content"):
                # Assuming generate_content takes filled data and returns content
                model = choose_model("4-turbo")
                generated_content = generate_content(st.session_state['filled_data'], model=model)
                st.session_state['generated_content'] = generated_content
                # format and print content
                formated_content = dict_to_markdown(generated_content)
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

    # Debug Section
    with st.expander("Debug", expanded=False):
        st.subheader("Current Structure Dictionary")
        st.write(st.session_state['structure_dict'])
        st.subheader("Current Data Dictionary")
        st.write(st.session_state['data_dict'])
