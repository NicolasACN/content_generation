
# 📄 Content Generation App

Welcome to the Content Generation App! This document provides an overview of the app's folder structure, its main functions, and a detailed explanation of each tab's functionality. This app is designed to streamline and enhance your content creation process.

---

## 📁 Folder Structure

Here's an overview of the folder structure:

```
content_generation/
├── functions/
│   ├── __pycache__/
│   ├── old/
│   ├── __init__.py
│   └── utils.py
├── images/
│   └── logo.svg
├── notebooks/
├── old/
├── projects/
│   └── my_new_project/
│       ├── content/
│           ├── template_0/
│               └── content_data/
│                   ├── content_structure.json
│                   ├── data_dict.json
│                   └── filled_data.json
│           ├── template_0_copy/
│           ├── template_1/
│           ├── template_2/
│           └── template_3/
│       └── data/
│           ├── brand_data/
│           ├── persona/
│           ├── platform_specs/
│           ├── product_data/
│           ├── project_info/
│           └── reference_examples/
├── reference/
├── .env
├── .gitignore
├── content_generation_app.py
├── README.md
└── requirements.txt
```

### 📂 Key Directories

- **functions/**: Contains the main utility functions and old versions.
- **images/**: Contains image assets like the app logo.
- **projects/**: Where project-specific data and templates are stored.
  - **my_new_project/**: Example project folder.
    - **content/**: Contains content templates.
      - **template_X/**: Different content templates with their data.
        - **content_data/**: Stores `content_structure.json`, `data_dict.json`, and `filled_data.json`.
    - **data/**: Contains various data related to the project.
      - **brand_data/**: Information about the brand.
      - **persona/**: Information about the target personas.
      - **platform_specs/**: Platform-specific specifications.
      - **product_data/**: Information about the products.
      - **project_info/**: Project-specific information like project name and brief.
      - **reference_examples/**: Examples to guide content creation.
- **reference/**: Stores reference materials.
- **.env**: Environment configuration file.
- **.gitignore**: Specifies files to ignore in version control.
- **content_generation_app.py**: The main app script.
- **README.md**: This documentation.
- **requirements.txt**: Lists dependencies required to run the app.

---

## 🚀 Content Generation Process

The Content Generation App helps you create structured content using predefined templates and data. Here's an overview of the process:

1. **Project Setup**: Create a new project or load an existing one.
2. **Data Upload**: Upload brand knowledge, copywriting guidelines, and reference examples.
3. **Content Generation**:
   - Select or create a content template.
   - Define the structure of the content.
   - Input and save relevant data.
   - Generate content based on the defined structure and data.
   - Debug and refine the content as needed.

---

## 🖥️ How To Use The App ?

### 1. Project Setup

In this tab, you can either create a new project or load an existing one. 

- **Create New Project**: Enter the project name and brief to set up a new project.
- **Select Existing Project**: Choose from a list of existing projects and load the selected one.

### 2. Data Upload

Upload various files that provide the foundational knowledge and guidelines for your content creation:

- **Brand Knowledge**: Upload text files that provide information about the brand.
- **Copywriting Guidelines**: Upload text files with guidelines for writing.
- **Reference Examples**: Upload text files with examples to use as references.

### 3. Content Generation

This tab allows you to manage content templates, create and structure content, input data, and generate the final content.

- **Select or Create Content Template**: Choose an existing template or create a new one.
- **Create Content Structure**: Define the structure of your content by adding pages, sections, and elements.
- **Data Factory**: Import existing data and input values and descriptions for each data element.
- **Generate Content**: Use the filled data to generate content and save it.
- **Debug**: View the current structure and data dictionaries for debugging purposes.

---


## How To Use The App in API mode ?

### 1. Project Setup

- Get the sources and install the app as indicated above.

- Check that you are on the git branch "poc_api" which contains the modifications to make the app work in API mode

- In a command prompt, enter the command above which creates an alias to launch the app on the APP.py file: 
set FLASK_APP=app.py

### 2. Launch Project

- still in command prompt execute the command to place yourself in the content_generation directory: 
cd C:\Projects\moliere\content_generation

- Execute the flask run command to start the app

Happy Content Creating! ✍️

*This app is a JJJAM'N Creation.*
