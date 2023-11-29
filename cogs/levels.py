import discord
from discord.ext import commands
from discord import app_commands
import random
import mysql.connector
import os
import config
from config import level_limit as limit
from dotenv import load_dotenv
import asyncio
import discord
from discord.ext import commands
from discord.ui import Button
load_dotenv()

db = mysql.connector.connect(
    host=os.getenv("punishments_host"),
    user=os.getenv("punishments_user"),
    password=os.getenv("punishments_password"),
    database=os.getenv("punishments_database")
)
cursor = db.cursor()

playing = discord.Activity(type=discord.ActivityType.playing, name="The Pit")

class Confirm(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
    
    @discord.ui.button(label= "Confirm", style= discord.ButtonStyle.red, custom_id= 'confirmmm')
    async def confirm_button2(self, interaction: discord.Interaction, button):
        try:
            cursor.execute(f"DELETE FROM levels")
            db.commit()
            await interaction.response.send_message("Levels reset.")
        except Exception as e:
            print(e)


class levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("LOADED: `levels.py`")
        await self.bot.change_presence(status=discord.Status.online, activity=playing)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.author.bot:
                return
            if message.guild is None:
                return
            if message.content.startswith("!"):
                return
            cursor.execute(f"SELECT * FROM levels WHERE user_id = {message.author.id}")
            result = cursor.fetchone()
            if result is None:
                cursor.execute(f"INSERT INTO levels (user_id, xp, level) VALUES ({message.author.id}, 0, 0)")
                db.commit()
            else:
                cursor.execute(f"UPDATE levels SET xp = xp + 1 WHERE user_id = {message.author.id}")
                db.commit()
                cursor.execute(f"SELECT * FROM levels WHERE user_id = {message.author.id}")
                result = cursor.fetchone()
                xp = result[1]
                level = result[2]
                counting_channel = self.bot.get_channel(config.counting_channel)
                if message.channel.id == counting_channel:
                    xp += random.randint(2, 5)
                else:
                    xp += random.randint(1, 3)
                if xp >= limit[level]:
                    level += 1
                    cursor.execute(f"UPDATE levels SET xp = {xp}, level = {level} WHERE user_id = {message.author.id}")
                    db.commit()
                    cursor.execute(f"SELECT * FROM levels WHERE user_id = {message.author.id}")
                    result = cursor.fetchone()
                    level = result[2]
                    reaction = '🆙'
                    return await message.add_reaction(reaction)
                else:
                    cursor.execute(f"UPDATE levels SET xp = {xp} WHERE user_id = {message.author.id}")
                    db.commit()
                    return
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"```Error in `on_message` in levels.py\n{e}\n```")
    
    @app_commands.command(name="level", description="Shows your level")
    async def level(self, interaction: discord.Interaction, user: discord.User = None, hidden: bool=None):
        try:
            if user is None:
                user = interaction.user
            cursor.execute(f"SELECT * FROM levels WHERE user_id = {user.id}")
            result = cursor.fetchone()
            if result is None:
                embed = discord.Embed(title="Error", description="This user does not have any xp.", color=0xff0000)
                await interaction.response.send_message(embed=embed)
            else:
                level = result[2]
                xp = result[1]
                embed = discord.Embed(title="Level", description=f"Level: `{level}`\nXP: `{xp}`", color=0x00ff00)
                await interaction.response.send_message(embed=embed, ephemeral=hidden)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"```Error in `/level`\n{e}\n```")


    @app_commands.command(name="add-xp", description="Adds xp to a user")
    @app_commands.checks.has_any_role(config.administrators, config.true_admin, config.transparent_admin)
    async def add_xp(self, interaction: discord.Interaction, user: discord.User, xp: int):
        try:
            cursor.execute(f"SELECT * FROM levels WHERE user_id = {user.id}")
            result = cursor.fetchone()
            
            if xp >= limit[19]:
                embed = discord.Embed(title="Error", description="You cannot add more than `332,525` xp to a user.", color=0xff0000)
                await interaction.response.send_message(embed=embed)
            elif xp < 0:
                embed = discord.Embed(title="Error", description="You cannot add negative xp to a user.", color=0xff0000)
                await interaction.response.send_message(embed=embed)
            else:
                level = result[2]
                xp += result[1]
                while xp >= limit[level-1]:
                    level += 1
                if result is None:
                    cursor.execute(f"INSERT INTO levels (user_id, xp, level) VALUES ({user.id}, {xp}, {level})")
                    db.commit()
                    embed = discord.Embed(title="Added XP", description=f"Added {xp} xp to {user.mention}. New level: {level}", color=0x00ff00)
                    await interaction.response.send_message(embed=embed)
                else:
                    cursor.execute(f"UPDATE levels SET xp = xp + {xp}, level = {level} WHERE user_id = {user.id}")
                    db.commit()
                    embed = discord.Embed(title="Added XP", description=f"Added {xp} xp to {user.mention}. New level: {level}", color=0x00ff00)
                    await interaction.response.send_message(embed=embed)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"```Error in `/add-xp`\n{e}\n```")
    
    @app_commands.command(name="remove-xp", description="Removes xp from a user")
    @app_commands.checks.has_any_role(config.administrators, config.true_admin, config.transparent_admin)
    async def remove_xp(self, interaction: discord.Interaction, user: discord.User, xp: int):
        try:    
            cursor.execute(f"SELECT * FROM levels WHERE user_id = {user.id}")
            result = cursor.fetchone()
            if result is None:
                embed = discord.Embed(title="Error", description="This user does not have any xp.", color=0xff0000)
                await interaction.response.send_message(embed=embed)
            elif xp < 0:
                embed = discord.Embed(title="Error", description="You cannot remove negative xp from a user.", color=0xff0000)
                await interaction.response.send_message(embed=embed)
            elif (xp - result[1]) < 0:
                embed = discord.Embed(title="Error", description="You cannot remove more xp than a user has.", color=0xff0000)
                await interaction.response.send_message(embed=embed)
            else:
                for i in range(len(limit)):
                    if xp >= limit[i]:
                        level = i-1
                xp -= result[1]
                if xp < 0:
                    xp = 0
                cursor.execute(f"UPDATE levels SET xp = xp - {xp}, level = {level} WHERE user_id = {user.id}")
                db.commit()
                embed = discord.Embed(title="Removed XP", description=f"Removed {xp} xp from {user.mention}. Also new level: `{level}`", color=0x00ff00)
                await interaction.response.send_message(embed=embed)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"```Error in `/remove-xp`\n{e}\n```")

    @app_commands.command(name="set-xp", description="Sets a user's xp")
    @app_commands.checks.has_any_role(config.administrators, config.true_admin, config.transparent_admin)
    async def set_xp(self, interaction: discord.Interaction, user: discord.User, xp: int):
        try:
            cursor.execute(f"SELECT * FROM levels WHERE user_id = {user.id}")
            result = cursor.fetchone()
            level = result[2]
            if result is None:
                embed = discord.Embed(title="Error", description="This user does not have any xp.", color=0xff0000)
                await interaction.response.send_message(embed=embed)
            elif xp < 0:
                embed = discord.Embed(title="Error", description="You cannot set negative xp to a user.", color=0xff0000)
                await interaction.response.send_message(embed=embed)
            elif xp >= limit[19]:
                embed = discord.Embed(title="Error", description="You cannot set more than `332,525` xp to a user.", color=0xff0000)
                await interaction.response.send_message(embed=embed)
            else:
                for i in range(len(limit)):
                    if xp >= limit[i]:
                        print(limit[i])
                        level = limit[i]
                        break
                cursor.execute(f"UPDATE levels SET xp = {xp}, level = {level} WHERE user_id = {user.id}")
                db.commit()
                embed = discord.Embed(title="Set XP", description=f"Set {user.mention}'s XP to `{xp}`", color=0x00ff00)
                await interaction.response.send_message(embed=embed)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"```Error in `/set-xp`\n{e}\n```")
    
    
    @app_commands.command(name="reset-levels", description="Resets all levels")
    @app_commands.checks.has_any_role(config.administrators, config.true_admin, config.transparent_admin)
    async def reset_levels(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message("Are you sure you would like to reset all of the levels in the server? This action is irreversible.", view=Confirm(), ephemeral=True)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"```Error in `/reset-levels`\n{e}\n```")
    
    @app_commands.command(name="list-levels", description="List all the levels")
    @app_commands.checks.has_any_role(config.administrators, config.true_admin, config.transparent_admin)
    async def list_levels(self, interaction: discord.Interaction):
        try:
            embed = discord.Embed(title="Levels", description="List of all the levels\n\n", color=0x00ff00)
            level = ""
            for i in range(len(limit)):
                level += f"Level {i+1}: XP: {limit[i]:,}\n"
            embed.description += level
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"```Error in `/list-levels`\n{e}\n```")


async def setup(bot):
    await bot.add_cog(levels(bot), guilds=[discord.Object(id=config.server_id)])