import requests

DATABASE_API_PORT = 5101
DATABASE_API_URL = f"http://localhost"

API = "http://localhost:5101"


class UserNotRegistered(Exception):
    pass


#TODO: THESE TWO SHOULD BE COMBINED INTO ONE FUNCTION!!!!!
def assure_positive_balance(lud16: str) -> bool:
    bal = _check_balance(lud16)

    if bal is None:
        return False
    else:
        return bool(bal > 0)

def get_invoice(lud16: str, sats: int = 100):
    response = requests.get(f"{DATABASE_API_URL}:{DATABASE_API_PORT}/invoice/", json={"username": lud16, "sats": sats})

    if response.status_code == 200:
        invoice = response.json()
        if 'error' in invoice:
            raise Exception(f"Error creating invoice: {invoice['error']}")
        return invoice
    else:
        # TODO: log and track these errors!!!
        raise Exception(f"Error getting invoice: {response.status_code} {response.text}")

def show_user_balance(lud16):
    bal = _check_balance(lud16)

    if bal is not None:
        yield f"User: {lud16}, Balance: {bal}"
    else:
        return "Error: Unknown error" # TODO: log and track these errors!!!


def get_balance(lud16):
    bal = _check_balance(lud16)

    if bal is not None:
        return bal
    else:
        raise Exception("Error: error in get_balance()") # TODO: log and track these errors!!!


def _check_balance(lud16):
    # Note: Using params instead of json to send username as a query parameter
    response = requests.get(f"{DATABASE_API_URL}:{DATABASE_API_PORT}/balance/", params={"username": lud16})

    try:
        response.raise_for_status()  # Raises HTTPError for bad HTTP responses
        user_data = response.json()
        return user_data['balance']
    except requests.exceptions.HTTPError as e:
        print("*" * 80)
        print(f"Error: {e}")
        print(response.text)
        print("*" * 80)

        if response.status_code == 404 and response.json().get("detail") == "User not found":
            # raise UserNotRegistered(f"User not registered: {lud16}")
            return 0 #TODO: nope, this is a bad idea... we should raise the exception and handle it in the app.py
        else:
            # TODO: TEST THIS FLOW
            raise Exception(f"Error checking balance: {response.status_code} {response.text}")







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

def deduct(lud16, chat_id, amount):
    if not lud16:
        raise ValueError("User's lud16 is not specified")

    bm = BalanceManager()
    return bm.deduct_balance(lud16, chat_id, amount)

# Example Usage:
# bm = BalanceManager()
# print(bm.check_balance("some_username"))
# print(bm.deduct_balance("some_username", "chat_id_123", 50))
