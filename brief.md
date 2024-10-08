# Project Brief for Developers

## Detailed Explanation of the Current Code

The provided code is a **Streamlit** application written in Python, designed for content generation using generative AI. The application allows users to create and manage projects, upload and manage brand-related data, define content structures, and generate content based on the provided data and structures.

Here's a breakdown of the application's functionality:

### 1. Imports and Initial Setup

- **Imports:**
  - `streamlit` for the web interface.
  - `json`, `os`, `shutil` for file and data handling.
  - Custom functions from local modules (not fully provided):
    - `make_bloc_structure`, `fill_hotel_data` from `functions.old.data_processing`.
    - `choose_model`, `dict_to_markdown`, `extract_brand_knowledge`, `extract_copywriting_guidelines` from `functions.utils`.
    - `generate_content` from `functions.generation`.

- **Session State Initialization:**
  - The application uses `st.session_state` to maintain state across user interactions.
  - Variables like `project_name`, `brand_knowledge`, `copywriting_guidelines`, etc., are initialized if not already present.

### 2. Application Structure

The application is organized into three main tabs:

#### Tab 1: Project Setup

- **Create New Project:**
  - Users can create a new project by providing a project name and brief.
  - Upon creation, a directory structure is set up in the `projects` folder with subfolders for data, prompts, and content.

- **Load Existing Project:**
  - Users can select an existing project to load.
  - The application reads the project details and loads brand knowledge, copywriting guidelines, reference examples, and roles into the session state.

#### Tab 2: Data Upload

- **Brand Knowledge:**
  - Users can upload brand documents (text files).
  - The application concatenates these documents and extracts key brand knowledge using `extract_brand_knowledge`.
  - Users can also import brand knowledge from another project.

- **Copywriting Guidelines:**
  - Similar to brand knowledge, users can upload documents containing copywriting guidelines.
  - Extraction is done via `extract_copywriting_guidelines`.
  - Importing from another project is also possible.

- **Reference Examples:**
  - Users can upload reference examples, which are concatenated and formatted.

- **Copywriting Role:**
  - Users define the writer's role, which influences the content generation process.
  - Roles can also be imported from other projects.

- **Debug Sections:**
  - For developers or advanced users to view the current state of the data being processed.

#### Tab 3: Content Generation

- **Select or Create Content Template:**
  - Users can select an existing content template or create a new one.
  - Templates contain the content structure and associated data.

- **Content Brief:**
  - Users provide a brief for the content they wish to generate.

- **Create Content Structure:**
  - Users define a hierarchical content structure:
    - **Pages**
    - **Sections**
    - **Elements** (with details like character limits, guidelines, reference content, and associated data)
  - The structure is saved as a JSON file.

- **Data Factory:**
  - Users can input or import data required for content generation.
  - Data is linked to elements in the content structure.

- **Generate Content:**
  - The application uses the `generate_content` function to produce content based on the structure, data, and guidelines.
  - Generated content is displayed and can be saved.

### 3. Supporting Functions

- **Project Management Functions:**
  - `create_project_structure` sets up the directory structure for a new project.
  - `load_project_details` loads existing project data into the session state.

- **Data Extraction Functions:**
  - `create_brand_knowledge` and `create_copywriting_guidelines` process uploaded documents and extract relevant information.

- **Content Structure Functions:**
  - Functions to add pages, sections, and elements to the content structure.
  - `make_bloc_structure` generates the block structure string for content generation.

- **Content Generation Functions:**
  - `generate_content` orchestrates the content creation process using the model selected by `choose_model`.

- **Utilities:**
  - `dict_to_markdown` formats the generated content for display in the application.

---

## Application Architecture

### Overview

The application will be refactored into a web application with a **Vue.js frontend** and a **Node.js backend**, while retaining the existing Python code for content generation as a separate service. Data storage will be handled using local folders and JSON files, similar to the current Python application.

