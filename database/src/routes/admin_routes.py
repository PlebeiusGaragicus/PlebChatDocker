# from fastapi import APIRouter, HTTPException
# from bson import ObjectId
# from typing import List

# from src.models import User, UserRequest, UsernameRequest, BalanceRequest, Invoice
# from src.database import db
# from src.logger import logger

# router = APIRouter()

# def invoice_helper(invoice) -> dict:
#     logger.warning(invoice)
#     return {
#         "id": str(invoice["_id"]),
#         "username": invoice["username"],
#         "pr": invoice["pr"],
#         # "routes": invoice["routes"],
#         "status": invoice["status"],
#         # "successAction": invoice["successAction"],
#         "verify": invoice["verify"],
#         "amount_sats": invoice["amount"],
#         # "issued_at": invoice["issued_at"]
#     }

# @router.get("/users/", response_model=List[User])
# async def get_all_users():
#     user_collection = db.db.get_collection("users")
#     users = await user_collection.find().to_list(length=None)
#     return users

# @router.post("/users/")
# async def create_user(user_request: UserRequest):
#     user_collection = db.db.get_collection("users")
#     user = await user_collection.find_one({"username": user_request.username})
#     if user:
#         raise HTTPException(status_code=400, detail="User already exists")
#     user = User(**user_request.dict())
#     await user_collection.insert_one(user.dict())
#     return user

# @router.delete("/users/")
# async def delete_user(request: UsernameRequest):
#     username = request.username
#     user_collection = db.db.get_collection("users")
#     result = await user_collection.delete_one({"username": username})
#     if result.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="User not found")
#     return {"message": f"User {username} deleted successfully"}

# @router.put("/balance/")
# async def set_user_balance(request: BalanceRequest):
#     username = request.username
#     new_balance = request.new_balance
#     user_collection = db.db.get_collection("users")
#     user = await user_collection.find_one({"username": username})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     await user_collection.update_one({"username": username}, {"$set": {"balance": new_balance}})
    
#     return {"username": username, "new_balance": new_balance}

# @router.get("/invoices/", response_model=List[dict])
# async def get_all_invoices():
#     invoices_collection = db.db.get_collection("invoices")
#     invoices = await invoices_collection.find().to_list(length=None)
#     invoices_with_id = [invoice_helper(invoice) for invoice in invoices]
#     for invoice in invoices_with_id:
#         logger.info(f"invoice: {invoice}")
#     # logger.info(f"Invoices being returned: {invoices_with_id}")
#     return invoices_with_id

# @router.post("/invoices/")
# async def create_invoice(invoice: Invoice):
#     invoices_collection = db.db.get_collection("invoices")
#     existing_invoice = await invoices_collection.find_one(
#         {"pr": invoice.pr}
#     )
#     if existing_invoice:
#         raise HTTPException(status_code=400, detail="Invoice already exists")
#     insert_result = await invoices_collection.insert_one(invoice.dict())
#     new_invoice_id = insert_result.inserted_id
#     new_invoice_dict = invoice.dict()
#     new_invoice_dict["_id"] = new_invoice_id
#     return invoice_helper(new_invoice_dict)

# @router.delete("/invoice/{invoice_id}/")
# async def delete_invoice(invoice_id: str):
#     invoices_collection = db.db.get_collection("invoices")
#     if not ObjectId.is_valid(invoice_id):
#         raise HTTPException(status_code=400, detail="Invalid invoice ID")
#     result = await invoices_collection.delete_one({"_id": ObjectId(invoice_id)})
#     if result.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="Invoice not found")
#     return {"message": f"Invoice {invoice_id} deleted successfully"}