import dotenv
dotenv.load_dotenv()

# import logging
from src.logger import setup_logging, logger
setup_logging()
# import src.logger
# logger = logging.getLogger(__name__)

import os
from datetime import datetime

# LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

# logging_config = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "standard": {
#             "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
#         },
#     },
#     "handlers": {
#         "default": {
#             "level": LOG_LEVEL,
#             "formatter": "standard",
#             "class": "logging.StreamHandler",
#             "stream": "ext://sys.stdout",
#         },
#     },
#     "loggers": {
#         "": {
#             "handlers": ["default"],
#             "level": LOG_LEVEL,
#             "propagate": True,
#         },
#     }
# }

# import logging.config

# # Load the logging configuration
# logging.config.dictConfig(logging_config)

# # Get the root logger
# logger = logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from bson import ObjectId
from typing import List

from src.models import (
    User, Transaction, Invoice, UsernameRequest, SuccessAction, TransactionRequest, BalanceRequest, UserRequest, Invoice
)

from src.database import db, connect_to_mongo, close_mongo_connection
import src.invoice as invoice_utils
import src.helpers as helpers




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

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Connecting to MongoDB...")
    await connect_to_mongo()
    yield
    logger.info("Closing MongoDB connection...")
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:5522",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response



# @app.get("/balance/")
# async def get_balance(request: Request):
#     logger.debug("get_balance endpoint called")
#     logger.debug(f"Request: {request}")
#     data = await request.json()
#     username = data['username']
#     user_collection = db.db.get_collection("users")
#     user = await user_collection.find_one({"username": username})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return {"username": username, "balance": user["balance"]}


@app.get("/balance/")
async def get_balance(username: str):
    logger.debug("get_balance endpoint called")
    logger.debug(f"Request: {username}")

    user = await helpers.update_user_balance_for_paid_invoices(username)
    return {"username": username, "balance": user["balance"]}




@app.get("/invoice/")
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






@app.put("/tx/")
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











############################################################
#NOTE: ADMIN TESTING ENDPOINTS!
############################################################
@app.get("/admin/users/", response_model=List[User])
async def get_all_users():
    user_collection = db.db.get_collection("users")
    users = await user_collection.find().to_list(length=None)
    return users

@app.post("/admin/users/")
async def create_user(user_request: UserRequest):
    user_collection = db.db.get_collection("users")
    user = await user_collection.find_one({"username": user_request.username})
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(**user_request.dict())
    await user_collection.insert_one(user.dict())
    return user

@app.delete("/admin/users/")
async def delete_user(request: UsernameRequest):
    username = request.username
    user_collection = db.db.get_collection("users")
    result = await user_collection.delete_one({"username": username})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {username} deleted successfully"}


@app.put("/admin/balance/")
async def set_user_balance(request: BalanceRequest):
    username = request.username
    new_balance = request.new_balance
    user_collection = db.db.get_collection("users")
    user = await user_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await user_collection.update_one({"username": username}, {"$set": {"balance": new_balance}})
    
    return {"username": username, "new_balance": new_balance}




@app.get("/admin/invoices/", response_model=List[dict])
async def get_all_invoices():
    invoices_collection = db.db.get_collection("invoices")
    invoices = await invoices_collection.find().to_list(length=None)
    invoices_with_id = [invoice_helper(invoice) for invoice in invoices]
    logger.info(f"Invoices being returned: {invoices_with_id}")  # Add logging
    return invoices_with_id


@app.post("/admin/invoices/")
async def create_invoice(invoice: Invoice):
    invoices_collection = db.db.get_collection("invoices")
    existing_invoice = await invoices_collection.find_one(
        {"pr": invoice.pr}
    )
    if existing_invoice:
        raise HTTPException(status_code=400, detail="Invoice already exists")
    insert_result = await invoices_collection.insert_one(invoice.dict())
    new_invoice_id = insert_result.inserted_id
    new_invoice_dict = invoice.dict()
    new_invoice_dict["_id"] = new_invoice_id
    ret = invoice_helper(new_invoice_dict)
    print("*"*50)
    print(ret)
    return ret


@app.delete("/admin/invoice/{invoice_id}/")
async def delete_invoice(invoice_id: str):
    invoices_collection = db.db.get_collection("invoices")
    if not ObjectId.is_valid(invoice_id):
        raise HTTPException(status_code=400, detail="Invalid invoice ID")
    result = await invoices_collection.delete_one({"_id": ObjectId(invoice_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"message": f"Invoice {invoice_id} deleted successfully"}







@app.get("/health")
def read_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, "path"):
            routes.append(route.path)
    return {"routes": routes}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5101)
