from __future__ import annotations

from discord import Member, Embed, utils, Message
from typing import Optional, Dict, Union


class Builder:
    def __init__(
        self: Builder, 
        flags: str = None
    ) -> None:
        """
        Initializes a Builder instance.

        Parameters
        ----------
        flags : str, optional
            A string containing embed attributes formatted for parsing.
        """
        self.title = None
        self.description = None
        self.color = None
        self.url = None
        self.author = None
        self.footer = None
        self.thumbnail = None
        self.image = None

        if flags:
            self.parse(flags)


    def parse(
        self: Builder,
        flags: str
    ) -> Builder:
        """
        Parses a string of flags to set embed attributes.

        Parameters
        ----------
        flags : str
            The string of flags formatted as 'key:value'.

        Returns
        -------
        Builder
            The current Builder instance for method chaining.
        """
        attributes = flags.split("$v")
        for attribute in attributes:
            if attribute.strip().lower() == "{embed}":
                continue

            key, value = attribute.split(":", 1)
            key = key.strip().lower().strip("{}")
            value = value.strip().rstrip("}")

            if key == "title":
                self.title = value
            elif key == "description":
                self.description = value
            elif key == "color":
                self.color = int(value, 16)  # Assuming color is provided in hex format
            elif key == "url":
                self.url = value
            elif key == "author":
                self.author = value
            elif key == "footer":
                self.footer = value
            elif key == "thumbnail":
                self.thumbnail = value
            elif key == "image":
                self.image = value


    def mapping(
        self: Builder, 
        user: Optional[Member] = None, 
        message: Optional[Message] = None,
        level: Optional[int] = None,
        xp: Optional[int] = None
    ) -> Dict[str, Optional[str]]:
        """
        Maps placeholders to user and guild information.

        Parameters
        ----------
        user : Optional[Member], optional
            The user for whom the embed is being created.
        message : Optional[Message], optional
            The message related to the embed.
        level : Optional[int], optional
            The user's level for XP or leveling purposes.
        xp : Optional[int], optional
            The user's experience points.

        Returns
        -------
        Dict[str, Optional[str]]
            A dictionary mapping placeholders to their corresponding values.
        """
        if user:
            return {
                "{user.id}": user.id,
                "{user.mention}": user.mention,
                "{user.name}": user.name,
                "{user.display}": user.display_name,
                "{user.avatar}": user.avatar.url if user.avatar else None,
                "{user.display_avatar}": user.display_avatar.url,
                "{user.joined_at}": utils.format_dt(user.joined_at, style="R"),
                "{user.created_at}": utils.format_dt(user.created_at, style="R"),
                "{guild.id}": user.guild.id,
                "{guild.name}": user.guild.name,
                "{guild.icon}": user.guild.icon.url if user.guild.icon else None,
                "{guild.membercount}": user.guild.member_count,
                "{guild.boost_count}": user.guild.premium_subscription_count,
                "{guild.boost_tier}": user.guild.premium_tier,
            }

        if level:
            return {
                "{level}": str(level),
                "{level.previous}": str(level-1)
            }
        
        if xp:
            return {
                "{xp}": str(xp),
                "{xp.previous}": str(xp-1)
            }

        if message:
            return {
                "{message.content}": message.content,
                "{message.url}": message.jump_url,
                "{message.created_at}": utils.format_dt(message.created_at, style="R"),
            }

        return {}


    def replace_placeholders(
        self: Builder, 
        text: Union[str, dict, list], 
        mappings: dict
    ) -> Union[str, dict, list]:
        """
        Replaces placeholders in a given text with corresponding values from mappings.

        Parameters
        ----------
        text : Union[str, dict, list]
            The text, dictionary, or list containing placeholders to replace.
        mappings : dict
            A dictionary mapping placeholders to their replacement values.

        Returns
        -------
        Union[str, dict, list]
            The text with placeholders replaced, or the original structure if no replacements were made.
        """
        if isinstance(text, str):
            for placeholder, value in mappings.items():
                if value:
                    text = text.replace(
                        placeholder,
                        str(value)
                    )
            return text

        elif isinstance(text, dict):
            return {
                key: self.replace_placeholders(
                    value,
                    mappings
                )
                for key, value in text.items()
            }

        elif isinstance(text, list):
            return [
                self.replace_placeholders(
                    item,
                    mappings
                ) for item in text
            ]

        return text


    def create(
        self: Builder, 
        user: Optional[Member] = None, 
        message: Optional[Message] = None,
        level: Optional[int] = None,
        xp: Optional[int] = None
    ) -> Embed:
        """
        Creates an Embed object using the attributes set in the Builder instance.

        Parameters
        ----------
        user : Optional[Member], optional
            The user for whom the embed is being created.
        message : Optional[Message], optional
            The message related to the embed.
        level : Optional[int], optional
            The user's level for XP or leveling purposes.
        xp : Optional[int], optional
            The user's experience points.

        Returns
        -------
        Embed
            The constructed Embed object with all attributes populated.
        """
        mappings = self.mapping(
            user=user, 
            message=message, 
            level=level, 
            xp=xp
        )

        def replace_attr(attr):
            return self.replace_placeholders(
                text=attr, 
                mappings=mappings
            ) if attr else None

        embed = Embed(
            title=replace_attr(self.title),
            description=replace_attr(self.description),
            color=self.color,
            url=self.url
        )

        if (
            author := replace_attr(
                self.author
            )
        ):
            embed.set_author(name=author)
        if (
            footer := replace_attr(
                self.footer
            )
        ):
            embed.set_footer(text=footer)
        if (
            thumbnail := replace_attr(
                self.thumbnail
            )
        ):
            embed.set_thumbnail(url=thumbnail)
        if (
            image := replace_attr(
                self.image
            )
        ):
            embed.set_image(url=image)

        return embed