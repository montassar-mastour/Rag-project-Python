from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
from .enums.DataBaseEnum import DataBaseEnum as Da
from bson import ObjectId

class AssetModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collction = self.db_client[Da.COLLECTION_ASSET_NAME.value]

    @classmethod    
    async def create_instances(cls, db_client: object):
        instance = cls(db_client=db_client)
        await instance.init_collection_indexes()
        return instance



    async def init_collection_indexes(self):
        all_collections = await self.db_client.list_collection_names()
        if Da.COLLECTION_ASSET_NAME.value not in all_collections:
            self.collection = self.db_client[Da.COLLECTION_ASSET_NAME.value]
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["keys"],
                    name=index["name"],
                    unique=index["unique"]
                )

    async def create_asset(self, asset: Asset) :
        doc = asset.model_dump(by_alias=True, exclude_unset=True)
        result = await self.collection.insert_one(doc)
        asset.id = result.inserted_id
        return asset
    

    async def get_all_projects_assets(self,asset_project_id): 
        return await self.collection.find({
            "project_id": ObjectId(asset_project_id) 
            if isinstance(asset_project_id, str)
            else asset_project_id
            }).to_list(length=None)