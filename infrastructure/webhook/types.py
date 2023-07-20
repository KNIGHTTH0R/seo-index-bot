from typing import Dict, Any, Optional
from typing import List

from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: float
    count: int


class WayforpayRequestData(BaseModel):
    merchantAccount: str
    orderReference: str
    merchantSignature: str
    amount: float
    currency: str
    authCode: str
    email: Optional[str] = None
    phone: Optional[str] = None
    createdDate: int
    processingDate: int
    cardPan: str
    cardType: Optional[str] = None
    issuerBankCountry: Optional[str] = None
    issuerBankName: Optional[str] = None
    recToken: str
    transactionStatus: str
    reason: str
    reasonCode: int
    fee: float
    paymentSystem: str
    acquirerBankName: str
    cardProduct: str = None
    clientName: Optional[str] = None
    products: List[Product]


