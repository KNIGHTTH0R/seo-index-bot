from collections import defaultdict

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import (
    BotCommand,
    BotCommandScopeChat,
    BotCommandScopeChatMember,
)


async def collect_and_assign_commands(routers: list[Router], bot, sort=True):
    commands = get_commands_from_routers(routers)
    await assign_commands_to_bot(bot, commands, sort)


def get_commands_from_routers(routers: list[Router]):
    commands = defaultdict(lambda: defaultdict(dict))
    scope_types = {}

    for command, description, language_code, scope in extract_command_descriptions(
            routers
    ):
        if isinstance(scope, BotCommandScopeChat):
            scope_key = f"{scope.type}:{scope.chat_id}"
        elif isinstance(scope, BotCommandScopeChatMember):
            scope_key = f"{scope.type}:{scope.chat_id}:{scope.user_id}"
        else:
            scope_key = str(scope)
        scope_types[scope_key] = scope
        if language_code == "description":
            language_code = None
        commands[scope_key][language_code][command] = description

    return commands, scope_types


async def assign_commands_to_bot(bot, commands_with_scopes, sort=True):
    commands, scope_types = commands_with_scopes

    for scope_key, language_codes in commands.items():
        for language_code, cmds in language_codes.items():
            # logging.info(
            #     f"Registering commands for {scope_key} {language_code}: {cmds}"
            # )

            scope = scope_types[scope_key]
            commands_list = (
                sorted(cmds.items(), key=lambda x: x[0]) if sort else cmds.items()
            )
            try:
                await bot.set_my_commands(
                    commands=[
                        BotCommand(command=command, description=description)
                        for command, description in commands_list
                    ],
                    scope=scope,
                    language_code=language_code,
                )
            except TelegramBadRequest as e:
                pass


def extract_command_descriptions(routers: list[Router]):
    processed_handlers = set()
    for router in routers:
        for handler in router.message.handlers:
            handler_key = str(handler.callback)
            if handler_key in processed_handlers:
                continue
            processed_handlers.add(handler_key)
            if "commands" not in handler.flags:  # ignore handlers without commands
                continue
            if command_descriptions := handler.flags.get("command_description"):
                command_obj: Command = handler.flags.get("commands")[0]
                if "/" not in command_obj.prefix:
                    continue
                command = command_obj.commands[0]
                scopes = command_descriptions.pop("scopes", [None])
                for scope in scopes:
                    # logging.info(
                    # f"Extracting commands for {scope}: {command}: {command_descriptions}"
                    # )
                    for language_code, description in command_descriptions.items():
                        yield command, description, language_code, scope
                # Recursively extract commands from nested routers
                for sub_router in router.sub_routers:
                    yield from extract_command_descriptions(sub_router)
