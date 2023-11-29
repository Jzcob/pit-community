import discord
from discord.ext import commands
from discord import app_commands
import config
from dotenv import load_dotenv
load_dotenv()

class general(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("LOADED: `general.py`")
    
    @commands.Cog.listener()
    async def on_join(self, member: discord.Member):
        try:
            if member.guild.id == config.server_id:
                await member.add_roles(member.guild.get_role(config.members))
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"```Error in `on_join`\n{e}\n```")
    
    @app_commands.command(name="send", description="Make the bot say something.")
    @app_commands.checks.has_any_role(config.moderator, config.administrators, config.transparent_admin, config.true_admin)
    async def say(self, interaction: discord.Interaction, *, message: str, channel: discord.TextChannel = None):
        try:
            if channel == None:
                channel = interaction.channel
                await channel.send(message)
                await interaction.response.send_message(f"Sent message to {channel.mention}", ephemeral=True)
            else:
                await channel.send(message)
                await interaction.response.send_message(f"Sent message to {channel.mention}", ephemeral=True)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"```Error in `/send`\n{e}\n```")

async def setup(bot):
    await bot.add_cog(general(bot), guilds=[discord.Object(id=config.server_id)])