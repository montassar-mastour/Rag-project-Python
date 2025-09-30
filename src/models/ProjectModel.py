from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum as Da

class ProjectModel(BaseDataModel):
    """
    Model for project data.
    Inherits from BaseDataModel to utilize common functionality.
    """

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[Da.COLLECTION_PROJECT_NAME.value]


    async def create_project(self, project: Project) :

        doc = project.model_dump(by_alias=True, exclude_unset=True)
        result = await self.collection.insert_one(doc)
        project.id = result.inserted_id
        return project
    

    async def get_project_or_create_one(self, project_id: str):
        """
        Retrieves a project by its ID or creates a new one if it doesn't exist.
        """
        record = await self.collection.find_one({"project_id": project_id})

        if record is not None:
            return Project(**record)
        
        else:
            project = Project(project_id=project_id)
            project = await self.create_project(project=project)
            return project
        
    async def get_all_projects(self,page: int = 1, page_size: int = 10):
        """
        Retrieves all projects from the database.
        """

        total_doc = await self.collection.count_documents({})
        total_pages = (total_doc + page_size - 1) // page_size 
        skip = (page - 1) * page_size
        curser= self.collection.find().skip(skip).limit(page_size)
        projects = [Project(**doc) async for doc in curser]

        return projects, total_pages




    