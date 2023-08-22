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
    debug_mode: bool = False


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
    ipn_secret: Optional[str] = None


@dataclass
class RedisConfig:
    """
    Redis configuration class.

    Attributes
    ----------
    redis_pass : Optional(str)
        The password used to authenticate with Redis.
    redis_port : Optional(int)
        The port where Redis server is listening.
    redis_host : Optional(str)
        The host where Redis server is located.
    """

    redis_pass: Optional[str]
    redis_port: Optional[int]
    redis_host: Optional[str]

    def dsn(self) -> str:
        """
        Constructs and returns a Redis DSN (Data Source Name) for this database configuration.
        """
        if self.redis_pass:
            return f"redis://:{self.redis_pass}@{self.redis_host}:{self.redis_port}/0"
        else:
            return f"redis://{self.redis_host}:{self.redis_port}/0"

    @staticmethod
    def from_env(env: Env):
        """
        Creates the RedisConfig object from environment variables.
        """
        redis_pass = env.str("REDIS_PASSWORD")
        redis_port = env.int("REDIS_PORT")
        redis_host = env.str("REDIS_HOST")

        return RedisConfig(
            redis_pass=redis_pass, redis_port=redis_port, redis_host=redis_host
        )


@dataclass
class Config:
    tg_bot: TgBot
    support_bot: TgBot
    db: DbConfig = None
    wayforpay: WayforpayConfig = None
    nowpayments: NowPaymentsConfig = None
    redis: RedisConfig = None


def load_config(path: Optional[str] = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS"),
            debug_mode=env.bool("DEBUG_MODE", False),
        ),
        support_bot=TgBot(
            token=env.str("SUPPORT_BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS"),
            debug_mode=env.bool("DEBUG_MODE", False),
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
            ipn_secret=env.str("NOWPAYMENTS_IPN_SECRET"),
        ),
        redis=RedisConfig.from_env(env) if env.bool("USE_REDIS") else None,

    )
