import discord
from discord import app_commands, TextStyle
from discord.ext import commands
import config
import json
import os
import requests
import mysql.connector
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

applications_channel_id = 1179232602855575572

class ApplicationModal(discord.ui.Modal, title="Staff Application", ):
    age = discord.ui.TextInput(label= "How old are you?", max_length= 2, required= True)
    whyStaff = discord.ui.TextInput(label= "Why do you want to become a staff member?", style=TextStyle.long, required= True)
    experience = discord.ui.TextInput(label= "Any past moderation/leadership experience?", style=TextStyle.long, required= True)
    question = discord.ui.TextInput(label="Your response to acceptance/denial?", style=TextStyle.long, required=True)
    time = discord.ui.TextInput(label="How much time can you lend to the server?", style=TextStyle.long, required=True)
    async def on_submit(self, interaction: discord.Interaction):
        try:
            cursor.execute(f"SELECT * FROM verified WHERE user_id = {interaction.user.id}")
            result = cursor.fetchone()
            uuid = result[1]
            url = f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}"
            r = requests.get(url)
            data = r.json()
            age = str(self.age.value)
            age = int(age)
            applicationForum = interaction.guild.get_channel(applications_channel_id)
            if age <= 13:
                embed = discord.Embed(title=f"{interaction.user.name}'s Staff Application",description="Warning this user is 13 or under", color=0xff0000)
                embed.add_field(name="IGN", value=data['player']['displayname'], inline=False)
                embed.add_field(name="Age", value=self.age.value, inline=False)
                embed.add_field(name="Why do you want to become a staff member?", value=self.whyStaff.value, inline=False)
                embed.add_field(name="Any past moderation/leadership experience?", value=self.experience.value, inline=False)
                embed.add_field(name="Your response to acceptance/denial?", value=self.question.value, inline=False)
                embed.add_field(name="How much time can you lend to the server?", value=self.time.value, inline=False)
                embed.set_thumbnail(url=interaction.user.avatar)
            else:
                embed = discord.Embed(title=f"{interaction.user.name}'s Staff Application", color=0x00ff00)
                embed.add_field(name="Age", value=self.age.value, inline=False)
                embed.add_field(name="IGN", value=data['player']['displayname'], inline=False)
                embed.add_field(name="Why do you want to become a staff member?", value=self.whyStaff.value, inline=False)
                embed.add_field(name="Any past moderation/leadership experience?", value=self.experience.value, inline=False)
                embed.add_field(name="Your response to acceptance/denial?", value=self.question.value, inline=False)
                embed.add_field(name="How much time can you lend to the server?", value=self.time.value, inline=False)
                embed.set_thumbnail(url=interaction.user.avatar)
            thread = await applicationForum.create_thread(name=f"{interaction.user.name}'s Staff Application", embed=embed)
            await thread.add_tag("Under Review")
            await interaction.response.send_message(f"Your application has been submitted.\n\nYou will be contacted by me <@279409843964608514> about the result of your information.\n# Please make sure that your privacy settings for direct messages are turned on for Pit Community.\nIf you have any questions feel free to make a ticket!", ephemeral=True)
            g = open("applied.json", "r")
            applied = json.load(g)
            applied = {
                **applied,
                f"{interaction.user.id}" : True
            }
            g = open("applied.json", "w")
            json.dump(applied, g)
            g.close()
            return
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in apply modal.\n{e}")

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

        if data["accepting-applications"] == True:
            f = open("info.json", "w")
            data["accepting-applications"] = False
            json.dump(data, f)
            f.close()
            await interaction.response.send_message("Applications are now closed.", ephemeral=True)
        else:
            f = open("info.json", "w")
            data["accepting-applications"] = True
            json.dump(data, f)
            f.close()
            await interaction.response.send_message("Applications are now open.", ephemeral=True)

    @app_commands.command(name="apply", description="Please make sure your DMs are open for this server before you submit your application!")
    async def apply(self, interaction: discord.Interaction):
        try:
            cursor.execute(f"SELECT * FROM verified WHERE user_id = {interaction.user.id}")
            result = cursor.fetchone()
            verified = False

            if result is None: # If they verified with other bots then they wont be in this db
                return await interaction.reponse.send_message("Please verify with `/verify`", ephemeral=True)
            else:
                uuid = result[1]
                verified = True
            
            if verified == True:
                f = open("info.json", "r")
                data = json.load(f)
                if data["accepting-applications"] == True:
                    g = open("applied.json", "r")
                    applied = json.load(g)
                    if str(interaction.user.id) in applied:
                        return await interaction.response.send_message("You have already applied.\nIf you think this is a mistake please make a ticket with `/ticket`", ephemeral=True)
                    else:
                        return await interaction.response.send_modal(ApplicationModal())
                else:
                    return await interaction.response.send_message("Applications are currently closed.", ephemeral=True)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in `/apply`.\n{e}")
    
    @app_commands.command(name="accept", description="Accept a user's application.")
    @commands.has_permissions(administrator=True)
    async def accept(self, interaction: discord.Interaction, user: discord.User):
        try:
            applicationForum = interaction.guild.get_channel(applications_channel_id)
            if interaction.channel.parent.id != applications_channel_id:
                return await interaction.response.send_message("This command can only be used in applications.", ephemeral=True)
            await user.send(f"Congratulations {user.mention}! Your application has been accepted.\nAn Administrator will contact you shortly.")
            await interaction.response.send_message(f"{user.mention}'s application has been accepted, this channel will now be locked and closed.", ephemeral=True)
            await applicationForum.edit(locked=True)
            a = open("applied.json", "r")
            applied = json.load(a)
            applied = {
                **applied,
                f"{user.id}" : False
            }
            a = open("applied.json", "w")
            json.dump(applied, a)
            a.close()
            await applicationForum.edit(archived=True)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in `/accept`.\n{e}")
    
    @app_commands.command(name="deny", description="Deny a user's application.")
    @commands.has_permissions(administrator=True)
    @app_commands.describe(reason="The reason for denial.")
    @app_commands.choices(reason=[
        app_commands.Choice(name="Not old enough", value="age"),
        app_commands.Choice(name="No experienced", value="experience"),
        app_commands.Choice(name="Not enough time", value="time"),
        app_commands.Choice(name="Not detailed enough", value="detailed")
    ])
    async def deny(self, interaction: discord.Interaction, user: discord.User, reason: app_commands.Choice[str]=None, custom_reason: str=None):
        if interaction.channel.parent.id != applications_channel_id:
            return await interaction.response.send_message("This command can only be used in applications.", ephemeral=True)
        if reason == None and custom_reason == None:
            return await interaction.response.send_message("Please provide a reason.", ephemeral=True)
        if reason == None:
            reason = custom_reason
            await user.send(f"Sorry {user.mention}, your application has been denied.\nReason: {reason}")
            await interaction.response.send_message(f"{user.mention}'s application has been denied, this channel will now be locked and closed.", ephemeral=True)
            await interaction.channel.edit(locked=True, archived=True)
        
        try:
            if reason.value == "age":
                await user.send(f"Sorry {user.mention}, your application has been denied.\nReason: {config.age}")
                await user.ban(reason="Underage")
                await interaction.response.send_message(f"{user.mention}'s application has been denied, this channel will now be locked and closed.", ephemeral=True)
                await interaction.channel.edit(locked=True, archived=True)
                return
            elif reason.value == "experience":
                await user.send(f"Sorry {user.mention}, your application has been denied.\nReason: {config.experience}")
                await interaction.response.send_message(f"{user.mention}'s application has been denied, this channel will now be locked and closed.", ephemeral=True)
                a = open("applied.json", "r")
                applied = json.load(a)
                applied = {
                    **applied,
                    f"{user.id}" : False
                }
                a = open("applied.json", "w")
                json.dump(applied, a)
                a.close()
                await interaction.channel.edit(locked=True, archived=True)
                return
            elif reason.value == "time":
                await user.send(f"Sorry {user.mention}, your application has been denied.\nReason: {config.time}")
                await interaction.response.send_message(f"{user.mention}'s application has been denied, this channel will now be locked and closed.", ephemeral=True)
                await interaction.channel.edit(locked=True, archived=True)
                a = open("applied.json", "r")
                applied = json.load(a)
                applied = {
                    **applied,
                    f"{user.id}" : False
                }
                a = open("applied.json", "w")
                json.dump(applied, a)
                a.close()
                return
            elif reason.value == "detailed":
                await user.send(f"Sorry {user.mention}, your application has been denied.\nReason: {config.detailed}")
                await interaction.response.send_message(f"{user.mention}'s application has been denied, this channel will now be locked and closed.", ephemeral=True)
                await interaction.channel.edit(locked=True, archived=True)
                a = open("applied.json", "r")
                applied = json.load(a)
                applied = {
                    **applied,
                    f"{user.id}" : False
                }
                a = open("applied.json", "w")
                json.dump(applied, a)
                a.close()
                return
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in `/deny`.\n{e}")


    @app_commands.command(name="toggle-appeals", description="Toggle whether or not appeals are open.")
    @commands.has_permissions(administrator=True)
    async def toggle_appeals(self, interaction: discord.Interaction):
        f = open("info.json", "r")
        data = json.load(f)

        if data["accepting-appeals"] == True:
            f = open("info.json", "w")
            data["accepting-appeals"] = False
            json.dump(data, f)
            f.close()
            await interaction.response.send_message("Appeals are now closed.", ephemeral=True)
        else:
            f = open("info.json", "w")
            data["accepting-appeals"] = True
            json.dump(data, f)
            f.close()
            await interaction.response.send_message("Appeals are now open.", ephemeral=True)

async def setup(bot):

    await bot.add_cog(applications(bot), guilds=[discord.Object(id=config.server_id)])