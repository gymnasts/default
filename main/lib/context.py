from __future__ import annotations

from typing import (
    ClassVar,
    Optional,
    TypedDict,
    List,
    Any
)

import json

from discord.ext.commands import Context as _Context
from discord import *

from .paginator import Paginator


class Config(TypedDict):
    """
    Represents the Config for the `Context` class
    """
    warn: str
    tick: str
    nope: str


class Context(_Context):
    """
    A custom context class for the `Default` bot
    Extending the default `discord.ext.commands.Context`

    Methods
    -------
    approve(content: Optional[str] = None) -> :class:`discord.Message`:
        Returns a message indicating a successful operation
        
    deny(content: Optional[str] = None) -> :class:`discord.Message`:
        Returns a message indicating a failed operation
        
    alert(content: Optional[str] = None) -> :class:`discord.Message`:
        Returns a message indicating an alert or warning


    Attributes
    ----------
    config : :class:`dict`
        Contains configuration data loaded from the JSON file, including emoji settings

    tick : :class:`str`
        The emoji used for the `approve()` method, representing success
        
    nope : :class:`str`
        The emoji used for the `deny()` method, representing failure
        
    warn : :class:`str`
        The emoji used for the `alert()` method, representing a warning or alert
    """
    config: ClassVar[Config] = json.load(
        open(
            file = "data/object.json",
            mode = "r"
        )
    )
    warn: ClassVar[str] = config["warn"]
    tick: ClassVar[str] = config["tick"]
    nope: ClassVar[str] = config["nope"]


    def __init__(
        self: Context, 
        **kwargs: Any

    ) -> None:
        """
        Initializes a custom context instance for the `Default` bot.

        Parameters
        ----------
        **kwargs : Any
            Additional keyword arguments passed to the parent class constructor.
        """
        super().__init__(**kwargs)


    async def approve(
        self: Context,
        content: Optional[str] = None
    ) -> Message:
        """
        Sends a message indicating a successful operation.

        Parameters
        ----------
        content : Optional[str], optional
            The content to include in the success message. If not provided, a default thumbs-up emoji is sent.

        Returns
        -------
        discord.Message
            A message with a success embed or a thumbs-up emoji.
        """
        if content:
            return await self.reply(
                embed = Embed(
                    description = (
                        f"{self.tick} {self.author.mention} {content}"
                    ),
                    color = 0x2A2D31
                )
            )

        else:
            return await self.reply(
                ":thumbsup:"
            )


    async def deny(
        self: Context,
        content: Optional[str] = None
    ) -> Message:
        """
        Sends a message indicating a failed operation.

        Parameters
        ----------
        content : Optional[str], optional
            The content to include in the fail message. If not provided, a default thumbs-down emoji is sent.

        Returns
        -------
        discord.Message
            A message with a fail embed or a thumbs-down emoji.
        """
        if content:
            return await self.reply(
                embed = Embed(
                    description = (
                        f"{self.nope} {self.author.mention} {content}"
                    ),
                    color = 0x2A2D31
                )
            )

        else:
            return await self.reply(
                ":thumbsdown:"
            )


    async def alert(
        self: Context,
        content: Optional[str] = None
    ) -> Message:
        """
        Sends a message indicating an alert or warning.

        Parameters
        ----------
        content : Optional[str], optional
            The content to include in the alert message. If not provided, a default warning emoji is sent.

        Returns
        -------
        discord.Message
            A message with an alert embed or a warning emoji.
        """
        if content:
            return await self.reply(
                embed = Embed(
                    description = (
                        f"{self.warn} {self.author.mention} {content}"
                    ),
                    color = 0x2A2D31
                )
            )

        else:
            return await self.reply(
                ":warning:"
            )


    async def help(self: Context) -> Message:
        """
        Sends an embed with detailed help information about the current command, 
        with pagination if there are sub-commands.

        Returns
        -------
        discord.Message
            A message with a help embed or a series of embeds for pagination.
        """
        command = self.command
        embeds = []

        # Create an embed for the main command
        embed = Embed(
            title=f"Command: {command.name}" if not hasattr(command, 'commands') else f"Group: {command.name}",
            description=getattr(command, 'brief', 'No description provided'),
            color=0x2A2D31
        )

        embed.add_field(
            name="Aliases",
            value=", ".join(command.aliases) if command.aliases else "n/a",
            inline=True
        )
        embed.add_field(
            name="Parameters",
            value=", ".join(command.clean_params.keys()) if command.clean_params else "",
            inline=True
        )

        permissions = "None"
        for check in command.checks:
            permissions = next(
                (
                    ', '.join(
                        perm.replace('_', ' ').capitalize()
                        for perm in cell.cell_contents
                    )
                    for cell in check.__closure__ or []
                    if isinstance(cell.cell_contents, dict)
                ),
                permissions
            )

        embed.add_field(
            name="Information",
            value=f"{self.warn} {permissions}",
            inline=True
        )

        embed.add_field(
            name="Usage",
            value=f"```Syntax: {command.name} {command.usage or ''}\n"
                  f"Example: {command.name} {getattr(command, '__original_kwargs__', {}).get('example', '')}```",
            inline=False
        )

        embed.set_author(
            name=self.author.name,
            icon_url=(
                self.author.avatar.url
                if self.author.avatar
                else self.bot.user.avatar.url
            )
        )
        embed.set_footer(
            text=",help (command)",
            icon_url=self.bot.user.avatar.url
        )

        embeds.append(embed)

        # If the command has sub-commands, paginate with subcommand information
        if hasattr(command, 'commands') and command.commands:
            for subcommand in command.commands:
                sub_embed = Embed(
                    title=f"Sub-command: {subcommand.name}",
                    description=getattr(subcommand, 'brief', 'No description provided'),
                    color=0x2A2D31
                )

                sub_embed.add_field(
                    name="Aliases",
                    value=", ".join(subcommand.aliases) if subcommand.aliases else "n/a",
                    inline=True
                )
                sub_embed.add_field(
                    name="Parameters",
                    value=", ".join(subcommand.clean_params.keys()) if subcommand.clean_params else "",
                    inline=True
                )

                permissions = "None"
                for check in subcommand.checks:
                    permissions = next(
                        (
                            ', '.join(
                                perm.replace('_', ' ').capitalize()
                                for perm in cell.cell_contents
                            )
                            for cell in check.__closure__ or []
                            if isinstance(cell.cell_contents, dict)
                        ),
                        permissions
                    )

                sub_embed.add_field(
                    name="Information",
                    value=f"{self.warn} {permissions}",
                    inline=True
                )

                sub_embed.add_field(
                    name="Usage",
                    value=f"```Syntax: {subcommand.name} {subcommand.usage or ''}\n"
                          f"Example: {subcommand.name} {getattr(subcommand, '__original_kwargs__', {}).get('example', '')}```",
                    inline=False
                )

                sub_embed.set_author(
                    name=self.author.name,
                    icon_url=(
                        self.author.avatar.url
                        if self.author.avatar
                        else self.bot.user.avatar.url
                    )
                )
                sub_embed.set_footer(
                    text=f",help {command.name} (sub-command)",
                    icon_url=self.bot.user.avatar.url
                )

                embeds.append(sub_embed)

        # If there's more than one embed, paginate; otherwise, just send the single embed
        if len(embeds) > 1:
            return await self.paginate(embeds)
        else:
            return await self.send(embed=embeds[0])


    async def paginate(
        self: Context, 
        embeds: List[Embed]
    ) -> None:
        """
        Paginate Embeds

        Parameters
        ----------
        embeds : List[Embed]
            A list of embeds to paginate.
        """
        view = Paginator(self, embeds)
        await self.send(embed=embeds[0], view=view)