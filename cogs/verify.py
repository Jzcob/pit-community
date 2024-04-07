import discord
from discord.ext import commands
from discord import app_commands
import os
import config
import traceback
import requests
import mysql.connector
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("api_key")

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
            await interaction.response.defer()
            msg = await interaction.original_response()
            today = datetime.now()
            timestamp = today.timestamp()
            mojangURl = f"https://api.mojang.com/users/profiles/minecraft/{ign}"
            response = requests.get(mojangURl)
            uuid = response.json()["id"]
            cursor.execute(f"SELECT * FROM verified WHERE user_id = {interaction.user.id}")
            result = cursor.fetchone()
            unranked = discord.utils.get(interaction.guild.roles, id=config.unranked)
            vip = discord.utils.get(interaction.guild.roles, id=config.vip)
            vip_plus = discord.utils.get(interaction.guild.roles, id=config.vip_plus)
            mvp = discord.utils.get(interaction.guild.roles, id=config.mvp)
            mvp_plus = discord.utils.get(interaction.guild.roles, id=config.mvp_plus)
            mvp_plus_plus = discord.utils.get(interaction.guild.roles, id=config.mvp_plus_plus)
            prestige_I_IV = discord.utils.get(interaction.guild.roles, id=config.prestige_I_IV)
            prestige_V_IX = discord.utils.get(interaction.guild.roles, id=config.prestige_V_IX)
            prestige_X_XIV = discord.utils.get(interaction.guild.roles, id=config.prestige_X_XIV)
            prestige_XV_XIX = discord.utils.get(interaction.guild.roles, id=config.prestige_XV_XIX)
            prestige_XX_XXIV = discord.utils.get(interaction.guild.roles, id=config.prestige_XX_XXIV)
            prestige_XXV_XXIX = discord.utils.get(interaction.guild.roles, id=config.prestige_XXV_XXIX)
            prestige_XXX_XXXIV = discord.utils.get(interaction.guild.roles, id=config.prestige_XXX_XXXIV)
            prestige_XXXV_XXXIX = discord.utils.get(interaction.guild.roles, id=config.prestige_XXXV_XXXIX)
            prestige_XL_XLIV = discord.utils.get(interaction.guild.roles, id=config.prestige_XL_XLIV)
            prestige_XLV_XLVII = discord.utils.get(interaction.guild.roles, id=config.prestige_XLV_XLVII)
            prestige_XLIII_XLIX = discord.utils.get(interaction.guild.roles, id=config.prestige_XLIII_XLIX)
            prestige_L = discord.utils.get(interaction.guild.roles, id=config.prestige_L)
            og = discord.utils.get(interaction.guild.roles, id=config.og)
            ancient = discord.utils.get(interaction.guild.roles, id=config.ancient)
            veteran = discord.utils.get(interaction.guild.roles, id=config.veteran)
            achievement_hunter = discord.utils.get(interaction.guild.roles, id=config.achievement_hunter)
            lord_of_karma = discord.utils.get(interaction.guild.roles, id=config.lord_of_karma)
            network_lord = discord.utils.get(interaction.guild.roles, id=config.network_lord)
            network_master = discord.utils.get(interaction.guild.roles, id=config.network_master)
            no_life = discord.utils.get(interaction.guild.roles, id=config.no_life)
            displayname = ""
            if result is None:
                hypixelURL = f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}"
                response = requests.get(hypixelURL)
                if response.json()["player"] is None:
                    await interaction.response.send_message("You must have played on Hypixel before to verify.", ephemeral=True)
                else:
                    displayname = response.json()["player"]["displayname"]
                    socialMedia = response.json()['player']['socialMedia']['links']
                    if str(socialMedia['DISCORD']) != str(interaction.user.name):
                        return await msg.edit(content="Your discord account is not linked to your minecraft account.")
                    pitPrestige = response.json()['player']['achievements']['pit_prestiges']
                    if pitPrestige >= 0 and pitPrestige <= 4:
                        await interaction.user.add_roles(prestige_I_IV)
                    elif pitPrestige >= 5 and pitPrestige <= 9:
                        await interaction.user.add_roles(prestige_V_IX)
                    elif pitPrestige >= 10 and pitPrestige <= 14:
                        await interaction.user.add_roles(prestige_X_XIV)
                    elif pitPrestige >= 15 and pitPrestige <= 19:
                        await interaction.user.add_roles(prestige_XV_XIX)
                    elif pitPrestige >= 20 and pitPrestige <= 24:
                        await interaction.user.add_roles(prestige_XX_XXIV)
                    elif pitPrestige >= 25 and pitPrestige <= 29:
                        await interaction.user.add_roles(prestige_XXV_XXIX)
                    elif pitPrestige >= 30 and pitPrestige <= 34:
                        await interaction.user.add_roles(prestige_XXX_XXXIV)
                    elif pitPrestige >= 35 and pitPrestige <= 39:
                        await interaction.user.add_roles(prestige_XXXV_XXXIX)
                    elif pitPrestige >= 40 and pitPrestige <= 44:
                        await interaction.user.add_roles(prestige_XL_XLIV)
                    elif pitPrestige >= 45 and pitPrestige <= 47:
                        await interaction.user.add_roles(prestige_XLV_XLVII)
                    elif pitPrestige >= 48 and pitPrestige <= 49:
                        await interaction.user.add_roles(prestige_XLIII_XLIX)
                    elif pitPrestige == 50:
                        await interaction.user.add_roles(prestige_L)
                    else:
                        pass
                    try:
                        rank = response.json()['player']['newPackageRank']
                    except:
                        pass
                    if rank == None:
                        await interaction.user.add_roles(unranked)
                    else:
                        if rank == "VIP":
                            await interaction.user.add_roles(vip)
                        elif rank == "VIP_PLUS":
                            await interaction.user.add_roles(vip_plus)
                        elif rank == "MVP":
                            await interaction.user.add_roles(mvp)
                        elif rank == "MVP_PLUS":
                            try:
                                monthlyPackageRank = response.json()['player']['monthlyPackageRank']
                            except:
                                pass
                            if monthlyPackageRank == "SUPERSTAR":
                                await interaction.user.add_roles(mvp_plus_plus)
                            await interaction.user.add_roles(mvp_plus)
                        else:
                            await msg.edit(content="Please make a ticket with `/ticket` to get your rank.")
                    try:
                        karma = response.json()['player']['karma']
                    except:
                        pass
                    if karma >= 3000000:
                        await interaction.user.add_roles(lord_of_karma)
                    try:
                        achievement_points = response.json()['player']['achievementPoints']
                    except:
                        pass
                    if achievement_points >= 5000:
                        await interaction.user.add_roles(achievement_hunter)
                    try:
                        network_exp = response.json()['player']['networkExp']
                    except:
                        pass
                    if network_exp >= 13117500:
                        await interaction.user.add_roles(network_lord)
                    elif network_exp >= 79680000:
                        await interaction.user.add_roles(network_master)
                    try:
                        first_login = response.json()['player']['firstLogin']
                    except:
                        pass
                    three_half_yearsago = datetime.now() - timedelta(days=1278)
                    three_half_yearsago = three_half_yearsago.timestamp()
                    five_yearsago = datetime.now() - timedelta(days=1825)
                    five_yearsago = five_yearsago.timestamp()
                    if first_login <= 1365868800 and first_login >= 1397491200:
                        await interaction.user.add_roles(og)
                        if first_login <= three_half_yearsago:
                            await interaction.user.add_roles(veteran)
                        if first_login <= five_yearsago:
                            await interaction.user.add_roles(ancient)
                    cursor.execute(f"INSERT INTO verified (user_id, uuid, timestamp) VALUES ({interaction.user.id}, '{uuid}', {int(timestamp)})")
                    db.commit()
                    await msg.edit(content=f"You have been verified as ``{displayname}!")
            else:
                await msg.edit(content="You are already verified!")
        except:
            error_channel = self.bot.get_channel(config.error_channel)
            string = f"{traceback.format_exc()}"
            await error_channel.send(f"```{string}```")

async def setup(bot):
    await bot.add_cog(verify(bot), guilds=[discord.Object(id=config.server_id)])