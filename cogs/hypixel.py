import discord
from discord.ext import commands
import requests
from discord import app_commands
import datetime
import os
import math
import traceback
from dotenv import load_dotenv
import config
load_dotenv()

class hypixel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('LOADED: `hypixel.py`')
    
    @app_commands.command(name="hypixel", description="Get hypixel stats")
    async def hypixel(self, interaction: discord.Interaction, ign: str):
        try:
            await interaction.response.defer()
            msg = await interaction.original_response()

            url = f"https://api.hypixel.net/player?key={os.getenv('api_key')}&name={ign}"
            dataGet = requests.get(url)
            data = dataGet.json()
            if data['success'] == False:
                if data['cause'] == "You have already looked up this name recently":
                    embed = discord.Embed(title="Hypixel Stats", description=f"**{ign}** has already been looked up recently!", color=0x00ff00)
                    await msg.edit(embed=embed)
                    return

            uuid = data['player']['uuid']
            hypixel = f"https://api.hypixel.net/player?key={os.getenv('api_key')}&uuid={uuid}"
            dataGet = requests.get(hypixel)
            data = dataGet.json()
            ign = data['player']['displayname']
            if data['player'] == None:
                embed = discord.Embed(title="Hypixel Stats", description=f"**{ign}** is not a valid player!", color=0x00ff00)
                await msg.edit(embed=embed)
                return
            else:
                if ign.lower() == "technoblade":
                    embed = discord.Embed(description=f"**Technoblade** 👑🐷 o7", color=0x00ff00)
                elif ign.lower() == "jzcob":
                    embed = discord.Embed(title="Hypixel Stats", description=f"**{ign}** 👀 Oh hey thats my developer!", color=0x00ff00)
                else:
                    embed = discord.Embed(title="Hypixel Stats", description=f"**{ign}**'s Hypixel Stats", color=0x00ff00)
                networkXP = data['player']['networkExp']
                networkLevel = round((math.sqrt((2 * networkXP) + 30625) / 50) - 2.5)
                karma = data['player']['karma']
                firstLogin = data['player']['firstLogin']
                firstLogin = datetime.datetime.fromtimestamp(firstLogin/1000.0)
                firstLogin = firstLogin.strftime("%m/%d/%Y, %H:%M:%S")
                #https://replit.com/@Jzcob/hypixel
                embed.set_author(name=f"{ign}'s Hypixel Stats")
                embed.add_field(name="Network Level", value=f"{networkLevel}", inline=False)
                embed.add_field(name="Karma", value=f"{karma:,}", inline=False)
                embed.add_field(name="First Login", value=f"{firstLogin}", inline=False)
                await msg.edit(embed=embed)
        except:
            error_channel = self.bot.get_channel(config.error_channel)
            string = f"{traceback.format_exc()}"
            await error_channel.send(f"```{string}```")


async def setup(bot):
    await bot.add_cog(hypixel(bot), guilds=[discord.Object(id=config.server_id)])
        
    