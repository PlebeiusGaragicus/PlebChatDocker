from fastapi import APIRouter, HTTPException, status
from datetime import datetime

from src.logger import logger
from src.models import UsernameRequest, TransactionRequest
from src.database import db
import src.helpers as helpers
import src.invoice as invoice_utils

from src.models import Transaction, Invoice


router = APIRouter()


def transaction_helper(transaction) -> dict:
    return {
        "id": str(transaction["_id"]),
        "username": transaction["username"],
        "chat_id": transaction["chat_id"],
        "amount": transaction["amount"],
        "timestamp": transaction["timestamp"]
    }

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


@router.get("/balance/")
async def get_balance(username: str):
    logger.debug("get_balance endpoint called")
    logger.debug(f"Request: {username}")

    user = await helpers.update_user_balance_for_paid_invoices(username)
    return {"username": username, "balance": user["balance"]}




@router.get("/invoice/")
async def get_invoice(request: UsernameRequest):
    logger.debug("get_invoice endpoint called")
    logger.debug(f"Request: {request}")

    username = request.username
    result = await helpers.check_and_update_invoice_status(username)

    if result:
        return result

    # Create New Invoice
    new_invoice_details = invoice_utils.create_invoice(
        amount=100
    )  # Check the amount parameter, you can modify it as needed
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




