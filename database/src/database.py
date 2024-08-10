import os
# import logging
# logger = logging.getLogger(__name__)
from src.logger import logger

from motor.motor_asyncio import AsyncIOMotorClient



class Database:
    client: AsyncIOMotorClient = None
    db = None


db = Database()




async def connect_to_mongo():
    logger.info("Connecting to MongoDB...")
    db.client = AsyncIOMotorClient(os.getenv("MONGO_DETAILS", "mongodb://localhost:27017"))
    db.db = db.client.user_balance
    logger.info("Connected to MongoDB")


async def close_mongo_connection():
    logger.info("Closing MongoDB connection...")
    db.client.close()
    logger.info("Closed MongoDB connection")

# mongosh
# show databases
# use user_balance
# show collections
# db.users.find().pretty()
# db.users.drop()
