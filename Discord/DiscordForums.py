import discord
from typing import Optional

class DiscordForums:
    """
    A helper class for managing forum channels and their threads.
    """

    def __init__(self, guild: discord.Guild):
        self.guild = guild

    async def get_forum_channel(self, channel_id: int) -> Optional[discord.ForumChannel]:
        """
        Retrieve a forum channel by its ID.
        Returns the forum channel if found, otherwise None.
        """
        channel = discord.utils.get(self.guild.channels, id=channel_id)
        if isinstance(channel, discord.ForumChannel):
            return channel
        return None

    async def create_forum_thread(self, forum_channel_id: int, name: str, content: str) -> Optional[discord.Thread]:
        """
        Create a new thread in the specified forum channel.
        The content becomes the first message in the thread.
        Returns the created thread if successful, otherwise None.
        """
        forum_channel = await self.get_forum_channel(forum_channel_id)
        if forum_channel is None:
            return None

        thread = await forum_channel.create_thread(name=name, content=content)
        return thread

    async def send_message_in_thread(self, thread_id: int, content: str) -> None:
        """
        Send a message to a thread with the specified thread ID.
        """
        thread = discord.utils.get(self.guild.threads, id=thread_id)
        if thread is not None:
            await thread.send(content)

    async def clear_messages_in_thread(self, thread_id: int) -> None:
        """
        Clear (purge) all messages in the thread with the specified thread ID.
        """
        thread = discord.utils.get(self.guild.threads, id=thread_id)
        if thread is not None:
            await thread.purge()

    async def get_thread_in_forum(self, forum_channel: discord.ForumChannel, thread_id: int, fetch_archived: bool = True) -> Optional[discord.Thread]:
        """
        Retrieve a thread by ID within a given forum channel.
        Searches active threads first, and if not found and fetch_archived is True,
        searches archived threads.
        Returns the thread if found, otherwise None.
        """
        thread = discord.utils.get(forum_channel.threads, id=thread_id)
        if thread is not None:
            return thread

        if fetch_archived:
            # Search public archived threads
            public_archived = await forum_channel.fetch_archived_threads(private=False)
            for t in public_archived.threads:
                if t.id == thread_id:
                    return t

            # Search private archived threads
            private_archived = await forum_channel.fetch_archived_threads(private=True)
            for t in private_archived.threads:
                if t.id == thread_id:
                    return t

        return None