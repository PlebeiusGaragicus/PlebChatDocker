# import requests
# from pydantic import BaseModel
# import streamlit as st

# DATABASE_API_PORT = 5101
# DATABASE_API_URL = f"http://localhost:{DATABASE_API_PORT}"

# # MONGO_DETAILS=mongodb://localhost:27017/?replicaSet=rs0



# # Helper function to handle increase user balance
# def increase_user_balance(username, amount):
#     response = requests.put(f"{DATABASE_API_URL}/admin/users/balance/increase", json={"username": username, "amount": amount})
#     if response.status_code == 200:
#         return response.json()
#     else:
#         st.error(f"Failed to increase balance: {response.json().get('detail', 'Unknown error')}")
#         return None

# st.title("Admin Dashboard")

# # Function to fetch all users
# def get_all_users():
#     response = requests.get(f"{DATABASE_API_URL}/admin/users/")
#     if response.status_code == 200:
#         return response.json()
#     else:
#         st.error("Failed to fetch users.")
#         return []

# # Create a user
# st.header("Create User")
# username = st.text_input("Username")
# balance = st.number_input("Initial Balance", min_value=0)
# if st.button("Create User"):
#     response = requests.post(f"{DATABASE_API_URL}/admin/users/", json={"username": username, "balance": balance})
#     if response.status_code == 200:
#         st.success(f"User {username} created successfully!")
#     else:
#         st.error(f"Error: {response.json().get('detail', 'Unknown error')}")




# # Fetch all users and their balances
# st.header("All Users")
# users = get_all_users()
# if users:
#     user_dict = {user["username"]: user["balance"] for user in users}
#     user_list = list(user_dict.keys())
#     st.write(user_dict)


# class DeleteUserRequest(BaseModel):
#     username: str

# st.header("Delete User")
# del_username = st.selectbox("Select User to Delete", user_list)
# if st.button("Delete User"):
#     response = requests.delete(f"{DATABASE_API_URL}/admin/users/", json={"username": del_username})
#     if response.status_code == 200:
#         st.success(f"User {del_username} deleted successfully!")
#     else:
#         st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

# # Get user balance using select box
# st.header("Get User Balance")
# if users:
#     get_username = st.selectbox("Select User", user_list)
#     if st.button("Get Balance"):
#         response = requests.get(f"{DATABASE_API_URL}/balance/", json={"username": get_username})
#         if response.status_code == 200:
#             user_data = response.json()
#             st.info(f"User: {user_data['username']}, Balance: {user_data['balance']}")
#         else:
#             st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

# # Deduct balance using select box
# st.header("Set User Balance")
# if users:
#     deduct_username = st.selectbox("Set a user to adjust", user_list)
#     new_balance = st.number_input("New Balance", min_value=0)
#     if st.button("Set Balance"):
#         response = requests.put(
#             f"{DATABASE_API_URL}/admin/balance/",
#             json={"username": deduct_username, "new_balance": new_balance}
#         )
#         if response.status_code == 200:
#             user_data = response.json()
#             st.info(f"New Balance for {user_data['username']}: {user_data['new_balance']}")
#         else:
#             st.error(f"Error: {response.json().get('detail', 'Unknown error')}")







# # Function to fetch all invoices
# def get_all_invoices():
#     response = requests.get(f"{DATABASE_API_URL}/admin/invoices/")
#     if response.status_code == 200:
#         return response.json()
#     else:
#         st.error("Failed to fetch invoices.")
#         return []

# # Create a new invoice
# st.header("Create Invoice")
# invoice_username = st.text_input("Invoice Username")
# invoice_pr = st.text_input("Invoice PR")
# invoice_amount = st.number_input("Invoice Amount", min_value=0)
# if st.button("Create Invoice"):
#     invoice_data = {
#         "username": invoice_username,
#         "pr": invoice_pr,
#         "routes": [],
#         "status": "pending",  # or 'paid', 'archived'
#         "successAction": {
#             "message": "Thanks, sats received!",
#             "tag": "message"
#         },
#         "verify": "https://getalby.com/lnurlp/turkeybiscuit/verify/xiNZ8HdmD3WzQJWMrhN8yDa7",
#         "amount": invoice_amount,
#         "issued_at": None  # this will be set by the server if left None
#     }
#     response = requests.post(f"{DATABASE_API_URL}/admin/invoices/", json=invoice_data)
#     if response.status_code == 200:
#         st.success("Invoice created successfully!")
#     else:
#         st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

# # # Display all invoices
# # st.header("All Invoices")
# # invoices = get_all_invoices()
# # if invoices:
# #     st.write(invoices)
# #     invoice_dict = {invoice["id"]: invoice for invoice in invoices}  # Updated the key to "_id"
# #     invoice_list = list(invoice_dict.keys())
# #     st.write(invoice_dict)

# #     st.header("Delete Invoice")
# #     del_invoice_id = st.selectbox("Select Invoice to Delete", invoice_list)
# #     if st.button("Delete Invoice"):
# #         response = requests.delete(f"{DATABASE_API_URL}/admin/invoice/{del_invoice_id}/")
# #         if response.status_code == 200:
# #             st.success(f"Invoice {del_invoice_id} deleted successfully!")
# #         else:
# #             st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
# # else:
# #     st.warning("No invoices found.")
# # Display invoices based on selected user
# st.header("All Invoices")
# invoices = get_all_invoices()
# if invoices:
#     st.subheader("Select User to View Invoices")
#     selected_user = st.selectbox("Select User to view invoices", user_list)
    
