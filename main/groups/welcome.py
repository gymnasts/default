from __future__ import annotations

from lib.context import Context
from lib.builder import Builder
from lib.bot import Template

from discord.ext.commands import (
    Cog,
    group,
    cooldown,
    BucketType,
    MissingPermissions
)

from discord import (
    Message, 
    TextChannel as Channel, 
    Member, 
    Embed
)

import sqlite3 
import json

from typing import ClassVar


class Welcome(Cog):
    """
    Welcome Cog for Template
    """
    
    connection: ClassVar[sqlite3.Connection] = sqlite3.connect(
        "data/base/welcome.db",
        timeout=1
    )
    cursor: ClassVar[sqlite3.Cursor] = connection.cursor()

    def __init__(
        self: Welcome, 
        bot: Template
    ) -> None:
        self.bot: Template = bot


    async def cog_check(
        self: Welcome, 
        ctx: Context
    ) -> bool:
        """
        Checks if the user has the necessary permissions to manage welcome messages.

        Parameters
        ----------
        ctx : Context
            The context of the command invoked.

        Returns
        -------
        bool
            True if the user has the required permissions; otherwise, raises MissingPermissions.
        """
        author_permissions = ctx.author.guild_permissions
        if (
            author_permissions.manage_channels and
            author_permissions.manage_guild
        ):
            return True
        
        raise MissingPermissions(
            [
                'manage_channels', 
                'manage_guild'
            ]
        )


    @group(
        name = "welcome",
        brief = "Manage welcome messages",
        usage = "<args>",
        example = "add #welcome {embed}$v...",
        invoke_without_command=True,
        aliases=["wlc"]
    )
    @cooldown(1, 5, BucketType.user)
    async def welcome(
        self: Welcome,
        ctx: Context
    ) -> Message:
        """
        Displays help information for the welcome command group

        Parameters
        ----------
        ctx : Context
            The context of the command invoked.

        Returns
        -------
        Message
            A message with the help information.
        """
        return await ctx.help()


    @welcome.command(
        name = "add",
        brief = "Add a welcome message",
        usage = "(channel) <content> <embed>",
        example = "#welcome {embed}$v{title: Hey}"
    )
    @cooldown(1, 5, BucketType.user)
    async def add(
        self: Welcome,
        ctx: Context,
        channel: Channel = None, 
        content: str = None, *,
        flags: str = None
    ) -> Message:
        """
        Adds a welcome message to the specified channel.

        Parameters
        ----------
        ctx : Context
            The context of the command invoked.
        channel : Channel
            The channel where the welcome message will be sent.
        content : str
            The content of the welcome message.
        flags : str
            Additional flags for formatting the embed.

        Returns
        -------
        Message
            A message confirming the addition of the welcome message.
        """
        if channel not in ctx.guild.channels:
            return await ctx.alert(
                f"{channel.mention} is not in this **server!**"
            )        

        builder = Builder(flags)
        embed_json = json.dumps(builder.create().to_dict())

        self.cursor.execute(
            '''
            REPLACE INTO welcomes(
                guild,
                channel,
                content,
                embed
            )
            VALUES (
                ?, ?, ?, ?
            )
            ''',
            (
                ctx.guild.id,
                channel.id or ctx.channel.id,
                content,
                embed_json
            )
        )
        self.connection.commit()

        return await ctx.send(
            embed=builder.create(
                ctx.author
            )
        )


    @welcome.command(
        name = "edit",
        brief = "Edit the current welcome message",
        usage = "(channel) <content> <embed>",
        example = "#welcome {embed}$v{title: Hey}"
    )
    @cooldown(1, 5, BucketType.user)
    async def edit(
        self: Welcome,
        ctx: Context,
        channel: Channel = None, 
        content: str = None, *,
        flags: str = None
    ) -> Message:
        """
        Edits the current welcome message in the specified channel.

        Parameters
        ----------
        ctx : Context
            The context of the command invoked.
        channel : Channel
            The channel to edit the welcome message for.
        content : str
            The new content of the welcome message.
        flags : str
            Additional flags for formatting the embed.

        Returns
        -------
        Message
            A message confirming the editing of the welcome message.
        """
        if channel not in ctx.guild.channels:
            return await ctx.alert(
                f"{channel.mention} is not in this **server!**"
            )

        self.cursor.execute(
            '''
            SELECT channel, content, embed 
            FROM welcomes 
            WHERE guild = ?
            ''',
            (
                ctx.guild.id,
            )
        )
        self.connection.commit()
        row = self.cursor.fetchone()

        if not row:
            return await ctx.deny(
                "No welcome message to **edit!**"
            )

        builder = Builder(flags)
        embed_json = json.dumps(builder.create().to_dict())

        self.cursor.execute(
            '''
            REPLACE INTO welcomes(
                guild,
                channel,
                content,
                embed
            )
            VALUES (
                ?, ?, ?, ?
            )
            ''',
            (
                ctx.guild.id,
                channel.id or row[0],
                content or row[1],
                embed_json or row[2]
            )
        )
        self.connection.commit()
        
        return await ctx.send(
            embed=builder.create(
                ctx.author
            )
        )


    @welcome.command(
        name = "view",
        brief = "View the current welcome message",
        usage=None,
        example=None
    )
    @cooldown(1, 5, BucketType.user)
    async def view(
        self: Welcome,
        ctx: Context
    ) -> Message:
        """
        Views the current welcome message.

        Parameters
        ----------
        ctx : Context
            The context of the command invoked.

        Returns
        -------
        Message
            A message displaying the current welcome message.
        """
        self.cursor.execute(
            '''
            SELECT content, embed 
            FROM welcomes 
            WHERE guild = ?
            ''',
            (
                ctx.guild.id,
            )
        )
        self.connection.commit()
        row = self.cursor.fetchone()

        if row:
            content, embed_json = row
            builder = Builder()

            content = builder.replace_placeholders(
                content, 
                builder.mapping(
                    user=ctx.author,
                    message=ctx.message
                )
            )

            embed = Embed.from_dict(
                builder.replace_placeholders(
                    json.loads(embed_json),
                    builder.mapping(
                        user=ctx.author,
                        message=ctx.message
                    )
                )
            )
            return await ctx.send(
                content=content,
                embed=embed
            )
        
        return await ctx.deny(
            "No welcome message **set**!"
        )


    @welcome.command(
        name = "remove",
        brief = "Remove a welcome message",
        usage=None,
        example=None
    )
    @cooldown(1, 5, BucketType.user)
    async def remove(
        self: Welcome,
        ctx: Context
    ) -> Message:
        """
        Removes the current welcome message.

        Parameters
        ----------
        ctx : Context
            The context of the command invoked.

        Returns
        -------
        Message
            A message confirming the removal of the welcome message.
        """
        self.cursor.execute(
            '''
            DELETE FROM welcomes 
            WHERE guild = ?
            ''',
            (
                ctx.guild.id,
            )
        )
        self.connection.commit()
        
        return await ctx.approve(
            "Welcome message **removed!**"
        )


    @Cog.listener()
    async def on_member_join(
        self: Welcome, 
        member: Member
    ) -> None:
        """
        Sends a welcome message when a new member joins.

        Parameters
        ----------
        member : Member
            The member that has joined the server.
        """
        self.cursor.execute(
            '''
            SELECT channel, content, embed 
            FROM welcomes 
            WHERE guild = ?
            ''',
            (
                member.guild.id,
            )
        )
        self.connection.commit()
        row = self.cursor.fetchone()

        if row:
            channel_id, content, embed_json = row
            channel = self.bot.get_channel(channel_id)

            builder = Builder()
            content = builder.replace_placeholders(
                content, 
                builder.mapping(
                    user=member
                )
            )

            embed = Embed.from_dict(
                builder.replace_placeholders(
                    json.loads(embed_json),
                    builder.mapping(
                        user=member,
                    )
                )
            )
            return await channel.send(
                content=content,
                embed=embed
            )


async def setup(
    bot: Template
) -> Cog:
    """
    Sets up the Welcome cog and creates the necessary SQLite table.

    Parameters
    ----------
    bot : Template
        The bot instance to add the cog to.

    Returns
    -------
    Cog
        The initialized Welcome cog.
    """
    Welcome.cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS welcomes (
            guild INTEGER NOT NULL,
            channel INTEGER NOT NULL,
            content TEXT,
            embed TEXT,
            PRIMARY KEY (guild)
        )
        '''
    )
    Welcome.connection.commit()
    
    return await bot.add_cog(
        Welcome(
            bot
        )
    )