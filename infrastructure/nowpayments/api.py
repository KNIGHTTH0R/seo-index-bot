import logging
from urllib.parse import urljoin

import aiohttp

from infrastructure.nowpayments.exceptions import APINotAvailable
from infrastructure.nowpayments.types import (
    MinAmount,
    EstimatedPrice,
    Payment,
    PaymentUpdate,
)


class NowPaymentsAPI:
    def __init__(self, api_key):
        # Set up a request's session for interacting with the API.
        self.session = aiohttp.ClientSession()
        self.api_endpoint = "https://api.nowpayments.io/v1/"
        self.api_key = api_key
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-type": "application/json; charset=utf-8",
            "Accept": "application/json ",
        }

    async def _post(self, *args, **kwargs):
        return await self._request("post", *args, **kwargs)

    async def _get(self, *args, **kwargs):
        return await self._request("get", *args, **kwargs)

    async def _request(self, method, *relative_path_parts, **kwargs):
        parts = "/".join(relative_path_parts)

        uri = urljoin(self.api_endpoint, parts)
        async with getattr(self.session, method)(
            uri, verify_ssl=True, headers=self.headers, **kwargs
        ) as resp:
            print(uri, kwargs)
            try:
                result = await resp.json()
            except Exception as e:
                logging.exception(e)
                return await resp.text()
            else:
                return result

    async def get_api_status(self):
        result = await self._get("status")
        if result.get("message") != "OK":
            raise APINotAvailable()
        return True

    async def get_min_amount(self, currency_to: str, currency_from: str = "usd"):
        payload = [
            ("currency_from", currency_from),
            ("currency_to", currency_to),
            ("fiat_equivalent", "usd"),
        ]
        result = await self._get("min-amount", params=payload)

        return MinAmount(**result)

    async def get_estimated_price(
        self, currency_to: str, currency_from: str = "usd", amount: float = 1
    ):
        payload = [
            ("currency_from", currency_from),
            ("currency_to", currency_to),
            ("amount", amount),
        ]
        result = await self._get("estimate", params=payload)
        return EstimatedPrice(**result)

    async def create_payment(
        self,
        price_amount: float,
        price_currency: str,
        pay_currency: str,
        order_id: str = None,
        order_description: str = None,
        ipn_callback_url: str = None,
        pay_amount: float = None,
        purchase_id: str = None,
        payout_address: str = None,
        payout_currency: str = None,
        payout_extra_id: str = None,
        fixed_rate: bool = False,
        is_fee_paid_by_user: bool = True,
    ):
        """
        :param price_amount: (required) - the fiat equivalent of the price to be paid in crypto.
        If the pay_amount parameter is left empty, our system will automatically convert this fiat price into its
        crypto equivalent. Please note that this does not enable fiat payments, only provides a fiat price for yours
        and the customer’s convenience and information. NOTE: Some of the assets
        (KISHU, NWC, FTT, CHR, XYM, SRK, KLV, SUPER, OM, XCUR, NOW, SHIB, SAND, MATIC, CTSI, MANA, FRONT, FTM,
        DAO, LGCY), have a maximum price amount of ~$2000.
        :param price_currency: (required) - the fiat currency in which the price_amount is specified (usd, eur, etc).
        :param pay_amount: (optional) - the amount that users have to pay for the order stated in crypto. You can
        either specify it yourself, or we will automatically convert the amount you indicated in price_amount.
        :param pay_currency: (required) - the cryptocurrency in which the pay_amount is specified (btc, eth, etc).
        NOTE: some of the currencies require a Memo, Destination Tag, etc., to complete a payment
        (AVA, EOS, BNBMAINNET, XLM, XRP). This is unique for each payment.
        This ID is received in “payin_extra_id” parameter of the response. Payments made without "payin_extra_id"
        cannot be detected automatically.
        :param ipn_callback_url: (optional) - url to receive callbacks, should contain "http" or "https",
        eg. "https://nowpayments.io"
        :param order_id: (optional) - inner store order ID, e.g. "RGDBP-21314"
        :param order_description: (optional) - inner store order description, e.g. "Apple Macbook Pro 2019 x 1"
        :param purchase_id: (optional) - id of purchase for which you want to create another payment,
        only used for several payments for one order
        :param payout_address: (optional) - usually the funds will go to the address you specify in your Personal
        account. In case you want to receive funds on another address, you can specify it in this parameter.
        :param payout_currency: (optional) - currency of your external payout_address, required when payout_address
        is specified.
        :param payout_extra_id: (optional) - extra id or memo or tag for external payout_address.
        :param fixed_rate: (optional) - boolean, can be true or false. Required for fixed-rate exchanges.
        """
        payload = {
            "price_amount": price_amount,
            "price_currency": price_currency,
            "pay_currency": pay_currency,
        }
        if order_id:
            payload["order_id"] = order_id
        if order_description:
            payload["order_description"] = order_description
        if ipn_callback_url:
            payload["ipn_callback_url"] = ipn_callback_url
        if pay_amount:
            payload["pay_amount"] = pay_amount
        if purchase_id:
            payload["purchase_id"] = purchase_id
        if payout_address:
            payload["payout_address"] = payout_address
        if payout_currency:
            payload["payout_currency"] = payout_currency
        if payout_extra_id:
            payload["payout_extra_id"] = payout_extra_id
        if fixed_rate:
            payload["fixed_rate"] = fixed_rate
        if is_fee_paid_by_user:
            payload["is_fee_paid_by_user"] = is_fee_paid_by_user
        result = await self._post("payment", json=payload)
        return Payment(**result)

    async def get_payment_status(self, payment_id: int):
        result = await self._get("payment", str(payment_id))
        return PaymentUpdate(**result)
