import hashlib
import hmac
import json
import logging
from datetime import datetime
from json import JSONDecodeError

import betterlogging as bl
import fastapi
from aiogram import Bot
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from starlette.requests import Request
from starlette.responses import JSONResponse

from infrastructure.database.repo.base import Repo
from infrastructure.nowpayments.types import PaymentStatus, PaymentUpdate
from infrastructure.webhook.types import WayforpayRequestData
from tg_bot.config_reader import load_config, Config

app = FastAPI()
log_level = logging.INFO
bl.basic_colorized_config(level=log_level)
log = logging.getLogger(__name__)

config: Config = load_config()
engine = create_async_engine(config.db.construct_sqlalchemy_url(), echo=True)
session_maker = async_sessionmaker(engine, expire_on_commit=False)
bot = Bot(token=config.tg_bot.token)


def check_signature_crypto(token: str, body: str, signature: str) -> bool:
    secret = hashlib.sha256(token.encode()).digest()
    hmac_digest = hmac.new(secret, body.encode(), hashlib.sha256).hexdigest()
    return hmac_digest == signature


def generate_signature_old(merchant_key, data_str):
    return hmac.new(merchant_key.encode(), data_str.encode(), hashlib.md5).hexdigest()


def check_signature_wayforpay(response):
    sign = ";".join(
        [
            str(response.get(key))
            for key in [
                "merchantAccount",
                "orderReference",
                "amount",
                "currency",
                "authCode",
                "cardPan",
                "transactionStatus",
                "reasonCode",
            ]
        ]
    )
    signature = generate_signature_old(config.wayforpay.merchant_secret_key, sign)
    merchantSignature = response.get("merchantSignature")
    result = merchantSignature == signature
    if not result:
        log.error(f"Invalid signature: {merchantSignature} != {signature}")
    return result


async def update_payment_status_and_send_message(order_id: str, session):
    repo = Repo(session)
    tx = await repo.get_tx(order_id)
    if not tx:
        return JSONResponse(status_code=400, content={"error": "Transaction not found"})
    if tx.status:
        return JSONResponse(
            status_code=400, content={"error": "Transaction already paid"}
        )
    await repo.update_tx_paid(order_id)

    await bot.send_message(
        tx.fk_tg_id,
        # Add Translations
        f"Your payment is confirmed. {tx.amount_points} points were added to your account",
    )


@app.post(f"/wayforpay/callback")
async def wayforpay_webhook_endpoint(request: fastapi.Request):
    try:
        # Get the request body as text
        payload = await request.body()
        payload_str = payload.decode("utf-8")
        log.info(f"Received payload: {payload_str}")
        # Parse the text payload to JSON and validate using Pydantic
        payload_json = json.loads(payload_str)
        data = WayforpayRequestData.parse_obj(payload_json)
    except JSONDecodeError as e:
        logging.exception(e)
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except ValidationError as e:
        logging.exception(e)
        raise HTTPException(status_code=422, detail=str(e))

    # Verify signature
    received_signature = data.merchantSignature
    if not check_signature_wayforpay(payload_json):
        return JSONResponse(status_code=400, content={"error": "Invalid signature"})

    # Generate response signature
    resp_time = int(datetime.utcnow().timestamp())
    response_signature = generate_signature_old(
        config.wayforpay.merchant_secret_key,
        ";".join(
            [
                data.orderReference,
                "accept",
                str(resp_time),
            ]
        ),
    )
    logging.info(f"Response signature: {response_signature}, {received_signature}")
    if data.transactionStatus == "Approved":
        async with session_maker() as session:
            await update_payment_status_and_send_message(data.orderReference, session)

    response_data = {
        "orderReference": data.orderReference,
        "status": "accept",
        "time": resp_time,
        "signature": response_signature,
    }

    return JSONResponse(content=response_data)


async def validate_request(request: Request):
    payment_update = await request.json()
    sorted_data = {k: payment_update[k] for k in sorted(payment_update.keys())}
    # Convert the data to a JSON string
    msg = json.dumps(sorted_data, sort_keys=True)
    msg = msg.replace(" ", "").encode("utf-8")
    # Generate the signature
    signed_string = hmac.new(
        key=config.nowpayments.ipn_secret.encode("utf-8"),
        msg=msg,
        digestmod=hashlib.sha512,
    ).hexdigest()

    nowpayments_sig = request.headers.get("x-nowpayments-sig")

    return signed_string == nowpayments_sig


@app.post("/nowpayments/callback")
async def nowpayments_route(request: Request):
    data = await request.json()
    payment_update = PaymentUpdate(**data)
    if config.nowpayments.ipn_secret and not await validate_request(request):
        log.info("Not valid signature")
        return {"status": "Invalid request"}
    if not payment_update.actually_paid:
        log.info("Not paid yet")
        return {"status": "Not paid"}
    log.info(f"Status is {payment_update.payment_status}")

    if payment_update.payment_status == PaymentStatus.FINISHED or (
        payment_update.payment_status
        in (PaymentStatus.CONFIRMED, PaymentStatus.SENDING)
        and payment_update.actually_paid >= payment_update.pay_amount
    ):
        async with session_maker() as session:
            await update_payment_status_and_send_message(
                payment_update.order_id, session
            )
