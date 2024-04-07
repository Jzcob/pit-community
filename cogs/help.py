import discord
from discord.ext import commands
from discord import app_commands
import config
import traceback
from dotenv import load_dotenv

load_dotenv()

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("LOADED: `help.py`")
    
    @app_commands.command(name="help", description="Get help with the bot.")
    async def help(self, interaction: discord.Interaction):
        try:
            pass
        except:
            error_channel = self.bot.get_channel(config.error_channel)
            string = f"{traceback.format_exc()}"
            await error_channel.send(f"```{string}```")

async def setup(bot):
    await bot.add_cog(Help(bot))