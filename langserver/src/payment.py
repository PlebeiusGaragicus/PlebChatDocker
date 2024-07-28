import logging
logger = logging.getLogger(__name__)

from typing import Optional
import requests

DATABASE_API_PORT = 5101
DATABASE_API_URL = f"http://localhost"

API = "http://localhost:5101"


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




def get_invoice(lud16: str, sats: int):
    response = requests.get(f"{DATABASE_API_URL}:{DATABASE_API_PORT}/invoice/", json={"username": lud16, "invoice_amount": sats})

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








class BalanceManager:
    def __init__(self, api_url=API):
        self.api_url = api_url
        self.session = requests.Session()  # Persist the connection

    def __del__(self):
        self.session.close()  # Ensure the session is closed when the instance is destroyed

    def check_balance(self, username):
        try:
            response = self.session.get(f"{self.api_url}/balance/", params={"username": username})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to get balance: {e}")

    def deduct_balance(self, username, chat_id, amount):
        try:
            response = self.session.put(
                f"{self.api_url}/tx/",
                json={"username": username, "chat_id": chat_id, "amount": -amount}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to deduct balance: {e}")


def deduct_with_usage(lud16, chat_id, amount):
    if not lud16:
        raise ValueError("User's lud16 is not specified")

    bm = BalanceManager()
    return bm.deduct_balance(lud16, chat_id, amount)
