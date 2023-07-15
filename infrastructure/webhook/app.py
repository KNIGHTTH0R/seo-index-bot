import hashlib
import hmac
import json
import logging
from datetime import datetime
from datetime import timezone
from functools import partial
from json import JSONDecodeError

import betterlogging as bl
import fastapi
from aiogram import Bot
from fastapi import FastAPI
from fastapi import Header, HTTPException
from pydantic import ValidationError
from starlette.responses import JSONResponse, StreamingResponse

from database.requests.requests import Repo
from database.setup import create_session_pool
from infrastructure.mixpanel.api import MixpanelClient
from infrastructure.mixpanel.types import Events
from infrastructure.webhook.types import CryptoPayUpdate, WayforpayRequestData
from openai.official.api import OpenAIAPIClient
from openai.official.types import ChatCompletionRequest
from openai.official.utils import num_tokens_from_messages
from tgbot.config import load_config, Config

app = FastAPI()
log_level = logging.INFO
bl.basic_colorized_config(level=log_level)
log = logging.getLogger(__name__)

config: Config = load_config()
session_pool = create_session_pool(config.db)
bot = Bot(token=config.tg_bot.token)
mixpanel_client = MixpanelClient(config.misc.mixpanel_token)
openai_client = OpenAIAPIClient(config.misc.openai_api_key)


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
    signature = generate_signature_old(config.payments.wayforpay_secret_key, sign)
    merchantSignature = response.get("merchantSignature")
    result = merchantSignature == signature
    if not result:
        log.error(f"Invalid signature: {merchantSignature} != {signature}")
    return result


@app.post(f"{config.misc.webhook_prefix}/gpt/wayforpay")
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
        config.payments.wayforpay_secret_key,
        ";".join(
            [
                data.orderReference,
                "accept",
                str(resp_time),
            ]
        ),
    )
    if data.transactionStatus == "Approved":
        async with session_pool() as session:
            repo = Repo(session)
            tx = await repo.get_tx(data.orderReference)
            if not tx:
                return JSONResponse(
                    status_code=400, content={"error": "Transaction not found"}
                )
            if tx.status:
                return JSONResponse(
                    status_code=400, content={"error": "Transaction already paid"}
                )
            await repo.update_tx_paid(data.orderReference)
            await repo.add_tokens(
                tx.user_id, tx.tokens_num, pricing_tier_id=tx.pricing_tier_id
            )
            await repo.activate_user_subscription(tx.user_id)
            await session.commit()

            await bot.send_message(
                tx.user_id,
                f"Thank you for your payment! Your {tx.tokens_num} tokens were added to your account!",
            )
            user = await repo.get_user(tx.user_id)
            await mixpanel_client.add_event(
                Events.Purchase,
                user=user,
                invoice_id=data.orderReference,
                num_tokens=tx.tokens_num,
                currency=tx.currency,
                usd_amount=tx.usd_amount,
            )

    response_data = {
        "orderReference": data.orderReference,
        "status": "accept",
        "time": resp_time,
        "signature": response_signature,
    }

    return JSONResponse(content=response_data)


---- 
for nowpayments




async def validate_request(request: Request):
    payment_update = await request.json()
    sorted_data = {k: payment_update[k] for k in sorted(payment_update.keys())}
    # Convert the data to a JSON string
    msg = json.dumps(sorted_data, sort_keys=True)
    msg = msg.replace(' ', '').encode('utf-8')
    # Generate the signature
    signed_string = hmac.new(
        key=config.nowpayments.ipn_secret.encode('utf-8'),
        msg=msg,
        digestmod=hashlib.sha512
    ).hexdigest()

    nowpayments_sig = request.headers.get('x-nowpayments-sig')

    return signed_string == nowpayments_sig


@app.post("/nowpayments")
async def nowpayments_route(request: Request):
    data = await request.json()
    payment_update = PaymentUpdate(**data)
    if config.nowpayments.ipn_secret and not await validate_request(request):
        log.info('Not valid signature')
        return {'status': "Invalid request"}
    if not payment_update.actually_paid:
        log.info('Not paid yet')
        return {'status': "Not paid"}
    if payment_update.payment_status in (PaymentStatus.CONFIRMED, PaymentStatus.FINISHED, PaymentStatus.SENDING):
        log.info(f'Status is {payment_update.payment_status}')
        async with session_pool() as session:
            if (status := await get_tx_status(session, payment_update.pay_address)) is not False:
                return

            await update_tx_paid(session, payment_update.pay_address, str(payment_update.purchase_id))
            await session.commit()
            tx: Transactions = await get_tx_info(session, int(payment_update.order_id))
            await bot.send_message(
                tx.user_id, f'Your payment is confirmed. {tx.checks_num} checks were added to your account'
            )