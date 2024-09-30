from __future__ import annotations

from typing import List, ClassVar, TypedDict

from discord.ext.commands import Context
from discord import Embed, ButtonStyle, Interaction
from discord.ui import Button, View

import json


class Config(TypedDict):
    left: str
    right: str
    stop: str
    warn: str


class Paginator(View):
    """
    Custom Paginator class for navigating through a list of embeds.
    
    Attributes
    ----------
    ctx : Context
        The context of the command.
    embeds : List[Embed]
        A list of embeds to paginate through.
    current_page : int
        The index of the currently displayed embed.
    
    Methods
    -------
    _left(interaction: Interaction)
        Callback for the left button to move to the previous page.
    _right(interaction: Interaction)
        Callback for the right button to move to the next page.
    _stop(interaction: Interaction)
        Callback for the stop button to end pagination and remove the view.
    update_embed(interaction: Interaction)
        Updates the embed being shown with the current page's embed.
    """
    
    config: ClassVar[Config] = json.load(
        open(
            file="data/object.json",
            mode="r"   
        )
    )
    left: ClassVar[str] = config["left"]
    stop: ClassVar[str] = config["stop"]
    right: ClassVar[str] = config["right"]
    warn: ClassVar[str] = config["warn"]


    def __init__(
        self: Paginator, 
        ctx: Context, 
        embeds: List[Embed]
    ) -> None:
        super().__init__()
        self.ctx = ctx
        self.embeds = embeds
        self.current_page = 0


        self.left_button = Button(
            style=ButtonStyle.primary, 
            emoji=self.left
        )
        self.stop_button = Button(
            style=ButtonStyle.danger, 
            emoji=self.stop
        )
        self.right_button = Button(
            style=ButtonStyle.primary, 
            emoji=self.right
        )

        self.left_button.callback = self._left
        self.stop_button.callback = self._stop
        self.right_button.callback = self._right

        self.add_item(self.left_button)
        self.add_item(self.stop_button)
        self.add_item(self.right_button)


    async def _left(
        self: Paginator, 
        interaction: Interaction
    ) -> None:
        """
        Moves to the previous page
        """
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message(
                embed = Embed(
                    description = f"{self.warn} {interaction.user.mention} This is not **your** paginator!",
                    color = 0x2A2D31
                ),
                ephemeral=True
            )

        self.current_page = (self.current_page - 1) % len(self.embeds)
        await self.update_embed(interaction)


    async def _right(
        self: Paginator, 
        interaction: Interaction
    ) -> None:
        """
        Moves to the next page
        """
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message(
                embed = Embed(
                    description = f"{self.warn} {interaction.user.mention} This is not **your** paginator!",
                    color = 0x2A2D31
                ),
                ephemeral=True
            )

        self.current_page = (self.current_page + 1) % len(self.embeds)
        await self.update_embed(interaction)


    async def _stop(
        self: Paginator, 
        interaction: Interaction
    ) -> None:
        """
        Stops the pagination and removes the view
        """
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message(
                embed = Embed(
                    description = f"{self.warn} {interaction.user.mention} This is not **your** paginator!",
                    color = 0x2A2D31
                ),
                ephemeral=True
            )

        await interaction.response.edit_message(view=None)


    async def update_embed(
        self: Paginator, 
        interaction: Interaction
    ) -> None:
        """
        Updates the embed being displayed based on the current page
        """
        embed = self.embeds[self.current_page]
        embed.set_footer(
            text=f"Page {self.current_page + 1}/{len(self.embeds)}",
            icon_url=self.ctx.bot.user.avatar.url
        )
        await interaction.response.edit_message(
            embed=embed, 
            view=self
        )