### Components

1. **Frontend**: Vue.js Application
   - Handles the user interface and user interactions.
   - Communicates with the backend via RESTful APIs.
   - Provides a responsive and user-friendly experience.

2. **Backend**: Node.js with Express.js
   - Acts as an API server for the frontend.
   - Manages project data, file uploads, and storage.
   - Communicates with the Python service for content generation.
   - Handles data storage using local folders and JSON files.

3. **Content Generation Service**: Python (Flask or FastAPI)
   - Contains the existing Python code for content generation.
   - Exposes content generation functions via RESTful APIs.
   - Runs as a separate microservice.

4. **Data Storage**: Local Folders and JSON Files
   - Project data, content structures, and generated content are stored as JSON files in a structured directory hierarchy.
   - Facilitates rapid development and easy debugging.

5. **Containerization**: Docker and Docker Compose
   - Each component runs in its own Docker container.
   - Docker Compose orchestrates the multi-container application.
   - Ensures consistency across different development environments.

### Data Flow

1. **User Interactions**:
   - The user interacts with the Vue.js frontend, performing actions like creating projects, uploading files, and initiating content generation.

2. **Frontend to Backend Communication**:
   - The frontend sends HTTP requests to the Node.js backend via defined API endpoints.
   - Data such as form inputs and uploaded files are transmitted.

3. **Backend Processing**:
   - The backend handles requests, processes data, and performs file operations.
   - Stores data as JSON files in the appropriate project directories.
   - When content generation is requested, the backend communicates with the Python service.

4. **Backend to Python Service Communication**:
   - The Node.js backend sends HTTP requests to the Python content generation service.
   - Payload includes all necessary data for content generation (e.g., content structures, data dictionaries, guidelines).

5. **Content Generation**:
   - The Python service processes the data and generates content using the existing codebase.
   - Returns the generated content to the backend as a JSON response.

6. **Backend to Frontend Response**:
   - The backend receives the generated content and sends it back to the frontend.
   - The frontend displays the content to the user.

### Key Interactions

- **File Uploads**:
  - Handled by the frontend using file input components.
  - Files are sent to the backend via multipart/form-data requests.
  - The backend saves files in the appropriate directories.

- **Data Storage**:
  - The backend reads from and writes to JSON files for storing project data.
  - Ensures quick read/write operations without the overhead of a database.

- **Service Communication**:
  - The backend and Python service communicate over HTTP using RESTful APIs.
  - Internal networking in Docker allows secure and efficient communication.

### Considerations

- **Feasibility Within Timeline**:
  - Using local folders and JSON files for data storage is feasible within the 7-day timeline.
  - It simplifies data management and reduces development time.

- **Scalability**:
  - The modular architecture allows for individual components to be scaled independently.
  - While JSON files are suitable for the MVP, future enhancements can include replacing file-based storage with a database.

- **Security**:
  - For the MVP, authentication is not implemented but can be added later.
  - Internal Docker networking reduces exposure of internal APIs.

- **Performance**:
  - Using JSON files minimizes setup time but may not be optimal for large datasets.
  - Content generation service runs separately to avoid blocking the backend.

- **Dockerization**:
  - Docker Compose configuration defines services, networks, and volumes.
  - Volumes are used to persist data across container restarts.

### Technology Stack Summary

- **Frontend**:
  - Vue.js 3, Vue Router, Vuex/Pinia, Axios, Vuetify/Element UI.

- **Backend**:
  - Node.js, Express.js, Multer (file uploads), Axios/node-fetch (HTTP requests), File System for data storage.

- **Content Generation Service**:
  - Python 3.x, Flask/FastAPI, Existing Python modules.

- **Data Storage**:
  - Local folders and JSON files.

- **Containerization**:
  - Docker, Docker Compose.

- **Development Tools**:
  - Git for version control, NPM/Yarn for package management, ESLint/Prettier for code formatting.

