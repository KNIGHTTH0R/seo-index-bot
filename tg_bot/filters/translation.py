from aiogram.filters import BaseFilter
from aiogram.types import Message
from fluentogram import TranslatorRunner


class TranslationFilter(BaseFilter):
    def __init__(self, key: str):
        self.key = key

    async def __call__(self, obj: Message, i18n: "TranslatorRunner") -> bool:
        return i18n.get(self.key) == obj.text
