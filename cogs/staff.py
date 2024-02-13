import discord
from discord.ext import commands
from discord import app_commands
import config

class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('LOADED: `staff.py`')
    
    @app_commands.command(name="staff", description="Get the staff of the server")
    async def staff(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Staff", description="These are the staff members of the server.", color=0x00ff00)
        embed.add_field(name="Owner", value="<@349719693264814092>", inline=False)
        embed.add_field(name="Admin", value="<@306570665694199809>", inline=False)
        embed.add_field(name="Developer", value=f"<@920797181034778655>", inline=False)
        embed.add_field(name="Moderator's", value="<@238762194320228352> <@403705883097563139> <@615124610379284481> <@422512146065391625>", inline=False)
        embed.add_field(name="Other Staff", value="<@631168537137905684>", inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Staff(bot), guilds=[discord.Object(id=config.server_id)])