import logging
from dataclasses import dataclass
from typing import Callable, Optional
from typing import Dict

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.kbd import Button, Group
from aiogram_dialog.widgets.text import Text, Multi
from fluentogram import AttribTracer, TranslatorRunner


class OpenClose(Text):
    def __init__(
        self,
        turn_on_option: Text,
        default_option: Text,
        selection_key: str,
        when: WhenCondition = None,
    ):
        super().__init__(when=when)
        self.turn_on_option = turn_on_option
        self.default_option = default_option
        self.selection_key = selection_key

    async def _render_text(self, data, manager: DialogManager) -> str:
        if data.get(self.selection_key):
            return await self.turn_on_option.render_text(data, manager)
        return await self.default_option.render_text(data, manager)

    def find(self, widget_id: str) -> Optional[Text]:
        for text in [self.turn_on_option, self.default_option]:
            if found := text.find(widget_id):
                return found
        return None


class Translation(AttribTracer):
    def __init__(self, separator: str = "-") -> None:
        super().__init__()
        self.separator = separator
        self.request_line = ""

    def __getattr__(self, item: str) -> "Translation":
        self.request_line += f"{item}{self.separator}"
        return self

    def __call__(self):
        text = self.request_line[:-1]
        self.request_line = ""
        return text


class TranslatableFormat(Text):
    def __init__(self, key: str, when: WhenCondition = None):
        super().__init__(when=when)
        self.key = key

    async def _render_text(
        self,
        data: Dict,
        manager: DialogManager,
    ) -> str:
        i18n: "TranslatorRunner" = manager.middleware_data.get("i18n")
        try:
            translated = i18n.get(self.key, **data)
        except Exception as e:
            logging.info(f"Failed to Translate {self.key}")
            return f"no-translation-error: {self.key}"

        translated = translated.format_map(data)
        return translated


@dataclass
class Option:
    id: str
    text: "TranslatorRunner"
    when_key: str


def dropdown_on_off_menu(
    dropdown_title: "TranslatorRunner",
    selection_key: str,
    options: list[Option],
    on_click: Callable,
    on_open_close: Callable,
    always_open: bool = False,
):
    i18n: "TranslatorRunner" = Translation()
    window_parts = []
    if not always_open:
        window_parts.append(
            Button(
                Multi(
                    TranslatableFormat(dropdown_title),
                    OpenClose(
                        TranslatableFormat(i18n.dialogs.buttons.open_on()),
                        default_option=TranslatableFormat(
                            i18n.dialogs.buttons.open_off()
                        ),
                        selection_key=selection_key,
                    ),
                ),
                id=selection_key,
                on_click=on_open_close,
            )
        )
    else:
        window_parts.append(
            TranslatableFormat(dropdown_title),
        )

    window_parts.append(
        Group(
            *[
                Button(
                    Multi(
                        TranslatableFormat(
                            i18n.dialogs.buttons.check_mark(), when=option.when_key
                        ),
                        TranslatableFormat(option.text),
                        sep=" ",
                    ),
                    id=option.id,
                    on_click=on_click,
                )
                for option in options
            ],
            width=4,
            when=selection_key if not always_open else None,
        ),
    )
    return window_parts
