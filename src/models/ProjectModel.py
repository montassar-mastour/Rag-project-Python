from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum as Da
from sqlalchemy.future import select
from sqlalchemy import func

class ProjectModel(BaseDataModel):
    """
    Model for project data.
    Inherits from BaseDataModel to utilize common functionality.
    """

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client

    @classmethod    
    async def create_instances(cls, db_client: object):
        instance = cls(db_client=db_client)
        return instance
    


    async def create_project(self, project: Project) :
        async with self.db_client() as session:
            async with session.begin():
                session.add(project)
            await session.commit()
            await session.refresh(project)

        return project 
    

    async def get_project_or_create_one(self, project_id: str):
        async with self.db_client() as session:
            async with session.begin():
                query = select(Project).where(Project.project_id==project_id)
                result = await session.execute(query)
                project= result.scalar_one_or_none()

                if project is None :
                    project_recor= Project(
                        project_id=project_id
                    )
                    project= await self.create_project(project=project_recor)
                    return project
                return project


        
    async def get_all_projects(self,page: int = 1, page_size: int = 10):
        async with self.db_client() as session:
            async with session.begin():

                total_doc=  await session.execute(select(
                    func.count(Project.project_id)
                )).scalar_one()

                total_page=(total_doc + page_size - 1) // page_size 
                skip = (page - 1) * page_size

                querry = select(Project).offset(skip).limit(page_size)
                results = await session.execute(querry)
                projects= results.scalars().all()

                return projects, total_page





    