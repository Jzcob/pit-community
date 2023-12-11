import discord
from discord.ext import commands
from discord import app_commands, TextStyle
import config
from dotenv import load_dotenv
import mysql.connector
import os
import json
load_dotenv()

db = mysql.connector.connect(
    host=os.getenv("punishments_host"),
    user=os.getenv("punishments_user"),
    password=os.getenv("punishments_password"),
    database=os.getenv("punishments_database")
)
cursor = db.cursor()
appeals_channel_id = 1179230717465608263
class AppealModal(discord.ui.Modal, title="Appeal a punishment"):
    punishmentReason = discord.ui.TextInput(label="What is your punishment reason?", placeholder="I was warned because I was spamming a lot", min_length=10, style=TextStyle.long, required=True)
    understanding = discord.ui.TextInput(label="Do you understand why you were punished?", placeholder="Please explain why you were punished.", min_length=10, style=TextStyle.long, required=True)
    why = discord.ui.TextInput(label="Why should you be unpunished?", placeholder="Please explain why you should be unpunished.", min_length=10, style=TextStyle.long, required=True)
    justified = discord.ui.TextInput(label="Do you think your punishment was justified?", min_length=50, style=TextStyle.long, required=True)
    async def on_submit(self, interaction: discord.Interaction):
        try:
            appealForum = interaction.client.get_channel(appeals_channel_id)
            embed = discord.Embed(title=f"{interaction.user.name}'s Appeal", color=0x00ff00)
            embed.add_field(name="Punishment Reason", value=self.punishmentReason.value, inline=False)
            embed.add_field(name="Understanding", value=self.understanding.value, inline=False)
            embed.add_field(name="Why should you be unpunished?", value=self.why.value, inline=False)
            embed.add_field(name="Do you think your punishment was justified?", value=self.justified.value, inline=False)
            embed.set_thumbnail(url=interaction.user.avatar)
            await appealForum.create_thread(name=f"{interaction.user.name}'s Appeal",embed=embed)
            g = open("appealed.json", "r")
            data = json.load(g)
            appealed = {
                **data,
                f"{interaction.user.id}": True
            }
            g = open("appealed.json", "w")
            json.dump(appealed, g)
            g.close()
            return await interaction.response.send_message(f"Your appeal has been submitted.\n\nYou will be contacted by me <@279409843964608514> about the result of your information. If needed our staff will contact you if we need more information.", ephemeral=True)

        except Exception as e:
            error_channel = interaction.client.get_channel(config.error_channel)
            await error_channel.send(f"```Error in appeal modal\n{e}\n```")
            await interaction.response.send_message("An error occured while submitting your appeal. Bot Devs have been alerted.", ephemeral=True)

class appeals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("LOADED: `appeals.py`")
    
    @app_commands.command(name="appeal", description="Appeal a punishment.")
    @app_commands.describe(type="What is the punishment type?")
    @app_commands.choices(type=[
        discord.app_commands.Choice(name="Warn", value="warn"),
        discord.app_commands.Choice(name="Kick", value="kick"),
        discord.app_commands.Choice(name="Ban", value="ban"),
        discord.app_commands.Choice(name="Timeout", value="timeout")
    ])
    async def appeal(self, interaction: discord.Interaction, type: discord.app_commands.Choice[str]):
        try:
            try:
                cursor.execute(f"SELECT * FROM warnings WHERE user_id = {interaction.user.id}")
                result = cursor.fetchone()
            except:
                pass
            try:
                cursor.execute(f"SELECT * FROM kicks WHERE user_id = {interaction.user.id}")
                result2 = cursor.fetchone()
            except:
                pass
            try:
                cursor.execute(f"SELECT * FROM bans WHERE user_id = {interaction.user.id}")
                result3 = cursor.fetchone()
            except:
                pass
            try:
                cursor.execute(f"SELECT * FROM timeouts WHERE user_id = {interaction.user.id}")
                result4 = cursor.fetchone()
            except:
                pass
            if result is None and result2 is None and result3 is None and result4 is None:
                return await interaction.response.send_message("You have no punishments to appeal.", ephemeral=True)
            if type.value == "warn":
                if result is None:
                    return await interaction.response.send_message("You have no warns to appeal.", ephemeral=True)
            if type.value == "kick":
                if result2 is None:
                    return await interaction.response.send_message("You have no kicks to appeal.", ephemeral=True)
            if type.value == "ban":
                if result3 is None:
                    return await interaction.response.send_message("You have no bans to appeal.", ephemeral=True)
            if type.value == "timeout":
                if result4 is None:
                    return await interaction.response.send_message("You have no timeouts to appeal.", ephemeral=True)
            await interaction.response.send_modal(AppealModal())
            f = open("appealed.json", "r")
            data = json.load(f)
            g = open("info.json", "r")
            info = json.load(g)
            if info['accepting-appeals'] == True:
                if data.get(f"{interaction.user.id}") == True:
                    return await interaction.response.send_message("You have already appealed a punishment.", ephemeral=True)
                else:
                    return await interaction.response.send_modal(AppealModal())
            else:
                return await interaction.response.send_message("We are not accepting appeals at this time.", ephemeral=True)
        except Exception as e:
            error_channel = interaction.client.get_channel(config.error_channel)
            await error_channel.send(f"```Error in `/appeal`\n{e}\n```")
    
    


async def setup(bot):
    await bot.add_cog(appeals(bot))