#     user_invoices = [invoice for invoice in invoices if invoice["username"] == selected_user]
    
#     if user_invoices:
#         # st.write(user_invoices)
#         # invoice_dict = {invoice["id"]: invoice for invoice in user_invoices}
#         # invoice_list = list(invoice_dict.keys())
#         st.write(user_invoices)
#         invoice_ids = [invoice["id"] for invoice in user_invoices]

#         st.header("Delete Invoice")
#         del_invoice_id = st.selectbox("Select Invoice to Delete", invoice_ids)
#         if st.button("Delete Invoice"):
#             response = requests.delete(f"{DATABASE_API_URL}/admin/invoice/{del_invoice_id}/")
#             if response.status_code == 200:
#                 st.success(f"Invoice {del_invoice_id} deleted successfully!")
#             else:
#                 st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
#     else:
#         st.info("No invoices found for the selected user.")
# else:
#     st.warning("No invoices found.")



import requests
from pydantic import BaseModel
import streamlit as st

DATABASE_API_PORT = 5101
DATABASE_API_URL = f"http://localhost:{DATABASE_API_PORT}"

# Helper function to handle increase user balance
def increase_user_balance(username, amount):
    try:
        response = requests.put(f"{DATABASE_API_URL}/admin/users/balance/increase", json={"username": username, "amount": amount})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to increase balance: {e}")
        return None

st.title("Admin Dashboard")

# Function to fetch all users
def get_all_users():
    try:
        response = requests.get(f"{DATABASE_API_URL}/admin/users/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch users: {e}")
        return []

# Create a user
st.header("Create User")
username = st.text_input("Username")
balance = st.number_input("Initial Balance", min_value=0)
if st.button("Create User"):
    try:
        response = requests.post(f"{DATABASE_API_URL}/admin/users/", json={"username": username, "balance": balance})
        response.raise_for_status()
        st.success(f"User {username} created successfully!")
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")

# Fetch all users and their balances
st.header("All Users")
users = get_all_users()
if users:
    user_dict = {user["username"]: user["balance"] for user in users}
    user_list = list(user_dict.keys())
    st.write(user_dict)
else:
    st.error("No users found.")
    quit()

class DeleteUserRequest(BaseModel):
    username: str

st.header("Delete User")
del_username = st.selectbox("Select User to Delete", user_list)
if st.button("Delete User"):
    try:
        response = requests.delete(f"{DATABASE_API_URL}/admin/users/", json={"username": del_username})
        response.raise_for_status()
        st.success(f"User {del_username} deleted successfully!")
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")

# Get user balance using select box
st.header("Get User Balance")
if users:
    get_username = st.selectbox("Select User", user_list)
    if st.button("Get Balance"):
        try:
            response = requests.get(f"{DATABASE_API_URL}/balance/", params={"username": get_username})
            response.raise_for_status()
            user_data = response.json()
            st.info(f"User: {user_data['username']}, Balance: {user_data['balance']}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")

# Deduct balance using select box
st.header("Set User Balance")
if users:
    deduct_username = st.selectbox("Set a user to adjust", user_list)
    new_balance = st.number_input("New Balance", min_value=0)
    if st.button("Set Balance"):
        try:
            response = requests.put(
                f"{DATABASE_API_URL}/admin/balance/",
                json={"username": deduct_username, "new_balance": new_balance}
            )
            response.raise_for_status()
            user_data = response.json()
            st.info(f"New Balance for {user_data['username']}: {user_data['new_balance']}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")

# Function to fetch all invoices
def get_all_invoices():
    try:
        response = requests.get(f"{DATABASE_API_URL}/admin/invoices/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch invoices: {e}")
        return []

# Create a new invoice
st.header("Create Invoice")
invoice_username = st.text_input("Invoice Username")
invoice_pr = st.text_input("Invoice PR")
invoice_amount = st.number_input("Invoice Amount", min_value=0)
if st.button("Create Invoice"):
    invoice_data = {
        "username": invoice_username,
        "pr": invoice_pr,
        "routes": [],
        "status": "pending",  # or 'paid', 'archived'
        "successAction": {
            "message": "Thanks, sats received!",
            "tag": "message"
        },
        "verify": "https://getalby.com/lnurlp/turkeybiscuit/verify/xiNZ8HdmD3WzQJWMrhN8yDa7",
        "amount": invoice_amount,
        "issued_at": None  # this will be set by the server if left None
    }
    try:
        response = requests.post(f"{DATABASE_API_URL}/admin/invoices/", json=invoice_data)
        response.raise_for_status()
        st.success("Invoice created successfully!")
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")

# Display invoices based on selected user
st.header("All Invoices")
invoices = get_all_invoices()
if invoices:
    st.subheader("Select User to View Invoices")
    selected_user = st.selectbox("Select User to view invoices", user_list)
    
    user_invoices = [invoice for invoice in invoices if invoice["username"] == selected_user]
    
    if user_invoices:
        st.write(user_invoices)
        invoice_ids = [invoice["id"] for invoice in user_invoices]

        st.header("Delete Invoice")
        del_invoice_id = st.selectbox("Select Invoice to Delete", invoice_ids)
        if st.button("Delete Invoice"):
            try:
                response = requests.delete(f"{DATABASE_API_URL}/admin/invoice/{del_invoice_id}/")
                response.raise_for_status()
                st.success(f"Invoice {del_invoice_id} deleted successfully!")
            except requests.exceptions.RequestException as e:
                st.error(f"Error: {e}")
    else:
        st.info("No invoices found for the selected user.")
else:
    st.warning("No invoices found.")