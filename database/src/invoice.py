import logging
logger = logging.getLogger(__name__)

import time
import json
import requests

from bolt11 import decode


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

    print(invoice)
    verify_url = invoice['verify']

    response = requests.get(verify_url)
    if response.status_code == 200:
        status = response.json().get('status')
        settled = response.json().get('settled', False)

        print(f"Status: {status}")
        print(f"Settled: {settled}")

        if settled:
            print("Invoice has been paid! 🎉")
            return True
        else:
            print("Invoice has not been settled yet.")
            return False
    else:
        print("ERROR IN VERIFYING INVOICE PAYMENT STATUS")
        print(response.status_code, response.text)
        return False
    




TOKENS_PER_SAT = 10

def create_invoice(amount: int = 100, payee_address: str = "turkeybiscuit@getalby.com"):
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

    # ln_address = "turkeybiscuit@getalby.com"
    url = "https://api.getalby.com/lnurl/generate-invoice"
    params = {
        "ln": payee_address,
        "amount": amount * 1000,  # in millisats
        "comment": f"Purchased {amount * TOKENS_PER_SAT} tokens"
    }

    response = requests.get(url, params=params)

    print(f"Creating invoice for {amount} sats")
    if response.status_code == 200:
        # Successfully created the invoice
        invoice_details = response.json()
        invoice_details['amount'] = amount  # Adding the amount to the invoice details
        print("Invoice created!")
        print(json.dumps(invoice_details, indent=4))  # Pretty print the invoice details
        return invoice_details
    else:
        # Failed to create the invoice
        print(response)
        error_message = f"Failed to create invoice: {response.status_code} {response.text}"
        print(error_message)
        return {"error": error_message}

