import os
from logger import logger
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

import streamlit as st

# from database import connect_to_mongo, close_mongo_connection



async def connect_to_mongo():
    logger.info("Connecting to MongoDB...")
    db.client = AsyncIOMotorClient(os.getenv("MONGO_DETAILS", "mongodb://localhost:27017"))
    db.db = db.client.user_balance
    logger.info("Connected to MongoDB")


async def close_mongo_connection():
    logger.info("Closing MongoDB connection...")
    db.client.close()
    logger.info("Closed MongoDB connection")


class Database:
    client: AsyncIOMotorClient = None
    db = None


db = Database()





async def main():
    # Ensure MongoDB connection is established before any operations
    await connect_to_mongo()


    # Set up Streamlit layout and title
    st.title("Admin Dashboard")


    st.header("All Users")
    user_collection = db.db.get_collection("users")
    users = await user_collection.find().to_list(length=None)
    st.write(users)



    st.header("All Invoices")
    invoices_collection = db.db.get_collection("invoices")
    invoices = await invoices_collection.find().to_list(length=None)
    # st.write(invoices)

    # show as a table with a delete button
    for invoice in invoices:
        st.write(invoice)
        if st.button("Delete", key=invoice["_id"]):
            await invoices_collection.delete_one({"_id": invoice["_id"]})
            st.write("Deleted invoice")
            break


    await close_mongo_connection()


asyncio.run(main())