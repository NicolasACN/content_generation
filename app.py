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

app = Flask(__name__)

# Function to create project directory structure
def create_project_structure(project_name, project_brief):
    result = {
    "projectName": "",
    "message": "",
    "success": False
    }
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
        result["projectName"] = project_name
        result["message"] = (f"Project '{project_name}' created successfully!")
        result["success"] = True
    except Exception as e:
        result["message"] = (f"Error created project '{project_name}' : {e}")
    finally:
        return result

# Function to create project directory structure
def get_all_projects():
    result = {
    "projectName": "",
    "message": "",
    "success": False
    }
    project_dir = os.path.join(os.getcwd(), "projects")
    #project_path = os.path.join(os.getcwd(), "projects", project_name)

    if os.path.exists(project_dir):
        projects = [d for d in os.listdir(project_dir) if os.path.isdir(os.path.join(project_dir, d))]
    return projects

# Endpoint pour crée un projet
@app.route('/api/project', methods=['POST'])
def create_project():
    # Récupérer les données du formulaire
    project_name = request.form.get('project_name')
    projectBrief = request.form.get('projectBrief')

    # Vérifier si les données sont présentes
    if project_name is None or projectBrief is None:
        return jsonify({"error": "Les champs 'nom' et 'age' sont obligatoires."}), 400

    result = create_project_structure(project_name, projectBrief)
    return jsonify(result)

# Endpoint pour recuperer la liste des projets
@app.route('/api/projects', methods=['GET'])
def get_projects():
    result = get_all_projects()
    return jsonify(result)

# Endpoint pour recuperer les détails du projet
@app.route('/api/project/<string:projectId>', methods=['GET'])
def get_project_detail():
    result = load_project_details(projectId)
    return jsonify(result)

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
