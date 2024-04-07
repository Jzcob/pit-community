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

class Hypixel(commands.Cog):
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

            mojang = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{ign}")
            data = requests.json(mojang)
            uuid = data['id']
            hypixel = requests.get(f"https://api.hypixel.net/player?key={os.getenv('api_key')}&uuid={uuid}")
            data = requests.json(hypixel)
            if data['player'] == None:
                embed = discord.Embed(title="Hypixel Stats", description=f"**{ign}** is not a valid player!", color=0x00ff00)
                await msg.edit(embed=embed)
                return
            else:
                if ign.lower() == "technoblade":
                    embed = discord.Embed(description=f"**{ign}** 👑🐷 o7", color=0x00ff00)
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
                lastLogin = data['player']['lastLogin']
                lastLogin = datetime.datetime.fromtimestamp(lastLogin/1000.0)
                lastLogin = lastLogin.strftime("%m/%d/%Y, %H:%M:%S")
                lastLogout = data['player']['lastLogout']
                lastLogout = datetime.datetime.fromtimestamp(lastLogout/1000.0)
                lastLogout = lastLogout.strftime("%m/%d/%Y, %H:%M:%S")
                hypixelURL = data['plaer']['socialMedia']['links']['HYPIXEL']
                #https://replit.com/@Jzcob/hypixel
                embed.author(name=f"{ign}'s Hypixel Stats", url=hypixelURL)
                embed.add_field(name="Network Level", value=f"{networkLevel}", inline=False)
                embed.add_field(name="Karma", value=f"{karma}", inline=False)
                embed.add_field(name="First Login", value=f"{firstLogin}", inline=False)
                embed.add_field(name="Last Login", value=f"{lastLogin}", inline=False)
                embed.add_field(name="Last Logout", value=f"{lastLogout}", inline=False)
                await msg.edit(embed=embed)
        except:
            error_channel = self.bot.get_channel(config.error_channel)
            string = f"{traceback.format_exc()}"
            await error_channel.send(f"```{string}```")


async def setup(bot):
    await bot.add_cog(Hypixel(bot), guilds=[discord.Object(id=882708221697863434)])
        
    