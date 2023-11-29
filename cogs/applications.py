import discord
from discord import app_commands, TextStyle
from discord.ext import commands
import config
import json
import os
from dotenv import load_dotenv
load_dotenv()

applications_channel_id = 1179232602855575572
appeals_channel_id = 1179230717465608263

class ApplicationModal(discord.ui.View, title="Staff Application", description="Please answer the following questions to the best of your ability. \n\nPlease don't close this window until you're done answers do not save."):
    age = discord.ui.TextInput(label= "How old are you?", max_length= 2, required= True)
    whyStaff = discord.ui.TextInput(label= "Why do you want to become a staff member?", style=TextStyle.long, required= True)
    experience = discord.ui.TextInput(label= "Any past moderation/leadership experience?", style=TextStyle.long, required= True)
    question = discord.ui.TextInput(label="Your response to acceptance/denial?", style=TextStyle.long, required=True)
    time = discord.ui.TextInput(label="How much time can you lend to the server?", style=TextStyle.long, required=True)
    async def on_submit(self, interaction: discord.Interaction):
        

class applications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("LOADED: `applications.py`")
    
    @app_commands.command(name="toggle-applications", description="Toggle whether or not applications are open.")
    @commands.has_permissions(administrator=True)
    async def toggle_applications(self, interaction: discord.Interaction):
        f = open("info.json", "r")
        data = json.load(f)
        if data["applications"] == True:
            f = open("info.json", "w")
            data["applications"] = False
            json.dump(data, f)
            f.close()
            await interaction.response.send_message("Applications are now closed.", ephemeral=True)
        else:
            f = open("info.json", "w")
            data["applications"] = True
            json.dump(data, f)
            f.close()
            await interaction.response.send_message("Applications are now open.", ephemeral=True)

    @app_commands.command(name="apply", description="Apply for staff.")
    async def apply(self, interaction: discord.Interaction):
        f = open("info.json", "r")
        data = json.load(f)
        if data["applications"] == True:
            g = open("applied.json", "r")
            applied = json.load(g)
            if str(interaction.user.id) in applied:
                await interaction.response.send_message("You have already applied.\nIf you think this is a mistake please make a ticket with `/ticket`", ephemeral=True)
            
            await interaction.response.send_message("", ephemeral=True)
        else:
            await interaction.response.send_message("Applications are currently closed.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(applications(bot), guilds=[discord.Object(id=config.server_id)])