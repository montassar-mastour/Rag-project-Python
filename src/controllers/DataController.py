from .BaseController import BaseControllers
from fastapi import UploadFile
from models import ResponseMessage
from .ProjectController import ProjectController
import os, re
class DataController(BaseControllers):
    
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576


    def validate_upload_file(self,file:UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPE:
            return False, ResponseMessage.FILE_Type_NOT_SUPPORTED.value
        
        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseMessage.FILE_Size_TOO_BIG.value
        return True, ResponseMessage.UPLOAD_WITH_SUCCES.value
    
    def generate_unique_filepath(self, orig_filename: str,project_id: str):
        random_key=self.generate_random_string()

        project_path = ProjectController().get_project_path(project_id=project_id)

        clean_file_path=self.get_clean_filename(org_filename=orig_filename)

        new_file_path = os.path.join(
            project_path,
            random_key+"_"+clean_file_path
        )

        while os.path.exists(new_file_path):
            random_key=self.generate_random_string()
            new_file_path = os.path.join(
            project_path,
            random_key+"_"+clean_file_path
        )
        
        return new_file_path,random_key+"_"+clean_file_path




    def get_clean_filename(self,org_filename: str):
        cleaned_filename= re.sub(r'[^\w.]','', org_filename.strip())
        cleaned_filename = cleaned_filename.replace(" ","_")
        return cleaned_filename



    
