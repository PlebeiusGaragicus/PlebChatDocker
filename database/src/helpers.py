import logging
logger = logging.getLogger(__name__)


from fastapi import HTTPException, status



from src.database import db
import src.invoice as invoice_utils


async def update_user_balance_for_paid_invoices(username: str):
    user_collection = db.db.get_collection("users")
    invoices_collection = db.db.get_collection("invoices")

    # Check if there are any pending invoices
    pending_invoices = await fetch_all_pending_invoices(username)
    total_amount = 0  # To accumulate all paid invoices' amounts

    for invoice in pending_invoices:
        is_paid = invoice_utils.check_for_payment(invoice)
        if is_paid:
            total_amount += invoice["amount"]
            await invoices_collection.update_one(
                {"_id": invoice["_id"]},
                {"$set": {"status": "archived"}}
            )
    
    if total_amount > 0:
        user = await user_collection.find_one({"username": username})
        if not user:
            # User not found, create a new one with the accumulated balance
            user = {"username": username, "balance": total_amount}
            await user_collection.insert_one(user)
        else:
            # Update the user's balance
            new_balance = user["balance"] + total_amount
            await user_collection.update_one(
                {"username": username},
                {"$set": {"balance": new_balance}}
            )

    # Fetch and return user after potential insertion/update
    user = await user_collection.find_one({"username": username})
    if not user:
        logger.debug(f"User '{username}' not found even after insertion.")
        raise HTTPException(status_code=404, detail="User not found")

    return user

async def fetch_all_pending_invoices(username: str):
    invoices_collection = db.db.get_collection("invoices")
    return await invoices_collection.find({"username": username, "status": "pending"}).to_list(length=None)

async def check_and_update_invoice_status(username: str):
    invoices_collection = db.db.get_collection("invoices")
    user_collection = db.db.get_collection("users")

    pending_invoices = await fetch_all_pending_invoices(username)
    total_amount = 0  # To accumulate all paid invoices' amounts

    for invoice in pending_invoices:
        is_paid = invoice_utils.check_for_payment(invoice)
        if is_paid:
            total_amount += invoice["amount"]
            await invoices_collection.update_one(
                {"_id": invoice["_id"]},
                {"$set": {"status": "archived"}}
            )
    
    if total_amount > 0:
        user = await user_collection.find_one({"username": username})
        if not user:
            # User not found, create a new one with the accumulated balance
            user = {"username": username, "balance": total_amount}
            await user_collection.insert_one(user)
        else:
            # Update the user's balance
            new_balance = user["balance"] + total_amount
            await user_collection.update_one(
                {"username": username},
                {"$set": {"balance": new_balance}}
            )
        return {"message": f"User {username} balance updated by {total_amount}"} 
    
    return {}
