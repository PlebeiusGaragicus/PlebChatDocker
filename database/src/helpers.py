import logging
logger = logging.getLogger(__name__)

import time
import json
from typing import Union, Optional

import requests
from fastapi import HTTPException
import bolt11

from src.config import TOKENS_PER_SAT
from src.database import db
# import src.invoice as invoice_utils





async def return_user_balance(username: str) -> Optional[int]:
    """
    Retrieve the balance for a given user from the database.

    This function interacts with a MongoDB database to find and return the
    balance of a user specified by their username. If the user is not found 
    in the database, it logs a warning and returns None. If the user is found 
    but does not have a balance, it also returns None.

    Args:
        username (str): The username of the user whose balance is to be retrieved.

    Returns:
        Optional[int]: The balance of the user as an integer if found, otherwise None.

    Raises:
        HTTPException: If the user is not found in the database, an HTTPException 
        with status code 404 may be raised (commented out in this code).
    """
    user_collection = db.db.get_collection("users")
    user = await user_collection.find_one({"username": username})
    if not user:
        logger.warning("User not found when checking a balance - user must not be registered.")
        # raise HTTPException(status_code=404, detail="User not found")
        return None

    balance = user.get("balance", None)
    if balance is not None:
        return int(balance)
    return None # it should never reach here, but just in case...







async def fetch_all_pending_invoices(username: str):
    invoices_collection = db.db.get_collection("invoices")
    return await invoices_collection.find({"username": username, "status": "pending"}).to_list(length=None)




async def return_first_pending_invoice(username: str):
    """
        Only returns a single invoice.
        Searches for, and returns, oldest invoice.
    """
    invoices_collection = db.db.get_collection("invoices")

    # Fetch the oldest pending invoice
    oldest_invoice = await invoices_collection.find_one(
        {"username": username, "status": "pending"},
        sort=[("issued_at", 1)]
    )

    return oldest_invoice






async def poll_for_payment():
    pass




# TODO should this be an async function?
def check_for_payment(invoice):
    """
    Check the payment status of an invoice.

    Parameters:
    - invoice: The invoice object containing the details.

    Returns:
    - True if the invoice is settled (paid).
    - False otherwise.
    """
    logger.debug(f"Checking payment status for invoice: {invoice}")

    logger.debug(invoice)
    verify_url = invoice['verify']

    response = requests.get(verify_url)
    if response.status_code == 200:
        status = response.json().get('status')
        settled = response.json().get('settled', False)

        logger.info(f"Status: {status}")
        logger.info(f"Settled: {settled}")

        if settled:
            logger.info("Invoice has been paid! 🎉")
            return True
        else:
            logger.info("Invoice has not been settled yet.")
            return False
    else:
        logger.error("ERROR IN VERIFYING INVOICE PAYMENT STATUS")
        logger.error(response.status_code, response.text)
        return False






def create_invoice(amount: int, payee_address: str):
    """
    Create a lightning invoice.

    Parameters:
    - amount: Amount in satoshis.
    - payee_address: The lightning address to receive the payment.
    
    Returns:
    - Invoice details as a dictionary if successful.
    - Error message if the request fails.
    """
    logger.info(f"Creating invoice for {amount} sats")

    url = "https://api.getalby.com/lnurl/generate-invoice"
    params = {
        "ln": payee_address,
        "amount": amount * 1000,  # in millisats
        "comment": f"Purchased {amount * TOKENS_PER_SAT} tokens"
    }

    response = requests.get(url, params=params)

    logger.info(f"Creating invoice for {amount} sats")
    if response.status_code == 200:
        # Successfully created the invoice
        invoice_details = response.json()
        invoice_details['amount'] = amount  # Adding the amount to the invoice details
        logger.info("Invoice created!")
        logger.debug(json.dumps(invoice_details, indent=4))  # Pretty print the invoice details
        return invoice_details
    else:
        # Failed to create the invoice
        logger.error(response)
        error_message = f"Failed to create invoice: {response.status_code} {response.text}"
        logger.error(error_message)
        return {"error": error_message}








