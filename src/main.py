from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings

@asynccontextmanager

async def lifespan():
    # Startup code
    settings = get_settings()
    app.mongodb_conn = AsyncIOMotorClient(settings.MONGO_URL)
    app.mongodb = app.mongodb_client[settings.MONGO_DB_NAME]
    print("Connected to the MongoDB database")

    yield

    # Shutdown code
    app.mongodb_client.close()
    print("Closed connection to the MongoDB database")

app=  FastAPI(lifespan=lifespan)

app.include_router(base.base_router)

app.include_router(data.data_router)

