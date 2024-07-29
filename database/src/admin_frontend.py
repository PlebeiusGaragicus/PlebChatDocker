import os
import json
import datetime
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

# OpenAI
# GPT-4o
#       $0.0050 / 1K input tokens
#       $0.0150 / 1K output tokens

# gpt-4-turbo
#       $0.0100 / 1K INPUT tokens
#       $0.0300 / 1K OUTPUT tokens

# gpt-3.5-turbo-16k-0613
#       $0.0030 / 1K INPUT tokens
#       $0.0040 / 1K OUTPUT tokens

# mixtral 8x7b
#       $0.00071 per / 1000 (INPUT AND OUTPUT)

# mistral 7b
#       $0.00022 per / 1000 (INPUT AND OUTPUT)


    st.header("tokens per dollar calculation")
    # enter in the price per 1000 tokens and the price of bitcoin and calculate the satoshi price per 1000 tokens
    price_per_10000_tokens = st.number_input("Enter price per 10K tokens", value=0.05)
    price_of_bitcoin = st.number_input("Enter price of bitcoin", value=68000)
    ans = price_per_10000_tokens * 100_000_000 / price_of_bitcoin
    st.write(f"Price per 10K tokens in satoshis: {ans}")






    st.header("PR decoder")
    pr = st.text_input("Enter PR code")
    if st.button("Decode PR"):
        import bolt11
        decoded = bolt11.decode(pr)
        st.json( json.dumps(decoded.data, indent=4) )
        st.write(f"Has expired: `{decoded.has_expired()}`")
        st.write(f"Expires at: `{decoded.expiry_date}`")
        st.write(f"Time until expiry: `{decoded.expiry_date - datetime.datetime.now()}` hours")

    st.header("All Users")
    user_collection = db.db.get_collection("users")
    users = await user_collection.find().to_list(length=None)
    # st.write(users)
    # show each user as a table with a delete button
    for user in users:
        st.write(user)
        if st.button("Delete", key=user["_id"]):
            await user_collection.delete_one({"_id": user["_id"]})
            st.write("Deleted user")
            break

    st.header("Set a user's balance")
    user_to_adjust = st.selectbox("Select a user", [user["username"] for user in users])
    new_balance = st.number_input("Enter new balance")
    if st.button("Set balance"):
        await user_collection.update_one({"username": user_to_adjust}, {"$set": {"balance": new_balance}})
        st.write("Updated user balance")


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

    st.header("All Transactions")
    with st.expander("show"):
        transactions_collection = db.db.get_collection("transactions")
        transactions = await transactions_collection.find().to_list(length=None)
        # st.write(transactions)
        # show as a table with a delete button
        for transaction in transactions:
            st.write(transaction)
            st.markdown(f"[View thread](http://localhost:3000/s/{transaction['thread_id']})")
            if st.button("Delete", key=transaction["_id"]):
                await transactions_collection.delete_one({"_id": transaction["_id"]})
                st.write("Deleted transaction")
                break

    await close_mongo_connection()


asyncio.run(main())
