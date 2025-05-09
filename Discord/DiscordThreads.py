import discord
from discord import Thread, TextChannel, Message
from typing import Optional

class DiscordThreads:
    def __init__(self, guild: discord.Guild) -> None:
        self.guild: discord.Guild = guild

    async def return_thread_channel(self, thread_id: int, create_if_not_found: bool,  parent_channel: TextChannel, thread_name: str, message: Optional[Message] = None) -> Optional[Thread]:
        thread = discord.utils.get(self.guild.threads, id=thread_id)
        if thread is None and create_if_not_found:
            if message is not None:
                thread = await parent_channel.create_thread(name=thread_name, message=message)
            else:
                # Note: Creating a thread without a message may only be supported for forum channels.
                thread = await parent_channel.create_thread(name=thread_name)
        return thread

    async def send_message_to_thread(self, thread_id: int, create_if_not_found: bool, parent_channel: TextChannel, thread_name: str, content: str, message: Optional[Message] = None) -> None:
        thread = await self.return_thread_channel(thread_id, create_if_not_found, parent_channel, thread_name, message)
        if thread is None:
            return
        await thread.send(content)

    async def clear_messages_in_thread(self, thread_id: int,  create_if_not_found: bool, parent_channel: TextChannel, thread_name: str, message: Optional[Message] = None) -> None:
        thread = await self.return_thread_channel(thread_id, create_if_not_found, parent_channel, thread_name, message)
        if thread is None:
            return
        await thread.purge()
