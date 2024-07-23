import logging
logger = logging.getLogger(__name__)

import time
import json
from fastapi import HTTPException
import bolt11

from src.database import db
import src.invoice as invoice_utils




async def update_user_balance_for_paid_invoices(username: str):
    user_collection = db.db.get_collection("users")
    invoices_collection = db.db.get_collection("invoices")
    
    total_amount = await process_invoices_and_accumulate_total(username, invoices_collection)

    if total_amount > 0:
        user = await user_collection.find_one({"username": username})
        if not user:
            user = {"username": username, "balance": total_amount}
            await user_collection.insert_one(user)
        else:
            new_balance = user["balance"] + total_amount
            await user_collection.update_one(
                {"username": username},
                {"$set": {"balance": new_balance}}
            )

    user = await user_collection.find_one({"username": username})
    if not user:
        logger.debug(f"User '{username}' not found even after insertion.")
        # NOTE: wow... this would be a huge issue... we need to track and report these
        raise HTTPException(status_code=404, detail="User not found")

    return user


async def check_and_update_invoice_status(username: str):
    invoices_collection = db.db.get_collection("invoices")
    user_collection = db.db.get_collection("users")

    total_amount = await process_invoices_and_accumulate_total(username, invoices_collection)

    if total_amount > 0:
        user = await user_collection.find_one({"username": username})
        if not user:
            user = {"username": username, "balance": total_amount}
            await user_collection.insert_one(user)
        else:
            new_balance = user["balance"] + total_amount
            await user_collection.update_one(
                {"username": username},
                {"$set": {"balance": new_balance}}
            )
        return {"message": f"User {username} balance updated by {total_amount}"}

    return {}


async def process_invoices_and_accumulate_total(username: str, invoices_collection):
    pending_invoices = await fetch_all_pending_invoices(username)
    total_amount = 0
    
    for invoice in pending_invoices:
        if invoice_utils.check_for_payment(invoice):
            total_amount += invoice["amount"]
            await invoices_collection.update_one(
                {"_id": invoice["_id"]},
                {"$set": {"status": "archived"}}
            )
    
    return total_amount


async def fetch_all_pending_invoices(username: str):
    invoices_collection = db.db.get_collection("invoices")
    return await invoices_collection.find({"username": username, "status": "pending"}).to_list(length=None)





# THIS IS UNUSED
def decode_invoice(invoice):
    try:
        invoice = json.loads(invoice)

         # TODO don't need this... will throw an exception
        if invoice is None:
            return None
    except TypeError:
        return None


    pr = invoice['pr']
    invoice_date = bolt11.decode(pr).date
    print(f"Invoice created: {invoice_date}")

    amount = bolt11.decode(pr).amount_msat / 1000
    tags: bolt11.models.tags.Tags = bolt11.decode(pr).tags

    # if not tags.has(bolt11.models.tags.TagChar.description):
    #     st.error("Invoice is missing a description tag")
    #     return None
    
    if not tags.has(bolt11.models.tags.TagChar.expire_time):
        print("ERROR: Invoice is missing an expiry tag")
        # expiry = 86400
        expiry = 3600 # 60 minutes ... why default to this? Because I'm a bad programmer.
        # return None
    else:
        expiry = tags.get(bolt11.models.tags.TagChar.expire_time).data
        print(f"Expiry: {expiry} seconds")

    # current time in seconds since epoch
    now = int(time.time())
    print(f"Now: {now}")
    # invoice expiry time in seconds since epoch
    invoice_expiry = invoice_date + expiry
    # time remaining in seconds
    time_remaining = invoice_expiry - now
    print(f"Time remaining: {time_remaining} seconds")

    # if time_remaining < 0:
    if time_remaining < 60: # if less than 60 seconds remaining... just consider it expired
        print("ERROR: Invoice has expired")
        return None


    # print(f"Amount: {amount} sats")
    # for t in tags:
    #     print(f"Tag: {t.char} : {t.data}")

    return invoice

