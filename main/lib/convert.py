from __future__ import annotations

from typing import Any

from discord.ext.commands import(
    MemberConverter,
    CommandError
)

from .context import Context


class Member(MemberConverter):
    """
    A custom member converter that extends the default MemberConverter.

    Raises:
        CommandError: If the member fails the checks.
    """
    async def convert(
        self: Member,
        ctx: Context,
        argument: Any
        
    ) -> Member:
        """
        Converts an argument into a Discord member while performing 
        additional checks to verify the command issuer's authority.

        Args:
            ctx (Context): The command context in which the conversion is taking place.
            argument (Any): The argument that needs to be converted into a member.

        Returns:
            Member: The converted member object if all checks pass.

        Raises:
            CommandError: If the member being converted is the command author, 
                          the bot itself, the guild owner, or if the command 
                          author does not have a higher role than the member.
        """
        member = await super().convert(
            ctx = ctx, 
            argument = argument
        )

        if (
            member == ctx.author or
            member == ctx.bot.user or
            member == ctx.guild.owner or
            (
                member.top_role >= 
                ctx.author.top_role and 
                ctx.author != ctx.guild.owner
            )
        ):
            raise CommandError(
                "Failed to pass the necessary checks!"
            )

        return member