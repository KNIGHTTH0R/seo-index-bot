import json
import logging
from dataclasses import dataclass

import aiohttp

from tg_bot.utils.utils import generate_signature
from .constants import API_URL


@dataclass
class Invoice:
    reason: str
    reasonCode: str
    invoiceUrl: str = None
    qrCode: str = None


# noinspection PyMethodMayBeStatic
class BadGateway(Exception):
    pass


async def _query(params, url=API_URL):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, verify_ssl=False, json=params) as resp:
            try:
                # js = await resp.json()
                text = await resp.text()
                try:
                    json_data = json.loads(text)
                except json.decoder.JSONDecodeError as err:
                    logging.error(
                        f"ERROR: {err.__class__.__name__}: {err}. TEXT: {text}"
                    )
                    if "bad gateway" in text.lower():
                        raise BadGateway()
                logging.info(f"RESPONSE: ----{resp}-{json_data}--")

                return json_data

            except aiohttp.ContentTypeError:
                logging.info(f"aiohttp.ContentTypeError: ----{resp}-----{params}")


class WayForPayAPI:
    def __init__(self, merchant_account, merchant_key, merchant_domain, webhook_url):
        self.merchant_account = merchant_account
        self.merchant_key = merchant_key
        self.merchant_domain = merchant_domain
        self.webhook_url = webhook_url

    async def create_invoice(
        self,
        product_name,
        product_price,
        product_count,
        currency,
        order_date,
        first_name,
        last_name,
        order_reference,
    ):
        signature_data = ";".join(
            [
                str(param)
                for param in [
                    self.merchant_account,
                    self.merchant_domain,
                    order_reference,
                    order_date,
                    product_price,
                    currency,
                    product_name,
                    product_count,
                    product_price,
                ]
            ]
        )
        merchantSignature = generate_signature(self.merchant_key, signature_data)

        params = {
            "transactionType": "CREATE_INVOICE",
            "merchantAccount": self.merchant_account,
            "merchantAuthType": "SimpleSignature",
            "merchantDomainName": self.merchant_domain,
            "merchantSignature": merchantSignature,
            "apiVersion": 1,
            "language": "EN",
            "notifyMethod": "bot",
            "orderDate": order_date,
            "serviceUrl": self.webhook_url,
            "orderReference": order_reference,
            "amount": product_price,
            "currency": currency,
            "productName": [product_name],
            "productPrice": [product_price],
            "productCount": [product_count],
            "paymentSystems": ";".join(
                [
                    "card",
                    "privat24",
                    "masterPass",
                    "visaCheckout",
                    "applePay",
                    "googlePay",
                    "lpTerminal",
                    "btc",
                    "credit",
                    "payParts",
                    "qrCode",
                    "masterPass",
                    "visaCheckout",
                    "payParts",
                ]
            ),
            "clientFirstName": first_name[:16] if first_name else "",
            "clientLastName": last_name[:32] if last_name else "",
        }
        logging.info(params)
        response = await _query(params)
        return Invoice(**response)
