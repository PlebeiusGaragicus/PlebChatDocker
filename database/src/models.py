from pydantic import BaseModel, Field
from datetime import datetime





class UserRequest(BaseModel):
    username: str
    balance: int

class TransactionRequest(BaseModel):
    username: str
    chat_id: str
    amount: int

class BalanceRequest(BaseModel):
    username: str
    new_balance: int



class User(BaseModel):
    username: str = Field(...)
    balance: float = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "balance": 1000.0,
            }
        }

class UsernameRequest(BaseModel):
    username: str


class Transaction(BaseModel):
    username: str = Field(...)
    chat_id: str = Field(...)
    amount: float = Field(...)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "chat_id": "chat_12345",
                "amount": -5.0,
                "timestamp": "2023-10-10T00:00:00Z"
            }
        }

class SuccessAction(BaseModel):
    message: str
    tag: str


class TransactionRequest(BaseModel):
    username: str
    chat_id: str
    amount: float

class Transaction(BaseModel):
    username: str = Field(...)
    chat_id: str = Field(...)
    amount: float = Field(...)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Invoice(BaseModel):
    username: str = Field(...)
    pr: str = Field(...)
    routes: list = Field(default_factory=list)
    status: str = Field(..., pattern="^(pending|paid|archived)$") # Change 'regex' to 'pattern'
    successAction: SuccessAction = Field(...)
    verify: str = Field(...)
    amount: float = Field(...)
    issued_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "pr": "lnbc1u1pnfc2utpp52pgctfl3fhslf93u37yq3ha9aleh8vqpgcalqduqtfs8shp5flf38893foah3wq4c2njau2jc9prswd0q43t5afjl98389af6h6pscqzzsxqyz5vqsp5897mqnprgwmchgdd4l2zx9u5szuvgrqkw73n7kaqr00pw73fgqls9qxpqfl3luaf3rv7h6zfxxcu29femukgrdud5hq3ljpf9hc7g7vajjgsysevf5cc5y3utanx2fjlfjl839fhlaucqpp0vfw",
                "routes": [],
                "status": "pending",
                "successAction": {
                    "message": "Thanks, sats received!",
                    "tag": "message"
                },
                "verify": "https://getalby.com/lnurlp/turkeyfuckers/verify/xiNZ8HdMd4wZqOWmRHN8yDa7",
                "amount": 100.0,
                "issued_at": "2024-01-10T00:00:00Z"
            }
        }
