from __future__ import annotations

from lib.context import Context
from lib.bot import Template

from discord.ext.commands import (
    Cog, 
    command, 
    cooldown, 
    BucketType,
    Group
)
from discord import (
    Message, 
    Embed, 
    User
)

from typing import Optional


class Information(Cog):
    """
    Information Cog for "Template", handles various commands
    related to user information, server data, and bot usage.
    """
    def __init__(
        self: Information, 
        bot: Template
    ) -> None:
        """
        Initialize the Information cog.

        Parameters
        ----------
        bot : Template
            The bot instance.
        """
        self.bot: Template = bot

    
    @command(
        name = "help",
        brief = "Displays help information for commands and groups",
        usage = "help [command]",
        example = "help ban",
        aliases = ["h"]
    )
    @cooldown(1, 4, BucketType.user)
    async def help(
        self: Information,
        ctx: Context,
        name: Optional[str] = None
    ) -> Message:
        """
        Display help information for a specific command or for all commands.

        Parameters
        ----------
        ctx : Context
            The context of the command invocation.
        name : Optional[str], optional
            The name of the command to show help for, by default None.

        Returns
        -------
        Message
            A message containing help information in embed format.
        """
        avatar = (
            self.bot.user.avatar.url 
            if self.bot.user.avatar
            else self.bot.user.default_avatar.url
        )

        if name:
            command = self.bot.get_command(name)
            if command:
                ctx.command = command
                return await ctx.help()
    
        home = Embed(
            description=(
                f"**{self.bot.__doc__}**\n"
                f"> Use the **buttons** to navigate **command groups**\n"
                f"> Total of **{len(self.bot.commands)}** commands\n"
                f"> Total of **{len(self.bot.cogs)}** groups"
            ),
            color=0x2A2D31
        )
        home.set_footer(text = ",help <command>")
        home.set_author(
            name=self.bot.user.name, 
            icon_url=avatar
        )
        home.set_thumbnail(url=avatar)

        embeds = [home]
        cogs = self.bot.cogs

        for cog_name, cog in cogs.items():
            if cog_name.lower() in {"event", "developer"}:
                continue

            commands_list = []
            for command in cog.get_commands():
                if command.hidden:
                    continue

                commands_list.append(command.name)

                if isinstance(command, Group):
                    subcommands = [
                        subcommand.name 
                        for subcommand
                        in command.commands
                    ]
                    commands_list.extend(subcommands)

            embed = Embed(
                title=cog_name,
                description=f"```{', '.join(commands_list) if commands_list else 'N/A'}```",
                color=0x2A2D31
            )
            embed.set_thumbnail(url=avatar)
            embeds.append(embed)

        return await ctx.paginate(embeds)


    @command(
        name = "ui",
        brief = "User Interface",
        usage = "<user>",
        example = "rt",
        aliases = [
            "userinfo",
            "whois",
            "who"
        ]
    )
    @cooldown(1, 4, BucketType.user)
    async def ui(
        self: Information,
        ctx: Context, *,
        User: Optional[User] = None
    ) -> Message:
        """
        Display information about a specific user or the author.

        Parameters
        ----------
        ctx : Context
            The context of the command invocation.
        User : Optional[User], optional
            The user to display information for, by default None.

        Returns
        -------
        Message
            A message containing user information in embed format.
        """
        User = (
            User 
            if User 
            else ctx.author
        )
        
        embed = Embed(
            title = f"User: {User.display_name} ({User.name})",
            description = (
                f"Created at **{User.created_at.year}, {User.created_at.month}/{User.created_at.day}**\n"
                f"Joined at **{User.joined_at.year}, {User.joined_at.month}/{User.joined_at.day}**"
            ),
            color = 0x2A2D31
        ).set_thumbnail(
            url=(
                User.avatar.url if User.avatar 
                else User.default_avatar.url
            )
        ).set_footer(
            text = f"{User.name} ({User.id})",
            icon_url = User.avatar.url
        )
        
        return await ctx.send(embed=embed)


    @command(
        name = "av",
        brief = "View an avatar",
        usage = "<user>",
        example = "uh",
        aliases = [
            "avatar",
            "pfp",
            "ab",
            "ag"
        ]
    )
    @cooldown(1, 4, BucketType.user)
    async def av(
        self: Information,
        ctx: Context, *,
        User: Optional[User] = None
    ) -> Message:
        """
        Display the avatar of a user or the author.

        Parameters
        ----------
        ctx : Context
            The context of the command invocation.
        User : Optional[User], optional
            The user whose avatar is displayed, by default None.

        Returns
        -------
        Message
            A message with the user's avatar in embed format.
        """
        embed = Embed(
            title=(
                User.name if User
                else ctx.author.name
            ),
            color = 0x2A2D31
        ).set_image(
            url=(
                User.avatar.url if User
                else ctx.author.avatar.url
            )
        )
        return await ctx.send(embed=embed)


    @command(
        name = "bnr",
        brief = "View a banner",
        usage = "<user>",
        example = "uh",
        aliases = [
            "banner",
            "bne",
            "bsnner"
        ]
    )
    @cooldown(1, 4, BucketType.user)
    async def banner(
        self: Information,
        ctx: Context, *,
        User: Optional[User] = None
    ) -> Message:
        """
        Display the banner of a user or the author.

        Parameters
        ----------
        ctx : Context
            The context of the command invocation.
        User : Optional[User], optional
            The user whose banner is displayed, by default None.

        Returns
        -------
        Message
            A message with the user's banner in embed format.
        """
        embed = Embed(
            title=(
                User.name if User
                else ctx.author.name
            ),
            color = 0x2A2D31
        ).set_image(
            url=(
                User.banner.url if User
                else ctx.author.banner.url
            )
        )
        return await ctx.send(embed=embed)


    @command(
        name = "serveravatar",
        usage = "<user>",
        example = "uh",
        aliases = [
            "sav",
            "serverpfp",
            "spfp"
        ]
    )
    @cooldown(1, 4, BucketType.user)
    async def serveravatar(
        self: Information,
        ctx: Context,
        User: Optional[User]
    ) -> Message:
        """
        Display the server avatar of a user or the author.

        Parameters
        ----------
        ctx : Context
            The context of the command invocation.
        User : Optional[User], optional
            The user whose server avatar is displayed.

        Returns
        -------
        Message
            A message with the user's server avatar in embed format.
        """
        return await ctx.send(
            embed = Embed(
                title = (
                    User.name 
                    if User 
                    else ctx.author.name
                ),
                color = 0x2A2D31
            ).set_image(
                url = (
                    User.display_avatar
                    if User
                    else
                    ctx.author.display_avatar
                )
            )
        )


    @command(
        name = "guildicon",
        usage = "<id>",
        example = "123...",
        aliases = [
            "gicon",
            "servericon",
            "sicon"
        ]
    )
    @cooldown(1, 4, BucketType.user)
    async def guildicon(
        self: Information,
        ctx: Context,
        id: Optional[str] = None
    ) -> Message:
        """
        Display the server's icon or a specific guild icon by ID.

        Parameters
        ----------
        ctx : Context
            The context of the command invocation.
        id : Optional[str], optional
            The guild ID to retrieve the icon for, by default None.

        Returns
        -------
        Message
            A message with the server icon in embed format.
        """
        return await ctx.send(
            embed = Embed(
                title = ctx.guild.name,
                color = 0x2A2D31
            ).set_image(
                url = (
                    self.bot.get_guild(id).icon.url
                    if id
                    else ctx.guild.icon.url
                )
            )
        )


    @command(
        name = "guildbanner",
        usage = "<id>",
        example = "123...",
        aliases = [
            "gbanner",
            "serverbanner",
            "sbanner"
        ]
    )
    @cooldown(1, 4, BucketType.user)
    async def guildbanner(
        self: Information,
        ctx: Context,
        id: Optional[str] = None
    ) -> Message:
        """
        Display the server's banner or a specific guild banner by ID.

        Parameters
        ----------
        ctx : Context
            The context of the command invocation.
        id : Optional[str], optional
            The guild ID to retrieve the banner for, by default None.

        Returns
        -------
        Message
            A message with the server banner in embed format.
        """
        return await ctx.send(
            embed = Embed(
                title = ctx.guild.name,
                color = 0x2A2D31
            ).set_image(
                url = (
                    self.bot.get_guild(id).banner.url
                    if id
                    else ctx.guild.banner.url
                )
            )
        )


async def setup(
    bot: Template
) -> None:
    """
    Add the Information cog to the bot.

    Parameters
    ----------
    bot : Template
        The bot instance to add the cog to.
    """
    await bot.add_cog(Information(bot))