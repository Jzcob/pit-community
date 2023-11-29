import discord
from discord.ext import commands
from discord import app_commands
import config
from dotenv import load_dotenv
load_dotenv()

bad_users = {}

class cantCount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("LOADED: `cantCount.py`")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        try:
            if message.channel.id == 922274486852661278:
                lastmessage = [msg async for msg in message.channel.history(limit=2)][1]
                if message.author.id == lastmessage.author.id:
                    if message.author.id in bad_users:
                        bad_users[message.author.id] += 1
                    else:
                        bad_users[message.author.id] = 1
                    if bad_users[message.author.id] >= 5:
                        try:
                            cantCount = discord.utils.get(message.guild.roles, id=778499740664070154)
                            await message.author.add_roles(cantCount, reason="Spamming in #counting")
                        except Exception as e:
                            error_channel = self.bot.get_channel(config.error_channel)
                            await error_channel.send(f"```Error in cantCount.py\n{e}\n```")
                    await message.delete()
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"```Error in cantCount event\n{e}\n```")

async def setup(bot):
    await bot.add_cog(cantCount(bot))