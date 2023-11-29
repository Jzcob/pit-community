import discord
from discord.ext import commands
from discord import app_commands, TextStyle
import os
import config
import json
import requests
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("dev_key")

db = mysql.connector.connect(
    host=os.getenv("punishments_host"),
    user=os.getenv("punishments_user"),
    password=os.getenv("punishments_password"),
    database=os.getenv("punishments_database")
)
cursor = db.cursor()

class verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"LOADED: `verify.py`")
    
    @app_commands.command(name="verify", description="Verify your minecraft account with the bot.")
    async def verify(self, interaction: discord.Interaction, ign: str):
        try:
            today = datetime.now()
            timestamp = today.strftime("%Y-%m-%d %H:%M:%S")
            mojangURl = f"https://api.mojang.com/users/profiles/minecraft/{ign}"
            response = requests.get(mojangURl)
            uuid = response.json()["id"]
            cursor.execute(f"SELECT * FROM verified WHERE user_id = {interaction.user.id}")
            result = cursor.fetchone()
            if result is None:
                hypixelURL = f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}"
                response = requests.get(hypixelURL)
                if response.json()["player"] is None:
                    await interaction.response.send_message("You must have played on Hypixel before to verify.", ephemeral=True)
                else:
                    pitPrestige = response.json()['player']['achievements']['pit_prestiges']
                    pitLevel = response.json()['player']['achievements']['pit_legendary']
                    pit = response.json()['player']['achievements']['pit_stats_ptl']
                    pit 
                    cursor.execute(f"INSERT INTO verified (user_id, uuid, timestamp) VALUES ({interaction.user.id}, '{uuid}', '{timestamp}')")
                    db.commit()
                    await interaction.response.send_message("You have been verified!", ephemeral=True)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"```Error in `/verify`\n{e}\n```")

async def setup(bot):
    await bot.add_cog(verify(bot), guilds=[discord.Object(id=config.server_id)])