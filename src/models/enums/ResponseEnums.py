from enum import Enum

class ResponseMessage(Enum):



    FILE_VALIDATE_SUCCESS="File Validate successfuly"
    FILE_Type_NOT_SUPPORTED= "File Type Not Supported"
    FILE_Size_TOO_BIG="File Size Too Big"
    UPLOAD_WITH_SUCCES="Upload With succes"
    UPLOAD_fAILED="Upload_Upload_failed"
    PROCESSING_FAILED="Processing Failed"
    PROCESSING_SUCCESS="Processing Success"
    NO_FILE_ERROR="No Files Found"
    FILE_ID_ERROR="No Files Found with this ID"
    PROJECT_NOT_FOUND_ERROR="Project not found"
    INSERT_INTO_VECTORDB_ERROR="Insert into vectorDB error"
    INSERT_INTO_VECTORDB_SUCCESS="Insert into vectorDB success"
    VECTORDB_COLLECTION_RETRIEVED="vectordb collection retrieved"
    VECTORDB_SEARCH_ERROR="vectordb search error"
    VECTORDB_SEARCH_SUCCESS="vectordb search success"
    RAG_ANSWER_ERROR="rag answer error"
    RAG_ANSWER_SUCCESS="rag answer success"
