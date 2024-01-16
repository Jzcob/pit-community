import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime as dt
from datetime import timedelta as td
import mysql.connector
import config


import os
from dotenv import load_dotenv
load_dotenv()

db = mysql.connector.connect(
    host=os.getenv("punishments_host"),
    user=os.getenv("punishments_user"),
    password=os.getenv("punishments_password"),
    database=os.getenv("punishments_database")
)
#command permissions
#warn - staff
#logs - staff
#info - staff
#timeout - staff
#reason - staff
#kick jr_moderator
#ban moderator
#cancel-timeout (untimeout) moderator
#purge moderator
#unban - jr_moderator
#logs-clear admin


def is_staff(member: discord.Member):
    return discord.utils.get(member.roles, id=config.staff)

cursor = db.cursor()

class punishments(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("LOADED: `punishments.py`")
    
    @app_commands.command(name="warn", description="Warn a user.")
    @app_commands.checks.has_any_role(config.staff)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, *, reason: str):
        today = dt.now()
        timestamp = dt.timestamp(today)
        try:
            if user.id == interaction.user.id:
                await interaction.response.send_message("You can't warn yourself!", ephemeral=True)
                return
            if user.id == self.bot.user.id:
                await interaction.response.send_message("You can't warn me!", ephemeral=True)
                return
            if user.id == interaction.guild.owner.id:
                await interaction.response.send_message("You can't warn the owner!", ephemeral=True)
                return
            if is_staff(user):
                await interaction.response.send_message("You can't warn staff!", ephemeral=True)
                return
            mod_logs = self.bot.get_channel(config.mod_log_channel)
            cursor.execute(f"INSERT INTO warnings (user_id, reason, staff_id, timestamp) VALUES ({user.id}, '{reason}', {interaction.user.id}, {int(timestamp)})")
            db.commit()
            embed = discord.Embed(title=f"Warned {user.name}", description=f"Reason: {reason}\nStaff: {interaction.user.mention}", color=discord.Color.red())
            userEmbed = discord.Embed(title=f"You were warned in {interaction.guild.name} ", description=f"Reason: {reason}", color=discord.Color.red())
            try:
                await user.send(embed=userEmbed)
            except:
                await mod_logs.send(f"Failed to send DM to {user.mention} ({user.id})")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await mod_logs.send(embed=embed)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in `/warn`: {e}")
    
    @app_commands.command(name="trade-warn", description="Warn a user that isnt following the trade rules.")
    @app_commands.checks.has_any_role(config.staff)
    async def tradeWarn(self, interaction: discord.Interaction, user: discord.Member, msgid: str):
        reason = "TRADE WARN"
        today = dt.now()
        timestamp = dt.timestamp(today)
        id = int(msgid)
        message = await interaction.channel.fetch_message(id)
        try:
            if message.author.id != user.id:
                await interaction.response.send_message("That message isn't from that user!", ephemeral=True)
                return
            if user.id == interaction.user.id:
                await interaction.response.send_message("You can't warn yourself!", ephemeral=True)
                return
            if user.id == self.bot.user.id:
                await interaction.response.send_message("You can't warn me!", ephemeral=True)
                return
            if user.id == interaction.guild.owner.id:
                await interaction.response.send_message("You can't warn the owner!", ephemeral=True)
                return
            if is_staff(user):
                await interaction.response.send_message("You can't warn staff!", ephemeral=True)
                return
            mod_logs = self.bot.get_channel(config.mod_log_channel)
            cursor.execute(f"INSERT INTO warnings (user_id, reason, staff_id, timestamp) VALUES ({user.id}, '{reason}', {interaction.user.id}, {int(timestamp)})")
            db.commit()
            embed = discord.Embed(title=f"Trade Warned {user.name}", description=f"Reason: {reason}\nStaff: {interaction.user.mention}", color=discord.Color.red())
            cantTrade = discord.utils.get(user.guild.roles, id=797912815280324681)
            await user.add_roles(cantTrade)
            await message.delete()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await mod_logs.send(content=f"`{message.content}`",embed=embed)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in `/trade-warn`: {e}")
    
    @app_commands.command(name="timeout", description="Timeout a user.")
    @app_commands.describe(duration="The duration of the timeout.")
    @app_commands.choices(duration=[
        discord.app_commands.Choice(name='15 minutes', value='15m'),
        discord.app_commands.Choice(name='1 hour', value='1h'),
        discord.app_commands.Choice(name='6 hours', value='6h'),
        discord.app_commands.Choice(name='1 day', value='1d'),
        discord.app_commands.Choice(name='3 days', value='3d'),
        discord.app_commands.Choice(name='1 week', value='1w'),
        discord.app_commands.Choice(name='2 weeks', value='2w'),
        discord.app_commands.Choice(name='3 weeks', value='3w'),
        discord.app_commands.Choice(name='1 month', value='1m'),
        ])
    @app_commands.checks.has_any_role(config.staff)
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, duration: discord.app_commands.Choice[str], *, reason: str):
        mod_logs = self.bot.get_channel(config.mod_log_channel)
        today = dt.today()
        timestamp = dt.timestamp(today)
        try:
            if user.id == interaction.user.id:
                await interaction.response.send_message("You can't timeout yourself!", ephemeral=True)
                return
            if user.id == self.bot.user.id:
                await interaction.response.send_message("You can't timeout me!", ephemeral=True)
                return
            if user.id == interaction.guild.owner.id:
                await interaction.response.send_message("You can't timeout the owner!", ephemeral=True)
                return
            if is_staff(user):
                await interaction.response.send_message("You can't timeout staff!", ephemeral=True)
                return
            mod_logs = self.bot.get_channel(config.mod_log_channel)
            
            embed = discord.Embed(title=f"Timed out {user.name}", description=f"Reason: {reason}\nStaff: {interaction.user.mention}\nDuration: {duration.name}", color=discord.Color.red())
            userEmbed = discord.Embed(title=f"You were timed out in {interaction.guild.name} ", description=f"Reason: {reason}\nDuration: {duration.name}", color=discord.Color.red())
            if duration.value == "15m":
                punishment_duration = td(minutes=15)
            elif duration.value == "1h":
                punishment_duration = td(hours=1)
            elif duration.value == "6h":
                punishment_duration = td(hours=6)
            elif duration.value == "1d":
                punishment_duration = td(days=1)
            elif duration.value == "3d":
                punishment_duration = td(days=3)
            elif duration.value == "1w":
                punishment_duration = td(weeks=1)
            elif duration.value == "2w":
                punishment_duration = td(weeks=2)
            elif duration.value == "3w":
                punishment_duration = td(weeks=3)
            elif duration.value == "1m":
                punishment_duration = td(weeks=4)
            else:
                return await interaction.response.send_message("Invalid duration!", ephemeral=True)
            
            await user.timeout(punishment_duration, reason=reason)
            cursor.execute(f"INSERT INTO timeouts (user_id, reason, staff_id, time, timestamp) VALUES ({user.id}, '{reason}', {interaction.user.id}, '{duration.name}', {int(timestamp)})")
            db.commit()
            try:
                await user.send(embed=userEmbed)
            except:
                await mod_logs.send(f"Failed to send DM to {user.mention} ({user.id})")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await mod_logs.send(embed=embed)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in `/timeout`: {e}")
    
    @app_commands.command(name="kick", description="Kick a user.")
    @app_commands.checks.has_any_role(config.jr_moderator, config.moderator, config.administrators, config.transparent_admin, config.true_admin)
    async def kick(self, interaction: discord.Interaction, user: discord.Member, *, reason: str):
        try:
            if user.id == interaction.user.id:
                await interaction.response.send_message("You can't kick yourself!", ephemeral=True)
                return
            if user.id == self.bot.user.id:
                await interaction.response.send_message("You can't kick me!", ephemeral=True)
                return
            if user.id == interaction.guild.owner.id:
                await interaction.response.send_message("You can't kick the owner!", ephemeral=True)
                return
            if is_staff(user):
                await interaction.response.send_message("You can't kick staff!", ephemeral=True)
                return
            mod_logs = self.bot.get_channel(config.mod_log_channel)
            embed = discord.Embed(title=f"Kicked {user.name}", description=f"Reason: {reason}\nStaff: {interaction.user.mention}", color=discord.Color.red())
            userEmbed = discord.Embed(title=f"You were kicked from {interaction.guild.name} ", description=f"Reason: {reason}", color=discord.Color.red())
            try:
                await user.send(embed=userEmbed)
            except:
                await mod_logs.send(f"Failed to send DM to {user.mention} ({user.id})")
            await user.kick(reason=reason)
            cursor.execute(f"INSERT INTO kicks (user_id, reason, staff_id) VALUES ({user.id}, '{reason}', {interaction.user.id})")
            db.commit()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await mod_logs.send(embed=embed)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in `/kick`: {e}")
    
    @app_commands.command(name="ban", description="Ban a user.")
    @app_commands.checks.has_any_role(config.moderator, config.administrators, config.transparent_admin, config.true_admin)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, *, reason: str):
        today = dt.today()
        timestamp = dt.timestamp(today)
        try:
            if user.id == interaction.user.id:
                await interaction.response.send_message("You can't ban yourself!", ephemeral=True)
                return
            if user.id == self.bot.user.id:
                await interaction.response.send_message("You can't ban me!", ephemeral=True)
                return
            if user.id == interaction.guild.owner.id:
                await interaction.response.send_message("You can't ban the owner!", ephemeral=True)
                return
            if is_staff(user):
                await interaction.response.send_message("You can't ban staff!", ephemeral=True)
                return
            mod_logs = self.bot.get_channel(config.mod_log_channel)
            embed = discord.Embed(title=f"Banned {user.name}", description=f"Reason: {reason}\nStaff: {interaction.user.mention}", color=discord.Color.red())
            userEmbed = discord.Embed(title=f"You were banned from {interaction.guild.name} ", description=f"Reason: {reason}", color=discord.Color.red())
            try:
                await user.send(embed=userEmbed)
            except:
                await mod_logs.send(f"Failed to send DM to {user.mention} ({user.id})")
            await user.ban(reason=reason)
            cursor.execute(f"INSERT INTO bans (user_id, reason, staff_id, timestamp) VALUES ({user.id}, '{reason}', {interaction.user.id}, {int(timestamp)})")
            db.commit()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await mod_logs.send(embed=embed)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in `/ban`: {e}")
    
    @app_commands.command(name="remove-timeout", description="Remove a user's timeout from the DB.")
    @app_commands.checks.has_any_role(config.administrators, config.transparent_admin, config.true_admin)
    async def removeTimeout(self, interaction: discord.Interaction, user: discord.Member, timeout: int):
        try:
            mod_logs = self.bot.get_channel(config.mod_log_channel)
            cursor.execute(f"SELECT * FROM timeouts WHERE user_id = {user.id}")
            timeouts = cursor.fetchall()
            if len(timeouts) < timeout:
                await interaction.response.send_message("Invalid timeout number!", ephemeral=True)
                return
            cursor.execute(f"DELETE FROM timeouts WHERE user_id = {user.id} AND reason = '{timeouts[timeout-1][1]}' AND staff_id = {timeouts[timeout-1][2]} AND time = '{timeouts[timeout-1][3]}' AND timestamp = {timeouts[timeout-1][4]}")
            db.commit()
            await interaction.response.send_message(f"Removed timeout for {user.mention}", ephemeral=True)
            embed = discord.Embed(title=f"Removed timeout for {user.name}", description=f"Staff: {interaction.user.mention}", color=discord.Color.green())
            await mod_logs.send(embed=embed)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in `/remove-timeout`: {e}")
    
    @app_commands.command(name="cancel-timeout", description="Cancel a user's timeout.")
    @app_commands.checks.has_any_role(config.moderator, config.administrators, config.transparent_admin, config.true_admin)
    async def cancelTimeout(self, interaction: discord.Interaction, user: discord.Member):
        try:
            if user.is_timed_out():
                await user.timeout(td(seconds=1), reason="Timeout cancelled")
                await interaction.response.send_message(f"Cancelled timeout for {user.mention}", ephemeral=True)
                embed = discord.Embed(title=f"Cancelled timeout for {user.name}", description=f"Staff: {interaction.user.mention}", color=discord.Color.green())
                mod_logs = self.bot.get_channel(config.mod_log_channel)
                await mod_logs.send(embed=embed)
            else:
                await interaction.response.send_message(f"{user.name} isn't timed out!", ephemeral=True)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in `/cancel-timeout`: {e}")
    
    @app_commands.command(name="remove-warning", description="Remove a user's warning from the DB.")
    @app_commands.checks.has_any_role(config.administrators, config.transparent_admin, config.true_admin)
    async def removeWarning(self, interaction: discord.Interaction, user: discord.Member, warning: int):
        try:
            mod_logs = self.bot.get_channel(config.mod_log_channel)
            cursor.execute(f"SELECT * FROM warnings WHERE user_id = {user.id}")
            warnings = cursor.fetchall()
            if len(warnings) < warning:
                await interaction.response.send_message("Invalid warning number!", ephemeral=True)
                return
            cursor.execute(f"DELETE FROM warnings WHERE user_id = {user.id} AND reason = '{warnings[warning-1][1]}' AND staff_id = {warnings[warning-1][2]} AND timestamp = {warnings[warning-1][3]}")
            db.commit()
            await interaction.response.send_message(f"Removed warning for {user.mention}", ephemeral=True)
            embed = discord.Embed(title=f"Removed warning for {user.name}", description=f"Staff: {interaction.user.mention}", color=discord.Color.green())
            await mod_logs.send(embed=embed)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in `/remove-warning`: {e}")
    "I added `clear-logs`, `cancel-timeout`, `remove-warning`, `remove-kick`, and `remove`ban`"
    @app_commands.command(name="remove-kick", description="Remove a user's kick from the DB.")
    @app_commands.checks.has_any_role(config.administrators, config.transparent_admin, config.true_admin)
    async def removeKick(self, interaction: discord.Interaction, user: discord.Member, kick: int):
        try:
            mod_logs = self.bot.get_channel(config.mod_log_channel)
            cursor.execute(f"SELECT * FROM kicks WHERE user_id = {user.id}")
            kicks = cursor.fetchall()
            if len(kicks) < kick:
                await interaction.response.send_message("Invalid kick number!", ephemeral=True)
                return
            cursor.execute(f"DELETE FROM kicks WHERE user_id = {user.id} AND reason = '{kicks[kick-1][1]}' AND staff_id = {kicks[kick-1][2]} AND timestamp = {kicks[kick-1][3]}")
            db.commit()
            await interaction.response.send_message(f"Removed kick for {user.mention}", ephemeral=True)
            embed = discord.Embed(title=f"Removed kick for {user.name}", description=f"Staff: {interaction.user.mention}", color=discord.Color.green())
            await mod_logs.send(embed=embed)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in `/remove-kick`: {e}")
    
    @app_commands.command(name="remove-ban", description="Remove a user's ban from the DB.")
    @app_commands.checks.has_any_role(config.administrators, config.transparent_admin, config.true_admin)
    async def removeBan(self, interaction: discord.Interaction, user: discord.Member, ban: int):
        try:
            mod_logs = self.bot.get_channel(config.mod_log_channel)
            cursor.execute(f"SELECT * FROM bans WHERE user_id = {user.id}")
            bans = cursor.fetchall()
            if len(bans) < ban:
                await interaction.response.send_message("Invalid ban number!", ephemeral=True)
                return
            cursor.execute(f"DELETE FROM bans WHERE user_id = {user.id} AND reason = '{bans[ban-1][1]}' AND staff_id = {bans[ban-1][2]} AND timestamp = {bans[ban-1][3]}")
            db.commit()
            await interaction.response.send_message(f"Removed ban for {user.mention}", ephemeral=True)
            embed = discord.Embed(title=f"Removed ban for {user.name}", description=f"Staff: {interaction.user.mention}", color=discord.Color.green())
            await mod_logs.send(embed=embed)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in `/remove-ban`: {e}")
    
    @app_commands.command(name="clear-logs", description="Clear a user's punishments.")
    @app_commands.checks.has_any_role(config.administrators, config.transparent_admin, config.true_admin)
    async def clearLogs(self, interaction: discord.Interaction, user: discord.Member):
        try:
            mod_logs = self.bot.get_channel(config.mod_log_channel)
            cursor.execute(f"SELECT * FROM warnings WHERE user_id = {user.id}")
            warnings = cursor.fetchall()
            cursor.execute(f"SELECT * FROM timeouts WHERE user_id = {user.id}")
            timeouts = cursor.fetchall()
            cursor.execute(f"SELECT * FROM kicks WHERE user_id = {user.id}")
            kicks = cursor.fetchall()
            cursor.execute(f"SELECT * FROM bans WHERE user_id = {user.id}")
            bans = cursor.fetchall()
            if len(warnings) == 0 and len(timeouts) == 0 and len(kicks) == 0 and len(bans) == 0:
                await interaction.response.send_message(f"{user.name} has no punishments!", ephemeral=True)
                return
            cursor.execute(f"DELETE FROM warnings WHERE user_id = {user.id}")
            cursor.execute(f"DELETE FROM timeouts WHERE user_id = {user.id}")
            cursor.execute(f"DELETE FROM kicks WHERE user_id = {user.id}")
            cursor.execute(f"DELETE FROM bans WHERE user_id = {user.id}")
            db.commit()
            await interaction.response.send_message(f"Cleared logs for {user.mention}", ephemeral=True)
            embed = discord.Embed(title=f"Cleared logs for {user.name}", description=f"Staff: {interaction.user.mention}", color=discord.Color.green())
            await mod_logs.send(embed=embed)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in `/clear-logs`: {e}")


    @app_commands.command(name="logs", description="View a user's punishments.")
    @app_commands.checks.has_any_role(config.staff)
    async def logs(self, interaction: discord.Interaction, user: discord.Member):
        try:
            cursor.execute(f"SELECT staff_id FROM warnings WHERE user_id = {user.id}")
            warningStaff = cursor.fetchall()
            cursor.execute(f"SELECT reason FROM warnings WHERE user_id = {user.id}")
            warningReason = cursor.fetchall()
            cursor.execute(f"SELECT timestamp FROM warnings WHERE user_id = {user.id}")
            warningTime = cursor.fetchall()
            cursor.execute(f"SELECT staff_id FROM timeouts WHERE user_id = {user.id}")
            timeoutStaff = cursor.fetchall()
            cursor.execute(f"SELECT reason FROM timeouts WHERE user_id = {user.id}")
            timeoutReason = cursor.fetchall()
            cursor.execute(f"SELECT time FROM timeouts WHERE user_id = {user.id}")
            timeoutDuration = cursor.fetchall()
            cursor.execute(f"SELECT timestamp FROM timeouts WHERE user_id = {user.id}")
            timeoutTime = cursor.fetchall()
            cursor.execute(f"SELECT staff_id FROM kicks WHERE user_id = {user.id}")
            kickStaff = cursor.fetchall()
            cursor.execute(f"SELECT reason FROM kicks WHERE user_id = {user.id}")
            kickReason = cursor.fetchall()
            cursor.execute(f"SELECT timestamp FROM kicks WHERE user_id = {user.id}")
            kickTime = cursor.fetchall()
            cursor.execute(f"SELECT staff_id FROM bans WHERE user_id = {user.id}")
            banStaff = cursor.fetchall()
            cursor.execute(f"SELECT reason FROM bans WHERE user_id = {user.id}")
            banReason = cursor.fetchall()
            cursor.execute(f"SELECT timestamp FROM bans WHERE user_id = {user.id}")
            banTime = cursor.fetchall()
            
            
            cursor.execute(f"SELECT * FROM warnings WHERE user_id = {user.id}")
            warnings = cursor.fetchall()
            cursor.execute(f"SELECT * FROM timeouts WHERE user_id = {user.id}")
            timeouts = cursor.fetchall()
            cursor.execute(f"SELECT * FROM kicks WHERE user_id = {user.id}")
            kicks = cursor.fetchall()
            cursor.execute(f"SELECT * FROM bans WHERE user_id = {user.id}")
            bans = cursor.fetchall()
            warning = ""
            timeout = ""
            kick = ""
            ban = ""
            for i in range(len(warnings)):
                warning += f"{i+1}. Staff: <@{warnings[i][2]}> Reason: `{warnings[i][1]}` <t:{warnings[i][3]}:D>\n"
            for i in range(len(timeouts)):
                timeout += f"{i+1}. Staff: <@{timeouts[i][2]}> Reason: `{timeouts[i][1]}` Duration: `{timeouts[i][3]}` <t:{timeouts[i][4]}:D>\n"
            for i in range(len(kicks)):
                kick += f"{i+1}. Staff: <@{kicks[i][2]}> Reason: `{kicks[i][1]}` <t:{kicks[i][3]}:D>\n"
            for i in range(len(bans)):
                ban += f"{i+1}. Staff: <@{bans[i][2]}> Reason: `{bans[i][1]}` <t:{bans[i][3]}:D>\n"
            
            if len(warnings) == 0 and len(timeouts) == 0 and len(kicks) == 0 and len(bans) == 0:
                embed = discord.Embed(title=f"{user.name} has no punishments!", color=discord.Color.green())
            else:
                embed = discord.Embed(title=f"Punishments for {user.name}", color=discord.Color.red())
            if len(warnings) == 0:
                pass
            else:
                embed.add_field(name="Warnings", value=warning, inline=False)
            if len(timeouts) == 0:
                pass
            else:
                embed.add_field(name="Timeouts", value=timeout, inline=False)
            if len(kicks) == 0:
                pass
            else:
                embed.add_field(name="Kicks", value=kick, inline=False)
            if len(bans) == 0:
                pass
            else:
                embed.add_field(name="Bans", value=ban, inline=False)
            
            
                
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in `/logs`: {e}")
    
    @app_commands.command(name="add-note", description="Add a note to a user.")
    @app_commands.checks.has_any_role(config.staff)
    async def addNote(self, interaction: discord.Interaction, member: discord.Member, *, note: str):
        today = dt.today()
        timestamp = dt.timestamp(today)
        try:
            cursor.execute(f"INSERT INTO notes (user_id, note, staff_id, timestamp) VALUES ({member.id}, '{note}', {interaction.user.id}, {int(timestamp)})")
            db.commit()
            await interaction.response.send_message(f"Added note to {member.mention}", ephemeral=True)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in `/add-note`: {e}")
    
    @app_commands.command(name="remove-note", description="Removes a note from a user.")
    @app_commands.checks.has_any_role(config.moderator, config.administrators, config.transparent_admin, config.true_admin)
    async def removeNote(self, interaction: discord.Interaction, member: discord.Member, note: int):
        try:
            cursor.execute(f"SELECT * FROM notes WHERE user_id = {member.id}")
            notes = cursor.fetchall()
            if len(notes) < note:
                await interaction.response.send_message("Invalid note number!", ephemeral=True)
                return
            cursor.execute(f"DELETE FROM notes WHERE user_id = {member.id} AND note = '{notes[note-1][1]}' AND staff_id = {notes[note-1][2]} AND timestamp = {notes[note-1][3]}")
            db.commit()
            await interaction.response.send_message(f"Removed note from {member.mention}", ephemeral=True)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in `/remove-note`: {e}")
    
    @app_commands.command(name="notes", description="Shows all of a users notes.")
    @app_commands.checks.has_any_role(config.staff)
    async def notes(self, interaction: discord.Interaction, member: discord.Member):
        try:
            cursor.execute(f"SELECT * FROM notes WHERE user_id = {member.id}")
            notes = cursor.fetchall()
            noteString = ""
            for i in range(len(notes)):
                noteString += f"{i+1}. Note: `{notes[i][1]}` Staff: <@{notes[i][2]}> <t:{notes[i][3]}:D>\n"
            if len(notes) == 0:
                embed = discord.Embed(title=f"{member.name} has no notes!", color=discord.Color.green())
            else:
                embed = discord.Embed(title=f"Notes for {member.name}", description=noteString, color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in `/notes`: {e}")
    
    @app_commands.command(name="unban", description="Unban a user.")
    @app_commands.checks.has_any_role(config.jr_moderator, config.moderator, config.administrators, config.transparent_admin, config.true_admin)
    async def unban(self, interaction: discord.Interaction, user: discord.User, *, reason: str):
        try:
            mod_logs = self.bot.get_channel(config.mod_log_channel)
            embed = discord.Embed(title=f"Unbanned {user.name}", description=f"Reason: {reason}\nStaff: {interaction.user.mention}", color=0x00ff00)
            await interaction.guild.unban(user, reason=reason)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await mod_logs.send(embed=embed)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in `/unban`: {e}")

    @app_commands.command(name="purge", description="Purge a user's messages.")
    @app_commands.describe(amount="The amount of messages to purge.")
    @app_commands.checks.has_any_role(config.moderator, config.administrators, config.transparent_admin, config.true_admin)
    async def purge(self, interaction: discord.Interaction, amount: int, member: discord.Member=None):
        try:
            if member == None:
                await interaction.channel.purge(limit=amount+1)
                await interaction.response.send_message(f"Purged {amount} messages", ephemeral=True)
                return
            await interaction.channel.purge(limit=amount+1, check=lambda m: m.author == member)
            await interaction.response.send_message(f"Purged {amount} messages from {member.mention}", ephemeral=True)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in `/purge`: {e}")


async def setup(bot):
    await bot.add_cog(punishments(bot), guilds=[discord.Object(id=config.server_id)])