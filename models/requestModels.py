# modele objet de la reponse api a la creation d'un projet
class CreateProjectResponse:
    def __init__(self):
        self.projectName = "" 
        self.message = ""
        self.success = False