---

## Detailed Brief and How-To for Developers

The goal is to transition this Streamlit application into a web application with a **Vue.js frontend** and a **Node.js backend**, using local folders and JSON files for data storage, and dockerized for local deployment. The development team consists of one frontend developer and two backend developers. The application needs to be ready for a client demo in **7 days**.

### Overall Architecture

- **Frontend:** Vue.js (JavaScript framework for building user interfaces)
- **Backend:** Node.js with Express.js (web framework for Node.js)
- **Data Storage:** Local folders and JSON files
- **Containerization:** Docker for containerization to ensure the application runs smoothly on any environment
- **File Storage:** Store files in structured directories within the Docker containers

### Development Plan

#### Day 1-2: Planning and Setup

- **Frontend Developer:**
  - Set up the Vue.js project using Vue CLI or Vite.
  - Define the project structure and install necessary dependencies (e.g., Vue Router, Vuex for state management).

- **Backend Developers:**
  - Set up the Node.js project with Express.js.
  - Define API endpoints based on the functionality required.
  - Decide on how to handle file uploads and storage.
  - Set up Dockerfile and docker-compose configuration for both frontend and backend.

#### Day 3-5: Feature Development

- **Frontend Tasks**:

  1. **Project Setup Page:**
     - **Create New Project:** Form to input project name and brief.
     - **Load Existing Project:** Dropdown to select existing projects.
     - **Actions:**
       - Create project via API.
       - Load project details via API.

  2. **Data Upload Page:**
     - **Brand Knowledge Upload:**
       - File upload component.
       - Display extracted brand knowledge.
     - **Copywriting Guidelines Upload:**
       - Similar to brand knowledge.
     - **Reference Examples Upload:**
       - File upload and display.
     - **Copywriting Role:**
       - Text area for input.
     - **Import from Another Project:**
       - Option to import data from existing projects via API.
     - **Actions:**
       - Upload files to backend.
       - Fetch extracted data from backend.

  3. **Content Generation Page:**
     - **Content Template Selection:**
       - Dropdown to select or create a new template.
     - **Content Brief:**
       - Text area for input.
     - **Content Structure Creation:**
       - Interactive UI to add pages, sections, and elements.
     - **Data Factory:**
       - Forms to input data values and descriptions.
     - **Generate Content:**
       - Button to trigger content generation.
       - Display generated content.
     - **Actions:**
       - Send structure and data to backend.
       - Fetch generated content from backend.

- **Backend Tasks**:

  1. **File Handling and Storage:**
     - Decide on the directory structure for storing projects, data, and content.
     - Ensure that file paths are correctly managed within the Docker container.

  2. **API Endpoints**:
     - **Project Management:**
       - `POST /projects`: Create a new project.
       - `GET /projects`: List all projects.
       - `GET /projects/:id`: Get project details.
     - **Data Upload:**
       - `POST /projects/:id/brand-knowledge`: Upload brand knowledge files.
       - `POST /projects/:id/copywriting-guidelines`: Upload copywriting guidelines.
       - `POST /projects/:id/reference-examples`: Upload reference examples.
       - `POST /projects/:id/role`: Save copywriting role.
     - **Content Templates:**
       - `POST /projects/:id/templates`: Create a new content template.
       - `GET /projects/:id/templates`: Get templates.
       - `GET /projects/:id/templates/:templateId`: Get template details.
     - **Content Structure:**
       - `POST /projects/:id/templates/:templateId/structure`: Save content structure.
       - `GET /projects/:id/templates/:templateId/structure`: Get content structure.
     - **Data Factory:**
       - `POST /projects/:id/templates/:templateId/data`: Save data.
       - `GET /projects/:id/templates/:templateId/data`: Get data.
     - **Content Generation:**
       - `POST /projects/:id/templates/:templateId/generate`: Trigger content generation.
       - `GET /projects/:id/templates/:templateId/generated-content`: Get generated content.

  3. **File Handling:**
     - Use middleware like `multer` for handling file uploads.
     - Ensure files are stored in a directory structure similar to the Python app.

  4. **Content Generation Logic:**
     - Use **Option 2**: Keep the Python content generation code and expose it via a REST API using Flask or FastAPI.
     - The Node.js backend communicates with the Python service for content generation.

  5. **Data Storage:**
     - Use JSON files for storing data.
     - Read from and write to these files as needed.

