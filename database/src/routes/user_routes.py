import os
from fastapi import APIRouter, HTTPException, status
from datetime import datetime

from src.logger import logger
from src.models import UsernameRequest, TransactionRequest, InvoiceRequest
from src.database import db
import src.helpers as helpers
import src.invoice as invoice_utils

from src.models import Transaction, Invoice
# from src.helpers import transaction_helper, invoice_helper

router = APIRouter()




def invoice_helper(invoice) -> dict:
    return {
        "id": str(invoice["_id"]),
        "username": invoice["username"],
        "pr": invoice["pr"],
        "routes": invoice["routes"],
        "status": invoice["status"],
        "successAction": invoice["successAction"],
        "verify": invoice["verify"],
        "amount": invoice["amount"],
        "issued_at": invoice["issued_at"]
    }



def transaction_helper(transaction) -> dict:
    return {
        "id": str(transaction["_id"]),
        "username": transaction["username"],
        "chat_id": transaction["chat_id"],
        "amount": transaction["amount"],
        "timestamp": transaction["timestamp"]
    }







@router.get("/balance/")
async def get_balance(username: str):
    logger.debug(f"/balance/\tRequest: {username}")

    # user = await helpers.update_user_balance_for_paid_invoices(username)
    # return {"username": username, "balance": user["balance"]}
    balance = await helpers.return_user_balance(username)
    return {"balance": balance}





@router.get("/invoice/")
async def get_invoice(request: InvoiceRequest):
    logger.debug("get_invoice endpoint called")
    logger.debug(f"Request: {request}")


    # test_invoice = Invoice(
    #     username=request.username,
    #     pr="lnbc1u1pnflm39pp5jdd4kf6g....",
    #     routes=[],
    #     status="pending",
    #     successAction={"message": "Thanks, sats received!","tag": "message"},
    #     verify="https://getalby.com/lnurlp/turkeybiscuit/verify/1mosQtN8GHDJup9B2m6HJE4w",
    #     amount=request.invoice_amount,
    # ).dict()
    # test_invoice['_id'] = "1234567890"
    # return invoice_helper(invoice=test_invoice)


################################################################
#### REFACTOR HERE #######




    username: str = request.username
    amount: int = request.invoice_amount
    # result = await helpers.check_and_update_invoice_status(username)

    # if result:
    #     return result
    
    # existing_invoice = await invoices_collection.find_one({"username": username, "status": "pending"})
    # if existing_invoice:
    #     return invoice_helper(existing_invoice)










    raise NotImplementedError("This endpoint is not implemented yet")

    # Create New Invoice
    # TODO: Check the amount parameter, you can modify it as needed
    payee = os.getenv('PAYEE_LUD16')
    if not payee:
        logger.critical("Payee address not found - This server is not configured correctly!!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payee address not found - This server is not configured correctly!!"
        )

    new_invoice_details = invoice_utils.create_invoice(
        amount=amount,
        payee_address=payee
    )
    if "error" in new_invoice_details:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=new_invoice_details["error"],
        )

    new_invoice = Invoice(
        username=username,
        pr=new_invoice_details.get("invoice", {}).get("pr"),
        routes=new_invoice_details.get("invoice", {}).get("routes", []),
        status="pending",
        successAction=new_invoice_details.get("invoice", {}).get("successAction", {}),
        verify=new_invoice_details.get("invoice", {}).get("verify"),
        amount=new_invoice_details.get("amount"),
    )

    invoices_collection = db.db.get_collection("invoices")
    insert_result = await invoices_collection.insert_one(new_invoice.dict())
    new_invoice_id = insert_result.inserted_id
    new_invoice_dict = new_invoice.dict()
    new_invoice_dict["_id"] = new_invoice_id

    return invoice_helper(new_invoice_dict)






@router.put("/tx/")
async def deduct_balance(request: TransactionRequest):
    """
        NOTE: This tracks user token usage
        #TODO: refactor
    """
    logger.debug("deduct_balance endpoint called")
    logger.debug(f"Request: {request}")

    username = request.username
    chat_id = request.chat_id
    amount = request.amount

    user_collection = db.db.get_collection("users")
    user = await user_collection.find_one({"username": username})

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user["balance"] + amount < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")

    new_balance = user["balance"] + amount  # `amount` is expected to be negative for deduction
    await user_collection.update_one(
        {"username": username},
        {"$set": {"balance": new_balance}}
    )

    # Optional: log the transaction in a transactions collection
    tx_collection = db.db.get_collection("transactions")
    new_tx = Transaction(
        username=username,
        chat_id=chat_id,
        amount=amount,
        timestamp=datetime.utcnow()
    )
    await tx_collection.insert_one(new_tx.dict())

    return {"username": username, "new_balance": new_balance}




