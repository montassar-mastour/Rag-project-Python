from ..LLMInterface import LLMInterface
from openai import OpenAI
import logging
from ..LLMEnums import CohereEnums, DocumentTypeEnums
import cohere

class CohereProvider(LLMInterface):
    def __init__(self, api_key: str, default_input_max_caracters:int=1000, 
                 default_output_max_tokens:int=1000, default_generation_temperature:float=0.1):
        self.api_key = api_key
        self.default_input_max_caracters = default_input_max_caracters
        self.default_output_max_tokens = default_output_max_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.Client(api_key= self.api_key)
        self.logger = logging.getLogger(__name__)

            
    def set_generate_method(self, model_id: str) :
        self.generation_model_id = model_id

    
    def set_embedding_model(self, model_id: str, embedding_size:int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        return text[:self.default_input_max_caracters].strip()

    
    def generate_text(self, prompt: str,chat_history: list=[] ,max_output_tokens: int=None, temperature: float=None):
        
        if not self.client:
            self.logger.error("Cohere was not set")
            return None
        if not self.egeneration_model_id:
            self.logger.error("generation model for Cohere was not set.")
            return None
        
        if max_output_tokens is None:
            max_output_tokens = self.default_output_max_tokens
        if temperature is None:
            temperature = self.default_generation_temperature


        response = self.client.chat(
            model=self.generation_model_id,
            chat_history=chat_history,
            messages=self.process_text(prompt),
            max_tokens=max_output_tokens,
            temperature=temperature
        )
        
        if not response or not response.text :
            self.logger.error("No Generation returned from Cohere.")
            return None
        return response.text
    

         
    def embed_text(self, text: str, document_type: str=None):
        if not self.client:
            self.logger.error("Cohere was not set")
            return None
        if not self.embedding_model_id:
            self.logger.error("Embedding model for OpeCoherenAI was not set.")
            return None
        
        input_type = CohereEnums.DOCUMENT.value
        if document_type == DocumentTypeEnums.QUERY.value:
            input_type = CohereEnums.QUERY.value

        
        response = self.client.embed(
            model=self.embedding_model_id,
            texts=[self.process_text(text)],
            input_type=input_type,
            embedding_types=['float']
        )


        if response is None:
            raise ValueError("No response from Cohere API")

        if not hasattr(response, "embeddings") or not hasattr(response.embeddings, "float"):
            raise ValueError("Invalid embedding structure from Cohere API")
        
        return response.embeddings.float[0]

    
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": self.process_text(prompt)
        }