#### Day 6: Integration and Testing

- **Integration:**
  - Connect frontend components with backend APIs.
  - Ensure that all API endpoints are working as expected.
  - Handle any CORS issues between frontend and backend.

- **Testing:**
  - Perform end-to-end testing of the application.
  - Fix any bugs or issues that arise.

#### Day 7: Finalization and Dockerization

- **Dockerization:**
  - Finalize Docker configurations for all services.
  - Ensure that all services run smoothly in Docker containers.
  - Write a `docker-compose.yml` file to orchestrate services.

- **Documentation:**
  - Prepare necessary documentation for the demo.
  - Write instructions on how to run the application locally using Docker.

- **Demo Preparation:**
  - Ensure that sample data is loaded.
  - Run through the demo flow multiple times to ensure smooth operation.

### Technical Choices and Recommendations

- **Frontend:**
  - Use Vue.js 3 with Composition API for better state management.
  - Use Vuetify or Element UI for a consistent and professional UI.
  - Implement state management with Vuex or Pinia (if necessary).

- **Backend:**
  - Use Express.js for routing and middleware.
  - Use `multer` for file uploads.
  - Use the file system and JSON files for data storage.
  - Communicate with the Python content generation service via REST API calls.

- **Content Generation Service:**
  - Expose the content generation functions via a Flask or FastAPI app.
  - Dockerize this service separately.
  - Ensure that the Node.js backend can communicate with this service.

- **Containerization:**
  - Use a multi-container setup with Docker Compose.
  - Define services for the frontend, backend, and Python service.

- **File Storage:**
  - Organize files in a structured way within the project directory.
  - Map volumes in Docker to persist data across container restarts.

- **Communication Between Services:**
  - Use internal Docker networking to allow services to communicate.
  - Ensure that API endpoints are correctly routed.

---

## How-To Guide for Developers

### Setting Up the Development Environment

1. **Clone the Repository:**
   - Set up a Git repository and ensure all developers have access.

2. **Install Dependencies:**
   - For frontend: Node.js, npm/yarn, Vue CLI.
   - For backend: Node.js, Express.js, `multer`, `axios` (for making HTTP requests to the Python service).
   - For Python service: Python 3.x, Flask or FastAPI, required Python packages.

3. **Set Up Docker:**
   - Install Docker and Docker Compose.
   - Create Dockerfiles for each service.

### Implementing the Frontend

1. **Project Setup:**
   - Initialize a Vue.js project.
   - Install UI libraries and set up the basic layout.

2. **Routing:**
   - Set up Vue Router to navigate between pages (Project Setup, Data Upload, Content Generation).

3. **Components:**
   - Create reusable components for forms, file uploads, data display, etc.

4. **State Management:**
   - Use Vuex or Pinia to manage the application state if necessary.

5. **API Integration:**
   - Use Axios for making API calls to the backend.
   - Handle responses and update the UI accordingly.

6. **File Uploads:**
   - Implement file upload components that send files to the backend.

### Implementing the Backend

1. **API Endpoints:**
   - Define the API routes as per the functionality.
   - Implement controllers for handling each route.

2. **File Handling:**
   - Use `multer` to handle file uploads.
   - Save files in the appropriate directories.

3. **Data Management:**
   - Read and write JSON files to store project data.
   - Ensure data consistency and handle file read/write operations properly.

