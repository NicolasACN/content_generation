###########################################################################################
# Ce fichier a été crée pour exposer des endpoints pour communiquer avec une API dans le  #
#  cadre d'une démo. Il est toujours possible de faire fonctionner l'app avec Streamlit.  #
#    Vous pouver ne pas tenir compte de ce fichier si vous n'utilisez pas l'app en mode   # 
#                                       serveur API                                       #
###########################################################################################
import os
import shutil
import json
from flask import Flask, request, jsonify
from models.objectModels import Project
from functions.old.data_processing import fill_hotel_data
from models.requestModels import CreateProjectResponse
from functions.utils import choose_model, extract_brand_knowledge, extract_copywriting_guidelines
from functions.generation import generate_content

app = Flask(__name__)

#####################################
#                                   #
#             Fonctions             #
#                                   #
#####################################

# Function to create project directory structure
def create_project_structure(project_name, project_brief):
    response = CreateProjectResponse()
    project_path = os.path.join(os.getcwd(), "projects", project_name)
    folders = [
        "data/brand_data",
        "data/persona",
        "data/copywriting",
        "data/role",
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
        response.projectName = project_name
        response.message = (f"Project '{project_name}' created successfully!")
        response.success = True
    except Exception as e:
        response.message = (f"Error created project '{project_name}' : {e}")
    finally:
        return response

# Function to create project directory structure
def get_all_projects():
    projects_list = []
    projects_dir = os.path.join(os.getcwd(), "projects")

    if os.path.exists(projects_dir):
        projects = [d for d in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, d))]
        for projectName in projects:
            brief_path = os.path.join(os.getcwd(), "projects", projectName, "data", "content", "brief", "brief.txt")
            # verification de l'existance du fichier
            if os.path.exists(brief_path):
                # lecture et extraction du contenu du fichier
                with open(brief_path, "r", encoding='utf-8') as f:
                    content = f.read()

                project = Project() 
                project.name = projectName
                project.brief = content
                projects_list.append(project)
    
    return projects_list

# Function for load project details
def load_project_details(project_name: str):
    try:
        project_path = os.path.join(os.getcwd(), "projects", project_name)
        if not os.path.exists(project_path):
            raise RuntimeError(f"Failed to load project details: {project_name} n'existe pas")
        project_info_path = os.path.join(project_path, "data", "project_info")

        with open(os.path.join(project_info_path, "project_brief.txt"), "r") as f:
            project_brief = f.read()
        
        # Load brand knowledge, copywriting guidelines, reference examples, and role
        brand_knowledge=load_data_file(project_name, "brand_data", "brand_knowledge")
        copywriting_guidelines=load_data_file(project_name, "copywriting", "copywriting_guidelines")
        reference_examples=load_data_file(project_name, "reference_examples", "reference_examples")
        role=load_data_file(project_name, "role", "role")
        brief=load_data_file(project_name,"brief","brief")
    
        # Simulated logic for loading project details, replace with actual logic
        # For example, load data from a database or file based on the project name
        return {
            "project_name": project_name,
            "project_brief": project_brief,
            "brief": brief,
            "role" : role,
            "brand_knowledge" : brand_knowledge,
            "copywriting_guidelines" : copywriting_guidelines
        }
    except Exception as e:
        raise RuntimeError(f"Failed to load project details: {str(e)}")

