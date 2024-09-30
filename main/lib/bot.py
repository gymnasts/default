from __future__ import annotations

from typing import (
    ClassVar,
    TypedDict,
    Any
)

from discord.ext.commands import (
    Bot,
    MissingRequiredArgument,
    MissingFlagArgument,
    MissingRequiredAttachment,
    MissingRequiredFlag,
    CommandOnCooldown,
    CommandError,
    CommandNotFound
)
from .context import Context
from discord import Intents, Message

import json
import sqlite3


class Config(TypedDict):
    token: str
    prefix: str
    developer: int


class Template(Bot):
    """A Template discord.py bot"""
    config: ClassVar[Config] = json.load(
        open(
            file = "data/config.json",
            mode = "r"
        )
    )
    token: ClassVar[str] = config["token"]
    prefix: ClassVar[str] = config["prefix"]
    developer: ClassVar[int] = config["developer"]
    
    connection: ClassVar[sqlite3.Connection] = sqlite3.connect(
        database = "data/base/main.db",
        timeout = 1
    )
    cursor: ClassVar[sqlite3.Cursor] = connection.cursor()


    def __init__(
        self: Template, 
        *args: Any, 
        **kwargs: Any

    ) -> None:
        """
        Initializes the Template bot instance.

        Args:
            *args (Any): Variable length argument list passed to Bot.
            **kwargs (Any): Arbitrary keyword arguments passed to Bot.
        """
        super().__init__(
            *args,
            **kwargs,
            command_prefix = self.prefix,
            intents = Intents.all(), 
            help_command = None,
            description = self.__doc__.strip()
        )


    async def setup_hook(self: Template) -> None:
        """
        Asynchronous setup hook to load bot features/extensions
        """
        for feature in [
            "information",
            "welcome"
        ]:
            await self.load_extension(
                f"groups.{feature}"
            )


    async def get_context(
        self: Template, 
        message: Message, *, 
        cls = Context

    ) -> Context:
        """
        Gets the custom context for a given message.

        Args:
            message (Message): The message to get the context for.
            cls (Type[Context], optional): The custom context class to use. Defaults to `Context`.

        Returns:
            Context: The custom context object for the message.
        """
        return await super().get_context(
            message, 
            cls=cls
        )


    async def on_command_error(
        self: Template, 
        ctx: Context, 
        error: Any
        
    ) -> Message:
        """
        Handles errors raised during command execution.

        Args:
            ctx (Context): The context of the command that caused the error.
            error (Any): The error that was raised.

        Returns:
            Message: A message response based on the error type.
        """
        if isinstance(
            error, 
            (
                MissingRequiredArgument,
                MissingFlagArgument,
                MissingRequiredAttachment,
                MissingRequiredFlag
            )
        ):
            return await ctx.help()

        elif isinstance(
            error,
            CommandOnCooldown
        ):
            return await ctx.deny(
                f"You are on **cooldown!**"
            )

        elif isinstance(
            error, 
            CommandError
        ):
            return await ctx.alert(
                f"**{str(error).strip('.')}**"
            )

        elif isinstance(
            error,
            CommandNotFound
        ):
            return


    def run(self: Template) -> None:
        """
        Run the bot
        """
        super().run(
            token = self.token, 
            reconnect = True, 
            root_logger = True
        )