4. **Communication with Python Service:**
   - Use Axios or `node-fetch` to make HTTP requests to the Python service.
   - Handle the responses and send them back to the frontend.

5. **Error Handling:**
   - Implement proper error handling and send meaningful error messages to the frontend.

### Implementing the Python Content Generation Service

1. **Set Up Flask/FastAPI App:**
   - Create endpoints that correspond to the content generation functions.
   - Example endpoint: `POST /generate-content`.

2. **Modify Existing Functions:**
   - Adapt the existing Python functions to work within the web framework.
   - Ensure that they accept JSON payloads and return JSON responses.

3. **Testing:**
   - Test the endpoints independently before integrating with the backend.

### Dockerization

1. **Create Dockerfiles:**
   - One for the frontend, one for the backend, and one for the Python service.
   - Ensure that each Dockerfile sets up the environment correctly.

2. **Docker Compose:**
   - Write a `docker-compose.yml` file that defines all services.
   - Map necessary ports and volumes.

3. **Environment Variables:**
   - Use a `.env` file to store environment variables.
   - Ensure that sensitive data is not hardcoded.

4. **Building and Running Containers:**
   - Use `docker-compose build` and `docker-compose up` to build and run the services.
   - Test the application end-to-end within Docker.

### Testing and Debugging

1. **Unit Tests:**
   - Write unit tests for critical functions in the backend and Python service.

2. **Integration Tests:**
   - Test the communication between frontend, backend, and Python service.

3. **Debugging:**
   - Use logging to track down issues.
   - Check container logs for errors.

### Final Preparations

1. **Documentation:**
   - Write README files with instructions on how to set up and run the application.
   - Document any assumptions or limitations.

2. **Demo Preparation:**
   - Ensure that sample data is loaded.
   - Run through the demo flow multiple times to ensure smooth operation.

---

## API Documentation

Below is an outline of the API endpoints, including the expected payloads and responses.

### Base URL

- **Node.js Backend:** `http://localhost:3000/api`
- **Python Content Generation Service:** `http://localhost:5000`

### Authentication

- For this MVP, authentication is not implemented to save development time.

### API Endpoints

#### Projects

- **Create a New Project**

  - **Endpoint:** `POST /api/projects`
  - **Payload:**

    ```json
    {
      "projectName": "string",
      "projectBrief": "string"
    }
    ```

  - **Response:**

    ```json
    {
      "projectId": "string",
      "message": "Project created successfully."
    }
    ```

- **Get All Projects**

  - **Endpoint:** `GET /api/projects`
  - **Response:**

    ```json
    [
      {
        "projectId": "string",
        "projectName": "string",
        "projectBrief": "string"
      }
    ]
    ```

- **Get Project Details**

  - **Endpoint:** `GET /api/projects/:projectId`
  - **Response:**

    ```json
    {
      "projectId": "string",
      "projectName": "string",
      "projectBrief": "string",
      "brandKnowledge": "string",
      "copywritingGuidelines": "string",
      "referenceExamples": "string",
      "role": "string",
      "templates": [/* list of templates */]
    }
    ```

#### Data Upload

- **Upload Brand Knowledge**

  - **Endpoint:** `POST /api/projects/:projectId/brand-knowledge`
  - **Payload:** Form Data with files.
  - **Response:**

    ```json
    {
      "message": "Brand knowledge uploaded successfully."
    }
    ```

- **Upload Copywriting Guidelines**

  - **Endpoint:** `POST /api/projects/:projectId/copywriting-guidelines`
  - **Payload:** Form Data with files.
  - **Response:**

    ```json
    {
      "message": "Copywriting guidelines uploaded successfully."
    }
    ```

- **Upload Reference Examples**

  - **Endpoint:** `POST /api/projects/:projectId/reference-examples`
  - **Payload:** Form Data with files.
  - **Response:**

    ```json
    {
      "message": "Reference examples uploaded successfully."
    }
    ```

