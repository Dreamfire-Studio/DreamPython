import discord
import uuid

class DiscordCore(discord.Client):
    callback_class = None

    def __init__(self, prefix, intents, callback_class):
        if intents is None:
            intents = discord.Intents.all()
        self.command_prefix = prefix
        self.callback_class = callback_class
        super().__init__(intents=intents)

    async def on_ready(self):
        print("Successfully logged in as {0.user}".format(self))

        for guild in self.guilds:
            func = getattr(self.callback_class, "on_ready")
            if func is not None and callable(func):
                await func(guild)

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith(self.command_prefix):
            command, *args = message.content[len(self.command_prefix):].split()
            func = getattr(self.callback_class, command, None)
            if func is not None and callable(func):
                await func(message, *args)
                return


class DiscordChannel:
    def __init__(self, guild):
        self.guild = guild

    async def return_text_channel(self, channel_id, create_if_not_found):
        channel = discord.utils.get(self.guild.text_channels, id=channel_id)
        if channel is None and create_if_not_found:
            channel = await self.guild.create_text_channel(str(uuid.uuid4()))
        return channel

    async def send_message_to_text_channel(self, channel_id, create_if_not_found, message):
        channel = await self.return_text_channel(channel_id, create_if_not_found)
        if channel is None:
            return
        await channel.send(message)