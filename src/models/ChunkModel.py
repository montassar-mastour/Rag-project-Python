from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnum import DataBaseEnum as Da
from bson import ObjectId
from pymongo import InsertOne

class ChunkModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[Da.COLLECTION_CHUNK_NAME.value]

    
    async def create_chunk(self, chunk: DataChunk) :

        doc = chunk.model_dump(by_alias=True, exclude_unset=True)
        result = await self.collection.insert_one(doc)
        chunk.id = str(result.inserted_id)
        return chunk
    
    
    async def get_chunk(self, chunck_id: str):
        record = await self.collection.find_one({
            "_id" : ObjectId(chunck_id)
            })
        if record is None: 
            return None
        
        return DataChunk(**record)
    
    async def insert_many_chunks(self, chunks: list, batch_size: int = 100):
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            operations =[
                InsertOne(chunk.model_dump(by_alias=True, exclude_unset=True))
                for chunk in batch
                ]
            await self.collection.bulk_write(operations)

        return len(chunks)
    async def delete_chunks_by_project_id(self, project_id: object):
        result = await self.collection.delete_many({
            "chunk_project_id": project_id
        })
        return result.deleted_count

