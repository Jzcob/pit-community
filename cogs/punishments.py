import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime as dt
from datetime import timedelta as td
import mysql.connector
from mysql.connector import pooling
import config
import traceback
import os
import re
from dotenv import load_dotenv

load_dotenv()

def is_staff(member: discord.Member):
    return any(role.id == config.staff for role in member.roles)

def clean_id(input_str: str):
    """Extracts only digits from a string (fixes mentions/strings being passed as IDs)."""
    return re.sub(r'\D', '', input_str)

class Punishments(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            self.db_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="punishments_pool",
                pool_size=5,
                host=os.getenv("punishments_host"),
                user=os.getenv("punishments_user"),
                password=os.getenv("punishments_password"),
                database=os.getenv("punishments_database")
            )
        except Exception as e:
            print(f"CRITICAL: Could not initialize DB pool: {e}")

    def get_db_connection(self):
        return self.db_pool.get_connection()

    @commands.Cog.listener()
    async def on_ready(self):
        print("LOADED: `punishments.py` with Connection Pooling")

    async def log_error(self, command_name, error_text):
        error_channel = self.bot.get_channel(config.error_channel)
        if error_channel:
            # Check if the error text is too long for a single message
            if len(error_text) > 1900:
                error_text = error_text[:1900] + "... [Truncated]"
            await error_channel.send(f"Error in `{command_name}`:\n```python\n{error_text}```")

    # --- Commands ---

    @app_commands.command(name="warn", description="Warn a user.")
    @app_commands.checks.has_any_role(config.staff)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str, evidence: discord.Attachment = None):
        await interaction.response.defer(ephemeral=True)
        
        if user.id == interaction.user.id or user.id == self.bot.user.id or is_staff(user):
            return await interaction.followup.send("You cannot warn this user.", ephemeral=True)

        try:
            timestamp = int(dt.timestamp(dt.now()))
            db = self.get_db_connection()
            cursor = db.cursor()
            
            cursor.execute(
                "INSERT INTO warnings (user_id, reason, staff_id, timestamp) VALUES (%s, %s, %s, %s)",
                (user.id, reason, interaction.user.id, timestamp)
            )
            db.commit()
            cursor.close()
            db.close()

            embed = discord.Embed(title=f"Warned {user.name}", description=f"**Reason:** {reason}\n**Staff:** {interaction.user.mention}", color=discord.Color.red())
            if evidence:
                embed.set_image(url=evidence.url)

            await interaction.followup.send(embed=embed)

            try:
                user_embed = discord.Embed(title=f"You were warned in {interaction.guild.name}", description=f"Reason: {reason}", color=discord.Color.red())
                await user.send(embed=user_embed)
            except: pass

            punishment_channel = self.bot.get_channel(config.punishments)
            if punishment_channel:
                file = await evidence.to_file() if evidence else None
                await punishment_channel.send(f"Warned {user.mention}", file=file, embed=embed if not file else None)
            
            mod_log = self.bot.get_channel(config.mod_log_channel)
            if mod_log:
                await mod_log.send(embed=embed)

        except Exception:
            await self.log_error("/warn", traceback.format_exc())
            await interaction.followup.send("Database or execution error occurred.", ephemeral=True)

    @app_commands.command(name="trade-warn", description="Warn a user regarding trade rules.")
    @app_commands.checks.has_any_role(config.staff)
    async def trade_warn(self, interaction: discord.Interaction, user: discord.Member, msgid: str):
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Clean ID to prevent ValueError: invalid literal for int()
            cleaned_msgid = clean_id(msgid)
            if not cleaned_msgid:
                return await interaction.followup.send("Invalid Message ID provided.", ephemeral=True)

            try:
                message = await interaction.channel.fetch_message(int(cleaned_msgid))
            except discord.NotFound:
                return await interaction.followup.send("Could not find that message in this channel.", ephemeral=True)

            if message.author.id != user.id:
                return await interaction.followup.send("Message author mismatch (The ID provided isn't from the user specified).", ephemeral=True)

            db = self.get_db_connection()
            cursor = db.cursor()
            timestamp = int(dt.timestamp(dt.now()))
            cursor.execute(
                "INSERT INTO warnings (user_id, reason, staff_id, timestamp) VALUES (%s, %s, %s, %s)",
                (user.id, "TRADE WARN", interaction.user.id, timestamp)
            )
            db.commit()
            cursor.close()
            db.close()

            cant_trade = interaction.guild.get_role(797912815280324681)
            if cant_trade: 
                try:
                    await user.add_roles(cant_trade)
                except: pass
            
            msg_content = message.content[:1024]
            try:
                await message.delete()
            except discord.Forbidden:
                pass # Bot lacks permission to delete

            embed = discord.Embed(title=f"Trade Warned {user.name}", description=f"Staff: {interaction.user.mention}", color=discord.Color.red())
            embed.add_field(name="Infringing Message", value=msg_content if msg_content else "No Text Content")
            
            await interaction.followup.send(embed=embed)
            
            mod_log = self.bot.get_channel(config.mod_log_channel)
            if mod_log:
                await mod_log.send(embed=embed)

        except Exception:
            await self.log_error("/trade-warn", traceback.format_exc())
            await interaction.followup.send("Error processing trade warn.", ephemeral=True)

    @app_commands.command(name="timeout", description="Timeout a user.")
    @app_commands.describe(duration="The duration of the timeout.")
    @app_commands.choices(duration=[
        app_commands.Choice(name='15 minutes', value='15m'),
        app_commands.Choice(name='1 hour', value='1h'),
        app_commands.Choice(name='6 hours', value='6h'),
        app_commands.Choice(name='1 day', value='1d'),
        app_commands.Choice(name='1 week', value='1w'),
        app_commands.Choice(name='1 month', value='1m'),
    ])
    @app_commands.checks.has_any_role(config.staff)
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, duration: app_commands.Choice[str], reason: str, evidence: discord.Attachment = None):
        await interaction.response.defer(ephemeral=True)

        durations = {"15m": td(minutes=15), "1h": td(hours=1), "6h": td(hours=6), "1d": td(days=1), "1w": td(weeks=1), "1m": td(weeks=4)}
        punishment_duration = durations.get(duration.value)

        try:
            await user.timeout(punishment_duration, reason=reason)
            
            db = self.get_db_connection()
            cursor = db.cursor()
            timestamp = int(dt.timestamp(dt.now()))
            cursor.execute(
                "INSERT INTO timeouts (user_id, reason, staff_id, time, timestamp) VALUES (%s, %s, %s, %s, %s)",
                (user.id, reason, interaction.user.id, duration.name, timestamp)
            )
            db.commit()
            cursor.close()
            db.close()

            embed = discord.Embed(title=f"Timed out {user.name}", description=f"Duration: {duration.name}\nReason: {reason}", color=discord.Color.red())
            await interaction.followup.send(embed=embed)
            
            mod_log = self.bot.get_channel(config.mod_log_channel)
            if mod_log:
                await mod_log.send(embed=embed)
        except Exception:
            await self.log_error("/timeout", traceback.format_exc())
            await interaction.followup.send("Failed to timeout user.", ephemeral=True)

    @app_commands.command(name="kick", description="Kick a user.")
    @app_commands.checks.has_any_role(config.staff)
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str, evidence: discord.Attachment = None):
        await interaction.response.defer(ephemeral=True)

        if is_staff(user):
            return await interaction.followup.send("Cannot kick staff.", ephemeral=True)

        try:
            try:
                await user.send(f"You were kicked from {interaction.guild.name}. Reason: {reason}")
            except: pass

            await user.kick(reason=reason)

            db = self.get_db_connection()
            cursor = db.cursor()
            cursor.execute("INSERT INTO kicks (user_id, reason, staff_id) VALUES (%s, %s, %s)", (user.id, reason, interaction.user.id))
            db.commit()
            cursor.close()
            db.close()

            await interaction.followup.send(f"Successfully kicked {user.name}.")
        except Exception:
            await self.log_error("/kick", traceback.format_exc())
            await interaction.followup.send("Failed to kick user.", ephemeral=True)

    @app_commands.command(name="ban", description="Ban a user.")
    @app_commands.checks.has_any_role(config.staff)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str, evidence: discord.Attachment = None):
        await interaction.response.defer(ephemeral=True)

        try:
            try:
                await user.send(f"You were banned from {interaction.guild.name}. Reason: {reason}")
            except: pass

            await user.ban(reason=reason)

            db = self.get_db_connection()
            cursor = db.cursor()
            timestamp = int(dt.timestamp(dt.now()))
            cursor.execute(
                "INSERT INTO bans (user_id, reason, staff_id, timestamp) VALUES (%s, %s, %s, %s)",
                (user.id, reason, interaction.user.id, timestamp)
            )
            db.commit()
            cursor.close()
            db.close()

            await interaction.followup.send(f"Banned {user.name}.")
        except Exception:
            await self.log_error("/ban", traceback.format_exc())
            await interaction.followup.send("Failed to ban user.", ephemeral=True)

    @app_commands.command(name="logs", description="View a user's punishments.")
    @app_commands.checks.has_any_role(config.staff)
    async def logs(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer()
        
        try:
            db = self.get_db_connection()
            cursor = db.cursor()
            cursor.execute("SELECT reason, staff_id, timestamp FROM warnings WHERE user_id = %s", (user.id,))
            warns = cursor.fetchall()
            cursor.close()
            db.close()
            
            embed = discord.Embed(title=f"Punishments for {user.name}", color=discord.Color.orange())
            
            if warns:
                val = "\n".join([f"{i+1}. <@{w[1]}>: `{w[0]}` (<t:{w[2]}:D>)" for i, w in enumerate(warns)])
                embed.add_field(name="Warnings", value=val, inline=False)
            else:
                embed.description = "No punishments found."

            await interaction.followup.send(embed=embed)
        except Exception:
            await self.log_error("/logs", traceback.format_exc())
            await interaction.followup.send("Error retrieving logs.", ephemeral=True)

    @app_commands.command(name="purge", description="Purge messages.")
    @app_commands.checks.has_any_role(config.staff)
    async def purge(self, interaction: discord.Interaction, amount: int, member: discord.Member = None):
        await interaction.response.send_message(f"Purging {amount} messages...", ephemeral=True)
        
        def check(m):
            return m.author == member if member else True

        try:
            await interaction.channel.purge(limit=amount, check=check)
        except Exception:
            await self.log_error("/purge", traceback.format_exc())

async def setup(bot):
    await bot.add_cog(Punishments(bot), guilds=[discord.Object(id=config.server_id)])