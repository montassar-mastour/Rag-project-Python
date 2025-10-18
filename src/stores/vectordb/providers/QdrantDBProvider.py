from qdrant_client import models, QdrantClient
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
from logging import getLogger
from typing import List
from models.db_schemes import RetrievedDocument


class QdrantDBProvider(VectorDBInterface):
    def __init__(self, db_path: str, distance_methods: str):

        self.client= None
        self.db_path = db_path
        self.distance_methods = None

        if distance_methods == DistanceMethodEnums.COSINE.value:
            self.distance_methods = models.Distance.COSINE
        elif distance_methods == DistanceMethodEnums.DOT.value:
            self.distance_methods = models.Distance.DOT

        self.logger = getLogger(__name__)

    def connect(self):
        self.client = QdrantClient(path=self.db_path)
        self.logger.info("Connected to QdrantDB at %s", self.db_path)

    def disconnect(self):
        self.client = None
        self.logger.info("Disconnected from QdrantDB")

    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)
    
    def list_all_collections(self) -> List: 
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)
    
    def delete_collection(self, collection_name: str):
        if self.is_collection_existed(collection_name):
            return self.client.delete_collection(collection_name=collection_name)
        
    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)
        if not self.is_collection_existed(collection_name):
            _ = self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_methods
                )
            )

            return True
        
        return False
    
    def insert_one(self, collection_name: str, text:str, vector: list, metadata: dict=None, record_id: str=None):
        if not self.is_collection_existed(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False
        
        try:
            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[  
                    models.Record(
                        id=[record_id],
                        vector=vector,
                        payload={"text": text, "metadata":metadata
                        }
                    )
                ]   
            )
        except Exception as e:
            self.logger.error(f"Error inserting record: {e}")
            return False
        
        return True
    
    def insert_many(self, collection_name: str, texts: list, vectors: list, metadata: list=None, record_ids: list=None, batch_size: int=50):
        if metadata == None:
            metadata =[]*len(texts)

        if record_ids == None:
            record_ids = list(range(0, len(texts)))

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size

            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_records_ids = record_ids[i:batch_end]

            batch_records=[
                models.Record(
                    id=batch_records_ids[x],
                    vector=batch_vectors[x],
                    payload={"text": batch_texts[x], "metadata":batch_metadata[x]
                    }
                )
                for x in range(len(batch_texts))
            ]

            try :
                _ = self.client.upload_records(
                collection_name=collection_name,
                records=batch_records
                )
            except Exception as e:
                self.logger.error(f"Error inserting batch starting at index {i}: {e}")
                return False
            
        return True
    
    def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):
        results =  self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit
        )

        if not results or len(results)==0:
            return None
        
        return [
            RetrievedDocument(**{
                "score": result.score,
                "text" : result.payload["text"]
            })
            for result in results
        ]
        
    

