import discord
from discord.ext import commands
from discord import app_commands
import config
from dotenv import load_dotenv
import mysql.connector
import os
import requests
load_dotenv()

api_key = os.getenv("dev_key")

db = mysql.connector.connect(
    host=os.getenv("punishments_host"),
    user=os.getenv("punishments_user"),
    password=os.getenv("punishments_password"),
    database=os.getenv("punishments_database")
)
cursor = db.cursor()

class general(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("LOADED: `general.py`")
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
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
    
    @app_commands.command(name="send-embed", description="Make the bot say something in an embed.")
    @app_commands.checks.has_any_role(config.moderator, config.administrators, config.transparent_admin, config.true_admin)
    async def sayEmbed(self, interaction: discord.Interaction, *, title: str, message: str, channel: discord.TextChannel = None):
        try:
            if channel == None:
                channel = interaction.channel
                embed = discord.Embed(title=title, description=message, color=0x00ff00)
                await channel.send(embed=embed)
                await interaction.response.send_message(f"Sent message to {channel.mention}", ephemeral=True)
            else:
                embed = discord.Embed(title=title, description=message, color=0x00ff00)
                await channel.send(embed=embed)
                await interaction.response.send_message(f"Sent message to {channel.mention}", ephemeral=True)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"```Error in `/send-embed`\n{e}\n```")
    
    @app_commands.command(name="edit-embed", description="Edit an embed.")
    @app_commands.checks.has_any_role(config.moderator, config.administrators, config.transparent_admin, config.true_admin)
    async def editEmbed(self, interaction: discord.Interaction, message_id: str, title: str, message: str, channel: discord.TextChannel = None):
        try:
            if channel == None:
                channel = interaction.channel
                embed = discord.Embed(title=title, description=message, color=0x00ff00)
                msg = await channel.fetch_message(message_id)
                await msg.edit(embed=embed)
                await interaction.response.send_message(f"Edited message in {channel.mention}", ephemeral=True)
            else:
                embed = discord.Embed(title=title, description=message, color=0x00ff00)
                msg = await channel.fetch_message(message_id)
                await msg.edit(embed=embed)
                await interaction.response.send_message(f"Edited message in {channel.mention}", ephemeral=True)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"```Error in `/edit-embed`\n{e}\n```")
    
    @app_commands.command(name="who-is", description="Get users in-game name.")
    @app_commands.checks.has_any_role(config.moderator, config.administrators, config.transparent_admin, config.true_admin)
    async def whoIs(self, interaction: discord.Interaction, user: discord.User):
        try:
            cursor.execute(f"SELECT * FROM verified WHERE user_id = {user.id}")
            result = cursor.fetchone()
            uuid = result[1]
            url = f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}"
            response = requests.get(url)
            data = response.json()
            ign = data["player"]["displayname"]
            if result is None:
                embed = discord.Embed(description=f"{user.mention} has not verified!", color=0x00ff00)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(description=f"`{ign}` in-game.", color=0x00ff00)
                embed.set_author(name=user.name, icon_url=user.display_avatar)
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"```Error in `/who-is`\n{e}\n```")

async def setup(bot):
    await bot.add_cog(general(bot), guilds=[discord.Object(id=config.server_id)])