# Functions to load data files like brand knowledge, copywriting guidelines, reference examples and role
def load_data_file(project_name, folderName, fileName):
    path = os.path.join(os.getcwd(), "projects", project_name, "data", folderName, f"{fileName}.txt")
    if not os.path.exists(path):
        path = os.path.join(os.getcwd(), "projects", project_name, "data", folderName, fileName, f"{fileName}.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()

# Functions to write content in data files like brand knowledge, copywriting guidelines, reference examples and role
def update_data_file(content, project_name, folderName, fileName):
    path = os.path.join(os.getcwd(), "projects", project_name, "data", folderName, f"{fileName}.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

# Function to create a new template
def create_template(project_id, template_name):
    # Define the path for the templates based on the project ID
    templates_path = os.path.join(os.getcwd(), "projects", project_id, "content")
    
    # Create the directory if it does not exist
    if not os.path.exists(templates_path):
        os.makedirs(templates_path, exist_ok=True)
    

    new_template_path = os.path.join(templates_path, template_name)
    
    # Create the template directory and empty JSON files
    os.makedirs(os.path.join(new_template_path, 'content_data'), exist_ok=True)
    with open(os.path.join(new_template_path, 'content_data', 'content_structure.json'), 'w') as f:
        json.dump({}, f)
    with open(os.path.join(new_template_path, 'content_data', 'data_dict.json'), 'w') as f:
        json.dump({}, f)
    with open(os.path.join(new_template_path, 'content_data', 'filled_data.json'), 'w') as f:
        json.dump({}, f)

# Function to get all templates for a given project
def get_templates(project_id):
    # Define the path for the templates based on the project ID
    templates_path = os.path.join(os.getcwd(), "projects", project_id, "content")
    
    # Check if the directory exists
    if not os.path.exists(templates_path):
        return []

    # List all directories (templates) in the content path
    templates = []
    for template_name in os.listdir(templates_path):
        template_path = os.path.join(templates_path, template_name)
        if os.path.isdir(template_path):
            # Create a template entry
            templates.append({
                "templateName": template_name
            })

    return templates

# Function to get template details for a given project and template ID
def get_template_details(project_id, template_id):
    # Define the path for the template based on the project ID and template ID
    template_path = os.path.join(os.getcwd(), "projects", project_id, "content", template_id, "content_data")
    
    # Check if the directory exists
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template '{template_id}' not found for project '{project_id}'")
    
    # Load content structure
    content_structure = {}
    content_structure_file = os.path.join(template_path, 'content_structure.json')
    if os.path.exists(content_structure_file):
        with open(content_structure_file, 'r') as f:
            content_structure = json.load(f)
    
    # Load data
    data = {}
    data_file = os.path.join(template_path, 'data_dict.json')
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            data = json.load(f)

    # Return the template details
    return {
        "templateName": template_id,
        "contentStructure": content_structure,
        "data": data
    }

# Function to save content structure for a given project and template ID
def save_content_structure(project_id, template_id, content_structure):
    # Define the path for the content structure file based on the project ID and template ID
    content_data_path = os.path.join(os.getcwd(), "projects", project_id, "content", template_id, "content_data")
    
    # Create the directory if it does not exist
    os.makedirs(content_data_path, exist_ok=True)
    
    # Save the content structure to a JSON file
    content_structure_file = os.path.join(content_data_path, 'content_structure.json')
    with open(content_structure_file, 'w') as f:
        json.dump(content_structure, f, indent=4)

# Function to get content structure for a given project and template ID
def get_content_structure(project_id, template_id):
    # Define the path for the content structure file based on the project ID and template ID
    content_structure_file = os.path.join(os.getcwd(), "projects", project_id, "content", template_id, "content_data", "content_structure.json")
    
    # Check if the file exists
    if not os.path.exists(content_structure_file):
        raise FileNotFoundError(f"Content structure not found for template '{template_id}' in project '{project_id}'")
    
    # Load the content structure from the JSON file
    with open(content_structure_file, 'r') as f:
        content_structure = json.load(f)

    # Return the content structure
    return content_structure

# Function to save data for a given project and template ID
def save_data(project_id, template_id, data):
    # Define the path for the data file based on the project ID and template ID
    content_data_path = os.path.join(os.getcwd(), "projects", project_id, "content", template_id, "content_data")
    
    # Create the directory if it does not exist
    os.makedirs(content_data_path, exist_ok=True)
    
    # Save the data to a JSON file
    data_file = os.path.join(content_data_path, 'data_dict.json')
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=4)

# Function to get data for a given project and template ID
def get_data(project_id, template_id):
    # Define the path for the data file based on the project ID and template ID
    data_file = os.path.join(os.getcwd(), "projects", project_id, "content", template_id, "content_data", "data_dict.json")
    
    # Check if the file exists
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Data not found for template '{template_id}' in project '{project_id}'")
    
    # Load the data from the JSON file
    with open(data_file, 'r') as f:
        data = json.load(f)

    # Return the data
    return data


# Function to initiate content generation for a given project and template ID
def generate_content_function(project_id, template_id):
    # Define the path for the project and template
    template_path = os.path.join(os.getcwd(), "projects", project_id, "content", template_id)
    
    # Check if the template directory exists
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template '{template_id}' not found for project '{project_id}'")
    
    # Define the paths for saving content and prompts
    save_path = os.path.join(os.getcwd(), "projects", project_id, "content", template_id, "output")
    os.makedirs(save_path, exist_ok=True)
    prompt_folder = os.path.join(os.getcwd(), "projects", project_id, "prompts")
            
    # Debug information
    print("PROMPT FOLDER")
    print(prompt_folder)
    print("-------------------")
            
    # Choose the model for content generation
    model = choose_model("4-turbo")

    content_data=fill_hotel_data(get_content_structure(project_id, template_id), get_data(project_id, template_id))

    # Generate the content using the generate_content function
    generated_content = generate_content(
            content_data=content_data, 
            reference_examples=load_data_file(project_id, "reference_examples", "reference_examples"), 
            role=load_data_file(project_id, "role", "role"), 
            project=project_id, 
            prompt_folder=prompt_folder, 
            brand_knowledge=load_data_file(project_id, "brand_data", "brand_knowledge"), 
            cw_guidelines=load_data_file(project_id, "copywriting", "copywriting_guidelines"), 
            model=model,
            content_brief=load_data_file(project_id,"content","brief")  # Pass the brief here
        )    
    # Save Generated Content
    with open(os.path.join(save_path, 'generated_content.json'), 'w') as f:
        json.dump(generated_content, f, indent=4)
    print(f"Generating content for template '{template_id}'")
    return generated_content


#####################################
#                                   #
#             Endpoints             #
#                                   #
#####################################

# Endpoint pour crée un projet
@app.route('/api/project', methods=['POST'])
def create_project():
    # Récupérer les données du formulaire
    project_name = request.form.get('project_name')
    projectBrief = request.form.get('projectBrief')

    # Vérifier si les données sont présentes
    if project_name is None or projectBrief is None:
        return jsonify({"error": "Les champs 'project_name' et 'projectBrief' sont obligatoires."}), 400

    result = create_project_structure(project_name, projectBrief)
    
    return jsonify(result.__dict__)

# Endpoint pour recuperer la liste des projets
@app.route('/api/projects', methods=['GET'])
def get_projects():
    result = get_all_projects()
    
    # Convertir chaque objet Project en dictionnaire pour pouvoir serialisé en json
    projects_dict = [project.to_dict() for project in result]
    return jsonify(projects_dict)

# Endpoint pour recuperer les détails du projet
@app.route('/api/project/<project_id>', methods=['GET'])
def get_project_details(project_id):
    if not project_id:
        return jsonify({"error": "Project name is required"}), 400
    try:
        # Call the load_project_details function and get the details
        project_details = load_project_details(project_id)
        return jsonify({"message": "Project details loaded successfully", "data": project_details}), 200
    except RuntimeError as e:
        # Return an HTTP 400 error with the exception message
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Return a general HTTP 500 error for any unexpected issues
        return jsonify({"error": "An unexpected error occurred"}), 500

# Endpoint pour upload un fichier brand knowledge
@app.route('/api/project/<projectName>/brand-knowledge', methods=['POST'])
def load_brand_knowledge(projectName):
    # Vérifie si un fichier a été envoyé
    if 'files' not in request.files:
        return jsonify({"erreur": "pas de fichier dans la requête"}), 400
    
    files = request.files.getlist('files')

    # Vérifie si des fichiers ont été sélectionnés
    if len(files) == 0:
        return jsonify({"erreur": "aucun fichier selectionnés"}), 400
    
    try: 
        concatenated_docs = "\n\n---\n\n".join([file.read().decode("utf-8") for file in files]) # Boucle sur chaque fichier
        digested_content = extract_brand_knowledge(concatenated_docs)
        update_data_file(digested_content, projectName, "brand_data", "brand_knowledge")
    except Exception as e:
        return jsonify({"error": f"Failed to update brand knowledge: {str(e)}"}), 500
    
    return jsonify({"message": f"Brand knowledge uploaded successfully."}), 200

# Endpoint pour upload un fichier copywriting guidelines
@app.route('/api/project/<projectName>/copywriting-guidelines', methods=['POST'])
def load_copywriting_guidelines(projectName):
    # Vérifie si un fichier a été envoyé
    if 'files' not in request.files:
        return jsonify({"erreur": "pas de fichier dans la requête"}), 400
    
    files = request.files.getlist('files')

    # Vérifie si des fichiers ont été sélectionnés
    if len(files) == 0:
        return jsonify({"erreur": "aucun fichier selectionnés"}), 400
    
    try: 
        concatenated_docs = "\n\n---\n\n".join([file.read().decode("utf-8") for file in files]) # Boucle sur chaque fichier
        digested_content = extract_copywriting_guidelines(concatenated_docs)
        update_data_file(digested_content, projectName, "copywriting", "copywriting_guidelines")
    except Exception as e:
        return jsonify({"error": f"Failed to update copywriting guidelines: {str(e)}"}), 500

    return jsonify({"message": f"Copywriting guidelines uploaded successfully."}), 200

# Endpoint pour upload un fichier reference examples
@app.route('/api/project/<projectName>/reference-examples', methods=['POST'])
def load_reference_examples(projectName):
    # Vérifie si un fichier a été envoyé
    if 'files' not in request.files:
        return jsonify({"erreur": "pas de fichier dans la requête"}), 400
    
    files = request.files.getlist('files')

    # Vérifie si des fichiers ont été sélectionnés
    if len(files) == 0:
        return jsonify({"erreur": "aucun fichier selectionnés"}), 400
    
    try: 
        concatenated_docs = "\n\n---\n\nEXAMPLE:\n".join([file.read().decode("utf-8") for file in files]) # Boucle sur chaque fichier
        digested_content = "EXAMPLE:\n" + concatenated_docs
        update_data_file(digested_content, projectName, "reference_examples", "reference_examples")
    except Exception as e:
        return jsonify({"error": f"Failed to update reference examples: {str(e)}"}), 500

    return jsonify({"message": f"Reference examples uploaded successfully."}), 200

# Endpoint pour save les Copywriting Role
@app.route('/api/project/<projectName>/role', methods=['POST'])
def load_copywriting_role(projectName):
    data = request.get_json()
    role = data.get('role')
    
    # Vérifie si un fichier a été envoyé
    if not role:
        return jsonify({"erreur": "paramétre 'role' obligatoire"}), 400
    
    try: 
        update_data_file(role, projectName, "role", "role")
    except Exception as e:
        return jsonify({"error": f"Failed to update reference examples: {str(e)}"}), 500

    return jsonify({"message": f"Copywriting role saved successfully."}), 200

# API endpoint to create a new template
@app.route('/api/projects/<project_id>/templates', methods=['POST'])
def create_new_template(project_id):
    # Get the request data
    data = request.get_json()
    template_name = data.get('templateName')
    
    if not template_name:
        return jsonify({"error": "Template name is required"}), 400
    
    try:
        # Call the create_template function
        create_template(project_id, template_name)
        response = {
            "templateId": template_name,
            "message": "Template created successfully."
        }
        return jsonify(response), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create template: {str(e)}"}), 500

# API endpoint to get templates for a project
@app.route('/api/projects/<project_id>/templates', methods=['GET'])
def get_project_templates(project_id):
    try:
        # Call the get_templates function
        templates = get_templates(project_id)
        return jsonify(templates), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve templates: {str(e)}"}), 500

# API endpoint to get template details for a project
@app.route('/api/projects/<project_id>/templates/<template_id>', methods=['GET'])
def get_template_details_api(project_id, template_id):
    try:
        # Call the get_template_details function
        template_details = get_template_details(project_id, template_id)
        return jsonify(template_details), 200
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve template details: {str(e)}"}), 500

# API endpoint to save content structure for a template
@app.route('/api/projects/<project_id>/templates/<template_id>/structure', methods=['POST'])
def save_content_structure_api(project_id, template_id):
    try:
        # Get the request data
        data = request.get_json()
        content_structure = data.get('contentStructure')
        
        if content_structure is None:
            return jsonify({"error": "Content structure is required"}), 400
        
        # Call the save_content_structure function
        save_content_structure(project_id, template_id, content_structure)
        
        # Return a success response
        return jsonify({"message": "Content structure saved successfully."}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to save content structure: {str(e)}"}), 500

# API endpoint to get content structure for a template
@app.route('/api/projects/<project_id>/templates/<template_id>/structure', methods=['GET'])
def get_content_structure_api(project_id, template_id):
    try:
        # Call the get_content_structure function
        content_structure = get_content_structure(project_id, template_id)
        return jsonify({"contentStructure": content_structure}), 200
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve content structure: {str(e)}"}), 500

# API endpoint to save data for a template
@app.route('/api/projects/<project_id>/templates/<template_id>/data', methods=['POST'])
def save_data_api(project_id, template_id):
    try:
        # Get the request data
        data = request.get_json()
        data_object = data.get('data')
        
        if data_object is None:
            return jsonify({"error": "Data object is required"}), 400
        
        # Call the save_data function
        save_data(project_id, template_id, data_object)
        
        # Return a success response
        return jsonify({"message": "Data saved successfully."}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to save data: {str(e)}"}), 500

# API endpoint to get data for a template
@app.route('/api/projects/<project_id>/templates/<template_id>/data', methods=['GET'])
def get_data_api(project_id, template_id):
    try:
        # Call the get_data function
        data = get_data(project_id, template_id)
        return jsonify({"data": data}), 200
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve data: {str(e)}"}), 500


# API endpoint to initiate content generation
@app.route('/api/projects/<project_id>/templates/<template_id>/generate', methods=['POST'])
def generate_content_api(project_id, template_id):
    try:
        
        # Call the generate_content function
        generated_content=generate_content_function(project_id, template_id)
        
        # Return a success response
        return jsonify({"message": "Content generation initiated.", "content": generated_content}), 200
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to initiate content generation: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080,debug=True)
