from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from fluent_compiler.bundle import FluentBundle
from fluentogram import TranslatorHub, FluentTranslator
from fluentogram import TranslatorRunner
from infrastructure.database.models.users import User


class TranslationMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.t_hub = TranslatorHub(
            {
                'uk': ('uk', 'ru'),
                "ru": ("ru",),
            },
            translators=[
                FluentTranslator(
                    locale=language_code,
                    translator=FluentBundle.from_files(
                        language_code,
                        [f"tg_bot/locales/{language_code}.ftl"],
                        use_isolating=False,
                    ),
                    separator="-",
                )
                for language_code in (
                    'uk',
                    "ru",
                )
            ],
            root_locale="uk",
        )

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        user: User = data.get("user")

        translator_runner: TranslatorRunner = self.t_hub.get_translator_by_locale(User.language)

        data["i18n"] = translator_runner
        data["th"] = self.t_hub
        return await handler(event, data)
