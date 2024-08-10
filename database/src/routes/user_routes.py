from fastapi import APIRouter, HTTPException, status
from datetime import datetime

from src.logger import logger
from src.database import db
from src.models import UsageDeducation, UsageRecord, InvoiceRequest, UsageRequest
from src.payment import return_user_balance, create_invoice, poll_pending_invoices, get_single_pending_invoice

router = APIRouter()


@router.get("/balance/")
async def get_balance(username: str):
    logger.debug(f">>> /balance/\tRequest: {username}")

    # Check for pending invoices and credit user if paid
    await poll_pending_invoices(username)

    balance = await return_user_balance(username)
    return {"balance": balance}




@router.get("/invoice/")
async def get_invoice(request: InvoiceRequest):
    logger.debug(">>> /invoice/")
    logger.debug(f"Request: {request}")

    username: str = request.username
    # tokens_requested: int = request.tokens_requested

    # This can be cleaned up... if poll_pending_invoices returns a pending invoice, return that.
    # It would need to sort by the most recent invoice, though... or maybe not? becuase we fixed the bug?
    await poll_pending_invoices(username)

    pending_invoice = await get_single_pending_invoice(username)
    if pending_invoice:
        logger.debug(f">>> /invoice/ returning pending invoice: {pending_invoice}")
        return pending_invoice
    else:
        logger.debug(f">>> /invoice/ creating new invoice")
        return await create_invoice(username=username)





@router.put("/tx/")
async def deduct_balance(request: UsageDeducation):
    """ NOTE: This tracks user token usage and deducts the token from the user's account balance. """

    logger.debug("deduct_balance endpoint called")
    logger.debug(f"Request: {request}")

    username = request.username
    thread_id = request.thread_id
    tokens_used = request.tokens_used

    user_collection = db.db.get_collection("users")
    user = await user_collection.find_one({"username": username})

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user["balance"] + tokens_used < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")

    new_balance = user["balance"] - tokens_used  # `amount` is expected to be negative for deduction
    await user_collection.update_one(
        {"username": username},
        {"$set": {"balance": new_balance}}
    )

    # Optional: log the transaction in a transactions collection
    tx_collection = db.db.get_collection("transactions")
    new_tx = UsageRecord(
        username=username,
        thread_id=thread_id,
        tokens_used=tokens_used,
        timestamp=datetime.utcnow()
    )
    await tx_collection.insert_one(new_tx.dict())

    return {"username": username, "new_balance": new_balance}



@router.get("/tx/")
async def get_transactions(request: UsageRequest):
    logger.debug(f">>> /tx/\tRequest: {request}")

    username = request.username
    thread_id = request.thread_id


    tx_collection = db.db.get_collection("transactions")
    transactions = await tx_collection.find({"username": username, "thread_id": thread_id}).to_list(length=None)
    logger.debug(f"Transactions: {transactions}")

    thread_usage = sum(t['tokens_used'] for t in transactions)

    # return transactions
    return int(thread_usage)