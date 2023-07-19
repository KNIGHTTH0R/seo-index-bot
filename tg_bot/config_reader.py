from dataclasses import dataclass
from typing import Optional

from environs import Env
from sqlalchemy import URL


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str
    port: int = 5432

    def construct_sqlalchemy_url(self, driver="asyncpg", host=None, port=None) -> str:
        if not host:
            host = self.host
        if not port:
            port = self.port
        uri = URL.create(
            drivername=f"postgresql+{driver}",
            username=self.user,
            password=self.password,
            host=host,
            port=port,
            database=self.database,
        )
        return uri.render_as_string(hide_password=False)


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    use_redis: bool


@dataclass
class Miscellaneous:
    other_params: str = Optional[str]


@dataclass
class WayforpayConfig:
    merchant_account: str
    merchant_secret_key: str
    merchant_domain: str
    webhook_url: Optional[str] = None


@dataclass
class NowPaymentsConfig:
    api_key: str
    callback_url: Optional[str] = None


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig = None
    wayforpay: WayforpayConfig = None
    nowpayments: NowPaymentsConfig = None


def load_config(path: Optional[str]):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS"),
        ),
        db=DbConfig(
            host=env.str("DB_HOST"),
            password=env.str("POSTGRES_PASSWORD"),
            user=env.str("POSTGRES_USER"),
            database=env.str("POSTGRES_DB"),
        ),
        wayforpay=WayforpayConfig(
            merchant_account=env.str("MERCHANT_ACCOUNT"),
            merchant_secret_key=env.str("MERCHANT_SECRET_KEY"),
            merchant_domain=env.str("MERCHANT_DOMAIN"),
            webhook_url=env.str("WEBHOOK_URL"),
        ),
        nowpayments=NowPaymentsConfig(
            api_key=env.str("NOWPAYMENTS_API_KEY"),
            callback_url=env.str("NOWPAYMENTS_CALLBACK_URL"),
        ),
    )