- **Save Copywriting Role**

  - **Endpoint:** `POST /api/projects/:projectId/role`
  - **Payload:**

    ```json
    {
      "role": "string"
    }
    ```

  - **Response:**

    ```json
    {
      "message": "Copywriting role saved successfully."
    }
    ```

#### Content Templates

- **Create a New Template**

  - **Endpoint:** `POST /api/projects/:projectId/templates`
  - **Payload:**

    ```json
    {
      "templateName": "string"
    }
    ```

  - **Response:**

    ```json
    {
      "templateId": "string",
      "message": "Template created successfully."
    }
    ```

- **Get Templates**

  - **Endpoint:** `GET /api/projects/:projectId/templates`
  - **Response:**

    ```json
    [
      {
        "templateId": "string",
        "templateName": "string"
      }
    ]
    ```

- **Get Template Details**

  - **Endpoint:** `GET /api/projects/:projectId/templates/:templateId`
  - **Response:**

    ```json
    {
      "templateId": "string",
      "templateName": "string",
      "contentStructure": {/* content structure object */},
      "data": {/* data object */}
    }
    ```

#### Content Structure

- **Save Content Structure**

  - **Endpoint:** `POST /api/projects/:projectId/templates/:templateId/structure`
  - **Payload:**

    ```json
    {
      "contentStructure": {/* content structure object */}
    }
    ```

  - **Response:**

    ```json
    {
      "message": "Content structure saved successfully."
    }
    ```

- **Get Content Structure**

  - **Endpoint:** `GET /api/projects/:projectId/templates/:templateId/structure`
  - **Response:**

    ```json
    {
      "contentStructure": {/* content structure object */}
    }
    ```

#### Data Factory

- **Save Data**

  - **Endpoint:** `POST /api/projects/:projectId/templates/:templateId/data`
  - **Payload:**

    ```json
    {
      "data": {/* data object */}
    }
    ```

  - **Response:**

    ```json
    {
      "message": "Data saved successfully."
    }
    ```

- **Get Data**

  - **Endpoint:** `GET /api/projects/:projectId/templates/:templateId/data`
  - **Response:**

    ```json
    {
      "data": {/* data object */}
    }
    ```

#### Content Generation

- **Generate Content**

  - **Endpoint:** `POST /api/projects/:projectId/templates/:templateId/generate`
  - **Payload:**

    ```json
    {
      "brief": "string" // Optional, if brief is needed
    }
    ```

  - **Response:**

    ```json
    {
      "message": "Content generation initiated."
    }
    ```

- **Get Generated Content**

  - **Endpoint:** `GET /api/projects/:projectId/templates/:templateId/generated-content`
  - **Response:**

    ```json
    {
      "generatedContent": {/* generated content object */}
    }
    ```

### Python Content Generation Service API

- **Generate Content**

  - **Endpoint:** `POST /generate-content`
  - **Payload:**

    ```json
    {
      "contentData": {/* filled data object */},
      "referenceExamples": "string",
      "role": "string",
      "project": "string",
      "brandKnowledge": "string",
      "copywritingGuidelines": "string",
      "contentBrief": "string"
    }
    ```

  - **Response:**

    ```json
    {
      "generatedContent": {/* generated content object */}
    }
    ```

### Example Payloads and Responses

**Save Content Structure Payload Example:**

```json
{
  "contentStructure": {
    "HomePage": {
      "HeroSection": {
        "bloc_guidelines": {
          "Title": {
            "nb_characters": "50",
            "content_guidelines": "Catchy headline",
            "reference_content": "Welcome to Our Hotel"
          },
          "Subtitle": {
            "nb_characters": "150",
            "content_guidelines": "Brief description",
            "reference_content": "Experience luxury like never before."
          }
        },
        "bloc_data": {
          "hotel_name": {
            "value": "Grand Plaza",
            "description": "Name of the hotel"
          }
        }
      }
    }
  }
}
