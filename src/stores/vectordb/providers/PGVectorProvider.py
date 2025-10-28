from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import PgVectorTableSchemeEnums, PgVectorDistanceMethodEnums,PgVectorIndexTypeEnums, DistanceMethodEnums
from logging import getLogger
from typing import List
from models.db_schemes import RetrievedDocument
from sqlalchemy.sql import text as sql_text
import json

class PGVectorProvider(VectorDBInterface):
    def __init__(self, db_client, def_vector_size: int=786, distance_methods: str = None, index_threshold: int=100):

        self.db_client= db_client
        self.def_vector_size = def_vector_size
        self.distance_methods = distance_methods
        if distance_methods == DistanceMethodEnums.COSINE.value:
            distance_methods= PgVectorDistanceMethodEnums.COSINE.value
        elif distance_methods == DistanceMethodEnums.DOT_PRODUCT.value:
            distance_methods= PgVectorDistanceMethodEnums.DOT_PRODUCT.value
        
        self.pgvector_table_prefix = PgVectorTableSchemeEnums._PREFIX.value
        self.index_threshold = index_threshold
        self.distance_methods= distance_methods

        self.logger = getLogger("uvicorn")
        self.default_index_name = lambda collection_name : f"{collection_name}_pgvector_idx"

    async def connect(self):
        async with self.db_client() as session:
            async with session.begin():
                await session.execute(sql_text(
                    "CREATE EXTENSION IF NOT EXISTS vector;"
                ))
                try:
                    results= await session.execute(sql_text("CREATE 1 FROM pg_extension WHERE extname='vector';"))
                    await session.commit()
                    extension_exist= results.scalar_one_or_none()
                    
                    if not extension_exist:
                        await session.execute(sql_text("CREATE EXTENSION vector;"))
                        await session.commit()
                except Exception as e:
                    self.logger.error(f"Vector extension setup: {str(e)}")
                    await session.rollback()

    

    def disconnect(self):
        pass


    async def is_collection_existed(self, collection_name: str) -> bool:
        record=None
        async with self.db_client() as session:
            async with session.begin():
                list_tables_query = sql_text(
                    "SELECT * FROM pg_tables WHERE tablename = :table_name;"
                )
                result = await session.execute(list_tables_query, {"table_name": collection_name})        
                record= result.scalar_one_or_none()
        return record
    


    async def list_all_collections(self) -> List: 
        records=None
        async with self.db_client() as session:
            async with session.begin():
                list_tables_query = sql_text(
                    "SELECT tablename FROM pg_tables WHERE tablename LIKE :prefix;"
                )
                result = await session.execute(list_tables_query, {"prefix": self.pgvector_table_prefix})        
                records= result.scalars().all()
        return records
    
    async def get_collection_info(self, collection_name: str) -> dict:
        async with self.db_client() as session:
            async with session.begin():

                table_info_sql= sql_text(
                    """
                    SELECT schemaname, tablename, tableowner, tablespace, hasindexes
                    FROM pg_tables
                    WHERE tablename = :table_name
                    """
                )
                count_sql= sql_text( f'SELECT COUNT(*) FROM {collection_name}')

                table_info= await session.execute(table_info_sql, {"table_name": collection_name})
                record_count= await session.execute(count_sql)

                table_data= table_info.fetchone()

                if not table_data:
                    return None 
                
                return {
                    "table_info": {
                        "schemaname": table_data[0],
                        "tablename":  table_data[1],
                        "tableowner": table_data[2],
                        "tablespace": table_data[3],
                        "hasindexes": table_data[4],
                    },
                    "records_count": record_count.scalar_one(),
                }
            
    async def delete_collection(self, collection_name: str):
        is_collection_existed = self.is_collection_existed(collection_name)
        if await is_collection_existed:
            async with self.db_client() as session:
                async with session.begin():
                    
                    self.logger.info(f"Dropping table {collection_name}")
                    drop_table_sql= sql_text(f'DROP TABLE IF EXISTS {collection_name};')
                    await session.execute(drop_table_sql)
                    await session.commit()
            return True
        return False


    async def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        if do_reset:
            _ = await self.delete_collection(collection_name=collection_name)
        is_collection_existed = await self.is_collection_existed(collection_name)
        if not is_collection_existed :
            self.logger.info(f"Creating table {collection_name} with vector size {embedding_size}")

            async with self.db_client() as session:
                async with session.begin():

                    create_table_sql= sql_text(
                        f"""
                        CREATE TABLE {collection_name} (
                            {PgVectorTableSchemeEnums.ID.value} SERIAL PRIMARY KEY,
                            {PgVectorTableSchemeEnums.TEXT.value} TEXT,
                            {PgVectorTableSchemeEnums.VECTOR.value} VECTOR({embedding_size}),
                            {PgVectorTableSchemeEnums.METADATA.value} JSONB DEFAULT '{{}}'::JSONB,
                            {PgVectorTableSchemeEnums.CHUNK_ID.value} INTEGER,
                            FOREIGN KEY ({PgVectorTableSchemeEnums.CHUNK_ID.value}) REFERENCES chunks(chunk_id)
                        );
                        """
                    )
                    await session.execute(create_table_sql)
                    await session.commit()
                     
            return True
        
        return False
    
    async def insert_one(self, collection_name: str, text:str, 
                         vector: list, metadata: dict=None, record_id: str=None):
        
        is_collection_existed= await self.is_collection_existed(collection_name)
        if not is_collection_existed :
            self.logger.error(f"Can not inser new record to non-existed collection: {collection_name}")
            return False

        if not record_id :
            self.logger.error(f"Can not inser new record without chunk_id: {collection_name}")
            return False
        
        async with self.db_client() as session:
            async with session.begin():
                insert_sql= sql_text(
                    f"""
                    INSERT INTO :table_name 
                    ({PgVectorTableSchemeEnums.TEXT.value}, {PgVectorTableSchemeEnums.VECTOR.value}, 
                    {PgVectorTableSchemeEnums.METADATA.value}, {PgVectorTableSchemeEnums.CHUNK_ID.value})
                    VALUES (:text, :vector, :metadata, :chunk_id);
                    """
                )

                metadata_json= json.dumps(metadata, ensure_ascii=False) if metadata else "{}"
                await session.execute(insert_sql,{
                    "table_name": collection_name,
                    "text": text,
                    "vector": "[" + ",".join([str(v) for v in vector]) + "]",
                    "metadata": metadata_json,
                    "chunk_id": record_id
                })
                await session.commit()

                await self.create_vector_index(collection_name=collection_name)

        return True
    
    async def insert_many(self, collection_name: str, texts: list, vectors: list, 
                    metadata: list=None, record_ids: list=None, batch_size: int=50):
        
        is_collection_existed= await self.is_collection_existed(collection_name)
        if not is_collection_existed :
            self.logger.error(f"Can not inser new records to non-existed collection: {collection_name}")
            return False
        
        if len(vectors) != len(record_ids):
            self.logger.error(f"Invalid data items fro collection: {collection_name}")
            return False
        
        if not metadata or len(metadata) ==0 :
            metadata=[None]*len(texts)
        
        async with self.db_client() as session:
            async with session.begin():

                for i in range(0, len(texts), batch_size):
                    batch_end = i + batch_size

                    batch_texts = texts[i:batch_end]
                    batch_vectors = vectors[i:batch_end]
                    batch_metadata = metadata[i:batch_end]
                    batch_records_ids = record_ids[i:batch_end]

                    values =[]

                    for _text, _vector, _metadata, _record_id in zip(batch_texts, batch_vectors, 
                                                                     batch_metadata, batch_records_ids):
                        metadata_json= json.dumps(_metadata, ensure_ascii=False) if _metadata else "{}"
                        values.append({
                            "text": _text,
                            "vector": "[" + ",".join([str(v) for v in _vector]) + "]",
                            "metadata": metadata_json,
                            "chunk_id": _record_id
                        })

                    batch_insert_sql = sql_text(f"""
                        INSERT INTO {collection_name} 
                        ({PgVectorTableSchemeEnums.TEXT.value}, {PgVectorTableSchemeEnums.VECTOR.value}, 
                        {PgVectorTableSchemeEnums.METADATA.value}, {PgVectorTableSchemeEnums.CHUNK_ID.value})
                        VALUES (:text, :vector, :metadata, :chunk_id)
                    """)

                    await session.execute(batch_insert_sql, values)


        await self.create_vector_index(collection_name=collection_name)

        return True 
    
    

    async def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):
        is_collection_existed= await self.is_collection_existed(collection_name)
        if not is_collection_existed :
            self.logger.error(f"Can not search for records to non-existed collection: {collection_name}")
            return False
        
        
        vector = "[" + ",".join([str(v) for v in vector]) + "]"
        async with self.db_client() as session:
            async with session.begin():
                search_sql= sql_text(
                    f"""
                    SELECT {PgVectorTableSchemeEnums.TEXT.value} AS text, 
                    1 - ({PgVectorTableSchemeEnums.VECTOR.value} <=> :vector) AS score
                    FROM {collection_name}
                    ORDER BY score DESC
                    LIMIT :limit;
                    """
                )   
                result = await session.execute(search_sql, {
                    "vector": vector,
                    "limit": limit
                })
                records= result.fetchall()

                if not records or len(records)==0:
                    return None
                
                return [    
                    RetrievedDocument(**{
                        "score": record.score,
                        "text" : record.text
                    })
                    for record in records
                ]
                


    async def is_index_existed(self, collection_name: str) -> bool:
        index_name= self.default_index_name(collection_name)

        async with self.db_client() as session:
            async with session.begin():    
                check_index_sql= sql_text(
                    """
                    SELECT 1 
                    FROM pg_indexes 
                    WHERE tablename = :table_name AND indexname = :index_name
                    """
                )
                result = await session.execute(check_index_sql, {
                    "table_name": collection_name,
                    "index_name": index_name
                })

                return bool(result.scalar_one_or_none()) 



    async def create_vector_index(self, collection_name: str, index_type: str= PgVectorIndexTypeEnums.HNSW.value):         
                
        is_index_existed= await self.is_index_existed(collection_name=collection_name)

        if is_index_existed : 
            return False
        
        
        async with self.db_client() as session:
            async with session.begin():
                count_sql= sql_text( f'SELECT COUNT(*) FROM {collection_name}')
                result = await session.execute(count_sql)
                record_count= result.scalar_one_or_none()   

                if record_count < self.index_threshold:
                    return False
                
                self.logger.info(f" Start creating index for table {collection_name} with index type {index_type}")
                
                index_name= self.default_index_name(collection_name)    
                create_index_sql= sql_text(
                    f"""
                    CREATE INDEX {index_name}
                    ON {collection_name}
                    USING {index_type} ({PgVectorTableSchemeEnums.VECTOR.value} {self.distance_methods});
                    """
                )
                await session.execute(create_index_sql)
                await session.commit()

                self.logger.info(f"End creation index for table {collection_name}")



    async def reset_vector_index(self, collection_name: str, index_type: str= PgVectorIndexTypeEnums.HNSW.value)-> bool:

            async with self.db_client() as session:
                async with session.begin():

                    self.logger.info(f"Dropping index for table {collection_name}")
                    drop_index_sql= sql_text(
                        f"""
                        DROP INDEX IF EXISTS :index_name;
                        """
                    )
                    await session.execute(drop_index_sql,{
                        "index_name": self.default_index_name(collection_name)
                    })
            return await self.create_vector_index(collection_name=collection_name, index_type=index_type)

 
                
