import discord
from discord import app_commands
from discord.ext import commands
import config
import datetime
import re

class advertise(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("LOADED: `advertise.py`")
    
    @app_commands.command(name="advertise", description="Advertise a link")
    async def advertise(self, interaction: discord.Interaction, url: str):
        user = interaction.user
        isStaff = user.top_role
        roles = ["Admin", "Founder", "Developer", "Transparent Admin"]
        if any(role in isStaff for role in roles):
            channel = self.bot.get_channel(922273598801084506)
            await channel.send(url)
        else:
            if re.search(r"(https?://)?(www.)?(discord.(gg|io|me|li)|discordapp.com/invite)/.+[a-z]", url):
                channel = self.bot.get_channel(922273598801084506)
                view = Buttons()
                await channel.send(url, view=view)
                await interaction.response.send_message("Your advertisement has been sent to the staff team for approval.", ephemeral=True)
            else:
                await interaction.response.send_message("Invalid URL", ephemeral=True)
    
async def setup(bot):
    bot.add_cog(advertise(bot))

class Buttons(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label="Approve", style=discord.ButtonStyle.green, custom_id="approve"))
        self.add_item(discord.ui.Button(label="Deny", style=discord.ButtonStyle.red, custom_id="deny"))
    
    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green)
    async def approve(self, button: discord.ui.Button, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(1234964528140390480)
        await channel.send(interaction.message.content)   
        await interaction.message.delete()     
        await interaction.response.send_message("Approved", ephemeral=True)
    
    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.message.delete()
        await interaction.response.send_message("Denied", ephemeral=True)

async def setup(bot):
    await bot.add_cog(advertise(bot))