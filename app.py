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
from models.requestModels import CreateProjectResponse

app = Flask(__name__)

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
    project = {
    "projectName": "",
    "projectBrief": "",
    }
    projects_list = []
    projects_dir = os.path.join(os.getcwd(), "projects")

    if os.path.exists(project_dir):
        projects = [d for d in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, d))]
        for project in projects:
            project_info = ProjectInfo(
                name=project.name,
                brief=project.brief  
            )
            projects_list.append(project_info)
    return projects

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
    return jsonify(result)


# Placeholder for the load_project_details function
def load_project_details(project_name: str):
    try:
        project_path = os.path.join(os.getcwd(), "projects", project_name)
        if not os.path.exists(project_path):
            raise RuntimeError(f"Failed to load project details: {project_name} n'existe pas")
        project_info_path = os.path.join(project_path, "data", "project_info")

        with open(os.path.join(project_info_path, "project_brief.txt"), "r") as f:
            project_brief = f.read()
        
        # Load brand knowledge, copywriting guidelines, reference examples, and role
        brand_knowledge=load_brand_knowledge(project_name)
        copywriting_guidelines=load_copywriting_guidelines(project_name)
        reference_examples=load_reference_examples(project_name)
        role=load_role(project_name)
        
        # Load brief
        brief_path = os.path.join(project_path, "data", "content", "brief", "brief.txt")
        if os.path.exists(brief_path):
            with open(brief_path, "r") as f:
                brief = f.read()
    
        # Simulated logic for loading project details, replace with actual logic
        # For example, load data from a database or file based on the project name
        return {
            "project_name": project_name,
            "project_brief": project_brief,
            "brief": brief,
            "role" : role,
            "brand_knowledge" : brand_knowledge,
            "copywriting_guidelines" : copywriting_guidelines,
            "brand_knowledge" : brand_knowledge
        }
    except Exception as e:
        raise RuntimeError(f"Failed to load project details: {str(e)}")

# Endpoint pour recuperer les détails du projet
@app.route('/api/project', methods=['GET'])
def get_project_details():
    project_name = request.args.get('project_name')
    if not project_name:
        return jsonify({"error": "Project name is required"}), 400
    try:
        # Call the load_project_details function and get the details
        project_details = load_project_details(project_name)
        return jsonify({"message": "Project details loaded successfully", "data": project_details}), 200
    except RuntimeError as e:
        # Return an HTTP 400 error with the exception message
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Return a general HTTP 500 error for any unexpected issues
        return jsonify({"error": "An unexpected error occurred"}), 500

# Functions to load brand knowledge, copywriting guidelines, and reference examples
def load_brand_knowledge(project_name):
    brand_knowledge_path = os.path.join(os.getcwd(), "projects", project_name, "data", "brand_data", "brand_knowledge.txt")
    if os.path.exists(brand_knowledge_path):
        with open(brand_knowledge_path, "r") as f:
            return f.read()

def load_role(project_name):
    role_path = os.path.join(os.getcwd(), "projects", project_name, "data", "role", "role.txt")
    if os.path.exists(role_path):
        with open(role_path, "r") as f:
            return f.read()
        
def load_copywriting_guidelines(project_name):
    copywriting_guidelines_path = os.path.join(os.getcwd(), "projects", project_name, "data", "copywriting", "copywriting_guidelines.txt")
    if os.path.exists(copywriting_guidelines_path):
        with open(copywriting_guidelines_path, "r") as f:
            return f.read()
        
def load_reference_examples(project_name):
    reference_examples_path = os.path.join(os.getcwd(), "projects", project_name, "data", "reference_examples", "reference_examples.txt")
    if os.path.exists(reference_examples_path):
        with open(reference_examples_path, "r") as f:
            return f.read()

# # Endpoint pour upload un fichier brand knowledge
# @app.route('/api/project/<string:projectId>/brand-knowledge', methods=['POST'])
# def get_project_detail():
#     result = load_project_details(projectId)
#     return jsonify(result)

# # Endpoint pour upload un fichier copywriting guidelines
# @app.route('/api/project/<string:projectId>/copywriting-guidelines', methods=['POST'])
# def get_project_detail():
#     result = load_project_details(projectId)
#     return jsonify(result)

# # Endpoint pour upload un fichier reference examples
# @app.route('/api/project/<string:projectId>/reference-examples', methods=['POST'])
# def get_project_detail():
#     result = load_project_details(projectId)
#     return jsonify(result)

# # Endpoint pour save les Copywriting Role
# @app.route('/api/project/<string:projectId>/role', methods=['POST'])
# def get_project_detail():
#     result = load_project_details(projectId)
#     return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
