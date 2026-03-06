import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime as dt
from datetime import timedelta as td
import mysql.connector
import config
import traceback
import os
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()

def is_staff(member: discord.Member):
    return discord.utils.get(member.roles, id=config.staff)

class punishments(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @contextmanager
    def get_db_connection(self):
        """Context manager to ensure DB connections always close."""
        db = mysql.connector.connect(
            host=os.getenv("punishments_host"),
            user=os.getenv("punishments_user"),
            password=os.getenv("punishments_password"),
            database=os.getenv("punishments_database")
        )
        cursor = db.cursor()
        try:
            yield db, cursor
        finally:
            cursor.close()
            db.close()

    @commands.Cog.listener()
    async def on_ready(self):
        print("LOADED: `punishments.py`")

    async def log_error(self, command_name, error_text):
        error_channel = self.bot.get_channel(config.error_channel)
        if error_channel:
            await error_channel.send(f"Error in `{command_name}`:\n```python\n{error_text}```")

    # --- Commands ---

    @app_commands.command(name="warn", description="Warn a user.")
    @app_commands.checks.has_any_role(config.staff)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str, evidence: discord.Attachment = None):
        await interaction.response.defer(ephemeral=True)
        
        if user.id == interaction.user.id or user.id == self.bot.user.id or is_staff(user):
            return await interaction.followup.send("You cannot warn this user.", ephemeral=True)

        with self.get_db_connection() as (db, cursor):
            try:
                timestamp = int(dt.timestamp(dt.now()))
                cursor.execute(
                    "INSERT INTO warnings (user_id, reason, staff_id, timestamp) VALUES (%s, %s, %s, %s)",
                    (user.id, reason, interaction.user.id, timestamp)
                )
                db.commit()

                embed = discord.Embed(title=f"Warned {user.name}", description=f"**Reason:** {reason}\n**Staff:** {interaction.user.mention}", color=discord.Color.red())
                if evidence:
                    embed.set_image(url=evidence.url)

                try:
                    userEmbed = discord.Embed(title=f"You were warned in {interaction.guild.name}", description=f"Reason: {reason}", color=discord.Color.red())
                    await user.send(embed=userEmbed)
                except:
                    pass

                await interaction.followup.send(embed=embed)
                await self.bot.get_channel(config.punishments).send(f"Warned {user.mention}", file=await evidence.to_file() if evidence else None)
                await self.bot.get_channel(config.mod_log_channel).send(embed=embed)
            except Exception:
                await self.log_error("/warn", traceback.format_exc())

    @app_commands.command(name="trade-warn", description="Warn a user regarding trade rules.")
    @app_commands.checks.has_any_role(config.staff)
    async def tradeWarn(self, interaction: discord.Interaction, user: discord.Member, msgid: str):
        await interaction.response.defer(ephemeral=True)
        
        try:
            message = await interaction.channel.fetch_message(int(msgid))
            if message.author.id != user.id:
                return await interaction.followup.send("Message author mismatch.", ephemeral=True)

            with self.get_db_connection() as (db, cursor):
                timestamp = int(dt.timestamp(dt.now()))
                cursor.execute(
                    "INSERT INTO warnings (user_id, reason, staff_id, timestamp) VALUES (%s, %s, %s, %s)",
                    (user.id, "TRADE WARN", interaction.user.id, timestamp)
                )
                db.commit()

                cantTrade = interaction.guild.get_role(797912815280324681)
                if cantTrade: await user.add_roles(cantTrade)
                await message.delete()

                embed = discord.Embed(title=f"Trade Warned {user.name}", description=f"Staff: {interaction.user.mention}", color=discord.Color.red())
                embed.add_field(name="Infringing Message", value=message.content[:1024])
                
                await interaction.followup.send(embed=embed)
                await self.bot.get_channel(config.mod_log_channel).send(embed=embed)
        except Exception:
            await self.log_error("/trade-warn", traceback.format_exc())

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
            
            with self.get_db_connection() as (db, cursor):
                timestamp = int(dt.timestamp(dt.now()))
                cursor.execute(
                    "INSERT INTO timeouts (user_id, reason, staff_id, time, timestamp) VALUES (%s, %s, %s, %s, %s)",
                    (user.id, reason, interaction.user.id, duration.name, timestamp)
                )
                db.commit()

            embed = discord.Embed(title=f"Timed out {user.name}", description=f"Duration: {duration.name}\nReason: {reason}", color=discord.Color.red())
            await interaction.followup.send(embed=embed)
            await self.bot.get_channel(config.mod_log_channel).send(embed=embed)
        except Exception:
            await self.log_error("/timeout", traceback.format_exc())

    @app_commands.command(name="kick", description="Kick a user.")
    @app_commands.checks.has_any_role(config.jr_moderator, config.moderator, config.administrators)
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str, evidence: discord.Attachment = None):
        await interaction.response.defer(ephemeral=True)

        if is_staff(user):
            return await interaction.followup.send("Cannot kick staff.", ephemeral=True)

        try:
            try:
                await user.send(f"You were kicked from {interaction.guild.name}. Reason: {reason}")
            except: pass

            await user.kick(reason=reason)

            with self.get_db_connection() as (db, cursor):
                cursor.execute("INSERT INTO kicks (user_id, reason, staff_id) VALUES (%s, %s, %s)", (user.id, reason, interaction.user.id))
                db.commit()

            await interaction.followup.send(f"Successfully kicked {user.name}.")
        except Exception:
            await self.log_error("/kick", traceback.format_exc())

    @app_commands.command(name="ban", description="Ban a user.")
    @app_commands.checks.has_any_role(config.moderator, config.administrators)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str, evidence: discord.Attachment = None):
        await interaction.response.defer(ephemeral=True)

        try:
            try:
                await user.send(f"You were banned from {interaction.guild.name}. Reason: {reason}")
            except: pass

            await user.ban(reason=reason)

            with self.get_db_connection() as (db, cursor):
                timestamp = int(dt.timestamp(dt.now()))
                cursor.execute(
                    "INSERT INTO bans (user_id, reason, staff_id, timestamp) VALUES (%s, %s, %s, %s)",
                    (user.id, reason, interaction.user.id, timestamp)
                )
                db.commit()

            await interaction.followup.send(f"Banned {user.name}.")
        except Exception:
            await self.log_error("/ban", traceback.format_exc())

    @app_commands.command(name="logs", description="View a user's punishments.")
    @app_commands.checks.has_any_role(config.staff)
    async def logs(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer()
        
        with self.get_db_connection() as (db, cursor):
            cursor.execute("SELECT reason, staff_id, timestamp FROM warnings WHERE user_id = %s", (user.id,))
            warns = cursor.fetchall()
            
            embed = discord.Embed(title=f"Punishments for {user.name}", color=discord.Color.orange())
            
            if warns:
                val = "\n".join([f"{i+1}. <@{w[1]}>: `{w[0]}` (<t:{w[2]}:D>)" for i, w in enumerate(warns)])
                embed.add_field(name="Warnings", value=val, inline=False)
            else:
                embed.description = "No punishments found."

            await interaction.followup.send(embed=embed)

    @app_commands.command(name="purge", description="Purge messages.")
    @app_commands.checks.has_any_role(config.moderator, config.administrators)
    async def purge(self, interaction: discord.Interaction, amount: int, member: discord.Member = None):
        await interaction.response.send_message(f"Purging {amount} messages...", ephemeral=True)
        
        def check(m):
            return m.author == member if member else True

        await interaction.channel.purge(limit=amount, check=check)

async def setup(bot):
    await bot.add_cog(punishments(bot), guilds=[discord.Object(id=config.server_id)])