# modele objet d'un projet
class Project:
    def __init__(self):
        self.name = ""
        self.brief = ""
    
    def to_dict(self):
        return {
            "projectName": self.name,
            "projectBrief": self.brief
        }