# create validation classes with pydantic

from typing import Optional, Any

from pydantic import BaseModel


class MinAmount(BaseModel):
    currency_from: str
    currency_to: str
    min_amount: float
    fiat_equivalent: Optional[float]


class EstimatedPrice(BaseModel):
    currency_from: str
    amount_from: float
    currency_to: str
    estimated_amount: float


class PaymentStatus:
    WAITING = "waiting"
    CONFIRMING = "confirming"
    CONFIRMED = "confirmed"
    SENDING = "sending"
    PARTIALLY_PAID = "partially_paid"
    FINISHED = "finished"
    FAILED = "failed"
    REFUNDED = "refunded"
    EXPIRED = "expired"


class Payment(BaseModel):
    payment_id: str
    payment_status: str
    pay_address: str
    price_amount: float
    price_currency: str
    pay_amount: float
    pay_currency: str
    order_id: Optional[str]
    order_description: Optional[str]
    ipn_callback_url: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    purchase_id: Optional[str]
    amount_received: Optional[float]
    payin_extra_id: Optional[str]
    smart_contract: Optional[str]
    network: Optional[str]
    network_precision: Optional[int]
    time_limit: Optional[Any]
    burning_percent: Optional[int]
    expiration_estimate_date: Optional[str]


class PaymentUpdate(BaseModel):
    payment_id: int
    invoice_id: Optional[int]
    payment_status: str
    pay_address: str
    price_amount: float
    price_currency: str
    pay_amount: float
    actually_paid: float
    actually_paid_in_fiat: Optional[float] = None
    pay_currency: str
    order_id: Optional[str] = None
    order_description: Optional[str] = None
    purchase_id: str
    created_at: str = None
    updated_at: str
    outcome_amount: float
    outcome_currency: str
