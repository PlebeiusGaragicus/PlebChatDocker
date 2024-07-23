import logging
logger = logging.getLogger(__name__)

from typing import Union
import requests

DATABASE_API_PORT = 5101
DATABASE_API_URL = f"http://localhost"

API = "http://localhost:5101"


DEFAULT_INVOICE_AMOUNT = 100


class UserNotRegistered(Exception):
    pass



def get_user_balance(lud16: str) -> Union[int, None]:
    """
        :param lud16: A user's lightning address - should be unique for every user

        Returns the balance of a given user LUD16
        Returns None if user is not found in database
    """

    logger.debug(f"Checking balance on LUD16: {lud16}")
    # Note: Using params instead of json to send username as a query parameter
    response = requests.get(f"{DATABASE_API_URL}:{DATABASE_API_PORT}/balance/", params={"username": lud16})

    try:
        response.raise_for_status()  # Raises HTTPError for bad HTTP responses
        user_data = response.json()
        logger.debug(f"This user has a balance of: {user_data['balance']}")
        return user_data['balance']
    except requests.exceptions.HTTPError as e:
        print("*" * 80)
        print(f"Error: {e}")
        print(response.text)
        print("*" * 80)

        if response.status_code == 404 and response.json().get("detail") == "User not found":
            # raise UserNotRegistered(f"User not registered: {lud16}")
            # return 0 #TODO: nope, this is a bad idea... we should raise the exception and handle it in the app.py
            return None
        else:
            # TODO: TEST THIS FLOW
            raise Exception(f"Error checking balance: {response.status_code} {response.text}")



def assure_positive_balance(lud16: str) -> bool:
    """
        Return True if provided user lud16 has a positive balance in the user database
        Return False otherwise, including if user is not registered.
    """
    bal = get_user_balance(lud16)

    if bal is None:
        return False
    else:
        return bool(bal > 0)


# def get_invoice(lud16: str, sats: int = DEFAULT_INVOICE_AMOUNT):
def get_invoice(lud16: str, sats: int):
    response = requests.get(f"{DATABASE_API_URL}:{DATABASE_API_PORT}/invoice/", json={"username": lud16, "sats": sats})

    if response.status_code == 200:
        invoice = response.json()
        if 'error' in invoice:
            raise Exception(f"Error creating invoice: {invoice['error']}")
        return invoice
    else:
        # TODO: log and track these errors!!!
        raise Exception(f"Error getting invoice: {response.status_code} {response.text}")





def deduct_with_usage(lud16, chat_id, amount):
    if not lud16:
        raise ValueError("User's lud16 is not specified")

    bm = BalanceManager()
    return bm.deduct_balance(lud16, chat_id, amount)





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

# def deduct(lud16, chat_id, amount):
    # if not lud16:
    #     raise ValueError("User's lud16 is not specified")

    # bm = BalanceManager()
    # return bm.deduct_balance(lud16, chat_id, amount)
