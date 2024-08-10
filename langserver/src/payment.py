import logging
logger = logging.getLogger(__name__)

from typing import Optional
import requests

DATABASE_API_PORT = 5101
DATABASE_API_URL = f"http://localhost"

API = "http://localhost:5101"


# sats denominated
# DEFAULT_INVOICE_AMOUNT = 500 # sats
DEFAULT_INVOICE_AMOUNT = 100 # sats
MINIMUM_INVOICE_AMOUNT = 25
MAXIMUM_INVOICE_AMOUNT = 10_000

DEFAULT_INVOICE_AMOUNT = 100



def get_user_balance(lud16: str) -> Optional[None]:
    """
        :param lud16: A user's lightning address - should be unique for every user

        Returns the integer balance of a given user LUD16
        Returns None if user is not found in database
    """

    response = requests.get(f"{DATABASE_API_URL}:{DATABASE_API_PORT}/balance/", params={"username": lud16})
    try:
        # Raises HTTPError for bad HTTP responses
        response.raise_for_status()
        balance = response.json()
        logger.debug(f"This user has a balance of: {balance}")
        return balance

    except requests.exceptions.HTTPError as e:
        if response.status_code == 404 and response.json().get("detail") == "User not found":
            return None
        else:
            raise Exception(f"Error checking balance: {response.status_code} {response.text}")




def get_invoice(lud16: str):
    # response = requests.get(f"{DATABASE_API_URL}:{DATABASE_API_PORT}/invoice/", json={"username": lud16, "tokens_requested": tokens_requested})
    response = requests.get(f"{DATABASE_API_URL}:{DATABASE_API_PORT}/invoice/", json={"username": lud16})

    if response.status_code == 200:
        invoice = response.json()
        if 'error' in invoice:
            logger.error(f"Error creating invoice: {invoice['error']}")
            raise Exception(f"Error creating invoice: {invoice['error']}")

        logger.debug(f"get_invoice returning: {invoice}")
        return invoice
    else:
        # TODO: log and track these errors!!!
        logger.critical(f"Error getting invoice: {response.status_code} {response.text}")
        raise Exception(f"Error getting invoice: {response.status_code} {response.text}")


def get_usage(username: str, thread_id: str):
    response = requests.get(f"{DATABASE_API_URL}:{DATABASE_API_PORT}/tx/", json={"username": username, "thread_id": thread_id})

    if response.status_code == 200:
        usage = response.json()
        logger.debug(f"get_usage returning: {usage}")
        return usage
    else:
        logger.critical(f"Error getting usage: {response.status_code} {response.text}")
        return None
