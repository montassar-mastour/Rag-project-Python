from fastapi import FastAPI, APIRouter
import os
base_route = APIRouter(
     prefix="/api/v1",
     tags=["api_v1"],

)


@base_route.get("/")
async def welcome():
     app_name= os.getenv('APP_NAME')
     app_version= os.getenv('APP_VERSION')
     return{
        "app_name" : app_name,
        "app_version" : app_version
    }  

