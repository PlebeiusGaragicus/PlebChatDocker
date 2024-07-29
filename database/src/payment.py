import os
import json
from typing import Optional
import requests
# from fastapi import HTTPException
import bolt11
# from bson.objectid import ObjectId

import logging
logger = logging.getLogger(__name__)

from src.config import TOKENS_PER_SAT #TODO: This needs to be a function that we can calculate routinely
from src.database import db




async def return_user_balance(username: str) -> Optional[int]:
    """
    Retrieve the balance for a given user from the database.
    This function interacts with a MongoDB database to find and return the
    balance of a user, specified by their username.
    If the user is not found in the database, it logs a warning and returns None.
    If the user is found but does not have a balance, it also returns None.

    Args:
        username (str): The username of the user whose balance is to be retrieved.

    Returns:
        Optional[int]: The balance of the user as an integer if found, otherwise None.

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

    logger.critical("User found but balance not found - this should not happen.")
    return None # it should never reach here, but just in case...






async def create_invoice(username: str, amount: int = 50):
    logger.info(f"Creating invoice for {amount} sats")

    payee_address = os.getenv('PAYEE_LUD16')
    if not payee_address:
        raise NotImplementedError("Payee address is required in your .env file!!")

    url = "https://api.getalby.com/lnurl/generate-invoice"
    params = {
        "ln": payee_address,
        "amount": amount * 1000,  # in millisats
        "description": f"Purchased {amount * TOKENS_PER_SAT} tokens"
    }

    logger.info(f"Creating invoice for {amount} sats")

    response = requests.get(url, params=params)
    if response.status_code == 200:
        invoice_details = response.json()['invoice']
        logger.debug("Invoice created!")
        logger.debug(json.dumps(invoice_details, indent=4))

        pr = invoice_details['pr']
        actual_amount = bolt11.decode(pr).amount_msat // 1000

        invoice = {
            "username": username,
            "status": "pending",
            "pr": invoice_details['pr'],
            "verify": invoice_details['verify'],
            "amount": actual_amount,
        }
        logger.debug("WE JUST CREATED THIS INVOICE:")
        logger.debug(invoice)

        # save to the database
        invoices_collection = db.db.get_collection("invoices")
        await invoices_collection.insert_one(invoice)
        # NOTE: WATCH OUT! MongoDB adds a ObjectId '_id' here and it's not serializable to JSON!
        # logger.debug("AFTER WE ADDED TO THE DATABASE:"
        # logger.debug(invoice)
        invoice['_id'] = str(invoice['_id'])


        return invoice

    else:
        error_message = f"Failed to create invoice: {response.status_code} {response.text}"

        logger.error(response)
        logger.error(error_message)
        return {"error": error_message}





async def get_pending_invoices(username: str):
    invoices_collection = db.db.get_collection("invoices")
    pending = await invoices_collection.find({"username": username, "status": "pending"}).to_list(length=None)
    return pending


async def get_single_pending_invoice(username: str):
    invoices_collection = db.db.get_collection("invoices")
    latest_pending = await invoices_collection.find({"username": username, "status": "pending"}, sort=[("_id", -1)]).to_list(length=None)
    # latest = await invoices_collection.find_one({"username": username}, sort=[("_id", -1)])
    if latest_pending and len(latest_pending) > 0:
        latest_pending = latest_pending[0]
        # convert the ObjectId to a string because it's not serializable to JSON otherwise (for FastAPI)
        # THIS IS A PERNICIOUS BUG WHEN YOU DON'T KNOW WHY IT'S FAILING!
        latest_pending['_id'] = str(latest_pending['_id'])
    return latest_pending


async def poll_pending_invoices(username: str) -> None:
    pending_invoices = await get_pending_invoices(username)

    for invoice in pending_invoices:
        await credit_user_if_paid(invoice, username)





async def credit_user_if_paid(invoice: dict, username: str) -> bool:
    """
        Takes an invoices, calls the verify url, credits the user if paid and updates the invoice status

        NOTE: This also checks if the invoice has expired and updates the status accordingly
    """
    amount_paid = await check_invoice_for_payment_or_expiry(invoice)

    if amount_paid is None:
        logger.debug("This invoice has not been paid yet.")
        # return False
        return

    if amount_paid == -1:
        logger.debug("This invoice has expired.")
        # return False
        # update the invoice status
        invoices_collection = db.db.get_collection("invoices")
        await invoices_collection.update_one(
            {"pr": invoice['pr']},
            {"$set": {"status": "expired"}}
        )
        return

    # Credit the user
    user_collection = db.db.get_collection("users")
    user = await user_collection.find_one({"username": username})

    if not user:
        # A new user is paying for the first time and being "registered" here
        user = {"username": username, "balance": amount_paid}
        await user_collection.insert_one(user)

    else:
        new_balance = user["balance"] + amount_paid
        await user_collection.update_one(
            {"username": username},
            {"$set": {"balance": new_balance}}
        )

    # Update the invoice status
    invoices_collection = db.db.get_collection("invoices")
    await invoices_collection.update_one(
        {"pr": invoice['pr']},
        {"$set": {"status": "settled"}}
    )

    logger.debug("This invoice has been paid! 💰")
    # return True






async def check_invoice_for_payment_or_expiry(invoice: dict) -> Optional[int]:
    """
        Calls the verify url and checks if the invoice has been paid.

        If it has, it returns the amount paid.

        If the invoice has expired, it returns -1

        If the invoice has not been paid yet, it returns None

        If there is an error, it returns None
    """
    logger.debug(f"Checking payment status for invoice: {invoice}")

    verify_url = invoice['verify']

    response = requests.get(verify_url)
    if response.status_code == 200:
        status = response.json().get('status')
        settled = response.json().get('settled', False)

        logger.debug(f"Status: {status}")
        logger.debug(f"Settled: {settled}")


        pr = invoice['pr']
        decoded_pr = bolt11.decode(pr)

        if settled:
            try:
                # sats_paid = bolt11.decode(pr).amount_msat // 1000
                sats_paid = decoded_pr.amount_msat // 1000

                logger.info("Invoice has been paid! 🎉")
                return sats_paid

            except Exception as e:
                logger.critical("Error decoding the invoice amount!!")
                logger.critical(e)
                return None

            # return True
        else:
            # If it hasn't been settled yet, check if it has expired

            if decoded_pr.has_expired():
                logger.warning("Invoice has expired. ⏰")
                return -1

            logger.info("Invoice has not been settled yet.")
            return None
    else:
        logger.critical("ERROR IN VERIFYING INVOICE PAYMENT STATUS") # log these... I need alerts!
        logger.error(f"Status Code: {response.status_code}, Response Text: {response.text}")
        return None