# async def process_invoices_and_accumulate_total(username: str, invoices_collection):
#     pending_invoices = await fetch_all_pending_invoices(username)
#     total_amount = 0
    
#     for invoice in pending_invoices:
#         if invoice_utils.check_for_payment(invoice):
#             total_amount += invoice["amount"]
#             await invoices_collection.update_one(
#                 {"_id": invoice["_id"]},
#                 {"$set": {"status": "archived"}}
#             )
    
#     return total_amount























# async def update_user_balance_for_paid_invoices(username: str):
#     user_collection = db.db.get_collection("users")
#     invoices_collection = db.db.get_collection("invoices")
    
#     total_amount = await process_invoices_and_accumulate_total(username, invoices_collection)

#     if total_amount > 0:
#         user = await user_collection.find_one({"username": username})
#         if not user:
#             user = {"username": username, "balance": total_amount}
#             await user_collection.insert_one(user)
#         else:
#             new_balance = user["balance"] + total_amount
#             await user_collection.update_one(
#                 {"username": username},
#                 {"$set": {"balance": new_balance}}
#             )

#     user = await user_collection.find_one({"username": username})
#     if not user:
#         # NOTE: wow... this would be a huge issue... we need to track and report these
#         logger.debug(f"User '{username}' not found even after insertion.")
#         raise HTTPException(status_code=404, detail="User not found")

#     return user


# async def check_and_update_invoice_status(username: str):
#     # invoices_collection = db.db.get_collection("invoices")
#     # user_collection = db.db.get_collection("users")

#     # total_amount = await process_invoices_and_accumulate_total(username, invoices_collection)

#     if total_amount > 0:
#         user = await user_collection.find_one({"username": username})
#         if not user:
#             user = {"username": username, "balance": total_amount}
#             await user_collection.insert_one(user)
#         else:
#             new_balance = user["balance"] + total_amount
#             await user_collection.update_one(
#                 {"username": username},
#                 {"$set": {"balance": new_balance}}
#             )
#         return {"message": f"User {username} balance updated by {total_amount}"}

#     return {}





# THIS IS UNUSED

# def decode_invoice(invoice):
#     try:
#         invoice = json.loads(invoice)

#          # TODO don't need this... will throw an exception
#         if invoice is None:
#             return None
#     except TypeError:
#         return None


#     pr = invoice['pr']
#     invoice_date = bolt11.decode(pr).date
#     print(f"Invoice created: {invoice_date}")

#     amount = bolt11.decode(pr).amount_msat / 1000
#     tags: bolt11.models.tags.Tags = bolt11.decode(pr).tags

#     # if not tags.has(bolt11.models.tags.TagChar.description):
#     #     st.error("Invoice is missing a description tag")
#     #     return None
    
#     if not tags.has(bolt11.models.tags.TagChar.expire_time):
#         print("ERROR: Invoice is missing an expiry tag")
#         # expiry = 86400
#         expiry = 3600 # 60 minutes ... why default to this? Because I'm a bad programmer.
#         # return None
#     else:
#         expiry = tags.get(bolt11.models.tags.TagChar.expire_time).data
#         print(f"Expiry: {expiry} seconds")

#     # current time in seconds since epoch
#     now = int(time.time())
#     print(f"Now: {now}")
#     # invoice expiry time in seconds since epoch
#     invoice_expiry = invoice_date + expiry
#     # time remaining in seconds
#     time_remaining = invoice_expiry - now
#     print(f"Time remaining: {time_remaining} seconds")

#     # if time_remaining < 0:
#     if time_remaining < 60: # if less than 60 seconds remaining... just consider it expired
#         print("ERROR: Invoice has expired")
#         return None


#     # print(f"Amount: {amount} sats")
#     # for t in tags:
#     #     print(f"Tag: {t.char} : {t.data}")

#     return invoice

