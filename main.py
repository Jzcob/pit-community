import discord
from discord.ext import commands
import os
import config
from dotenv import load_dotenv
import asyncio
load_dotenv()

import mysql.connector
db = mysql.connector.connect(
    host=os.getenv("punishments_host"),
    user=os.getenv("punishments_user"),
    password=os.getenv("punishments_password"),
    database=os.getenv("punishments_database")
)
cursor = db.cursor()


intents = discord.Intents.all()
intents.members = True
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix='!', intents=intents)
status = discord.Status.online
activity = discord.Game("Pit")
bot.remove_command('help')

@bot.command()
async def sync(ctx):
    if ctx.author.id in config.bot_authors and ctx.channel.id == 922273598801084506:
        try:
            fmt = await ctx.bot.tree.sync()
            print(f"Synced {len(fmt)} commands.")
            embed = discord.Embed(title="Synced", description=f"Synced {len(fmt)} commands.", color=0x00ff00)
            await ctx.send(embed=embed)
            return
        except Exception as e:
            print(e)
    else:
        embed = discord.Embed(title="Error", description="This is a bot admin command restricted to only the bot owner, used to sync the global commands with the discord api.", color=0xff0000)
        await ctx.send(embed=embed)

@bot.command()
async def syncserver(ctx) -> None:
    if ctx.author.id in config.bot_authors:
        try:
            fmt = await ctx.bot.tree.sync(guild=ctx.guild)
            print(f"Synced {len(fmt)} commands.")
            embed = discord.Embed(title="Synced", description=f"Synced {len(fmt)} commands.", color=0x00ff00)
            await ctx.send(embed=embed)
            return
        except Exception as e:
            print(e)
    else:
        embed = discord.Embed(title="Error", description="This is a bot admin command restricted to only the bot owner, used to sync the server commands with the discord api.", color=0xff0000)
        await ctx.send(embed=embed)

@bot.tree.context_menu(name="Level", guilds=[discord.Object(id=config.server_id)])
async def level(interaction: discord.Interaction, user: discord.User):
    try:
        cursor.execute(f"SELECT * FROM levels WHERE user_id = {user.id}")
        result = cursor.fetchone()
        if result is None:
            embed = discord.Embed(title="Level", description=f"{user.mention} has not chatted!", color=0x00ff00)
            await interaction.response.send_message(embed=embed)
        else:
            xp = result[1]
            level = result[2]
            embed = discord.Embed(title="Level", description=f"{user.mention} is level {level} with {xp} xp.", color=0x00ff00)
            embed.set_author(name=user, icon_url=user.display_avatar)
            await interaction.response.send_message(embed=embed)
        return
    except Exception as e:
        error_channel = bot.get_channel(config.error_channel)
        await error_channel.send(f"```Error in `level context menu`\n{e}\n```")

@bot.tree.context_menu(name="Level Leaderboard", guilds=[discord.Object(id=config.server_id)])
async def level_leaderboard(interaction: discord.Interaction, user: discord.User):
    try:
        cursor.execute(f"SELECT COUNT(*) FROM levels")
        count = cursor.fetchone()[0]
        cursor.execute(f"SELECT * FROM levels ORDER BY level DESC, xp DESC LIMIT 10")
        result = cursor.fetchall()
        embed = discord.Embed(color=0x00ff00)
        embed.set_author(name="Leaderboard for Pit Community", icon_url=bot.user.display_avatar)
        top = ""
        for i in range(len(result)):
            user1 = await bot.fetch_user(result[i][0])
            level = result[i][2]
            xp = result[i][1]
            if user.id == user1.id:
                top += f"**{i+1}.** **{user1.mention}\nLevel `{level}` with `{xp}` xp**\n"
            else:
                top += f"**{i+1}.** {user1.mention}\nLevel `{level}` with `{xp}` xp\n"
        embed.description = top
        if count > 10:
            embed.set_footer(text=f"1-10 out of {count}")
        else:
            embed.set_footer(text=f"1-{count} out of {count}")
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        error_channel = bot.get_channel(config.error_channel)
        await error_channel.send(f"```Error in `level_leaderboard context menu`\n{e}\n```")


@bot.tree.context_menu(name="Reset Level", guilds=[discord.Object(id=config.server_id)])
async def reset_level(interaction: discord.Interaction, user: discord.User):
    try:
        def check(m):
            return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id and m.content.lower() == "yes"
        embed = discord.Embed(title="Reset Level", description=f"Are you sure you want to reset {user.mention}'s level?", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        try:
            msg = await bot.wait_for('message', check=check, timeout=30)
            if msg.content.lower() == "no":
                embed = discord.Embed(title="Reset Level", description=f"Cancelled.", color=0xff0000)
                await interaction.followup.send(embed=embed)
                return
            else:
                pass
        except asyncio.TimeoutError:
            embed = discord.Embed(title="Reset Level", description=f"Timed out.", color=0xff0000)
            await interaction.followup.send(embed=embed)
            return
        cursor.execute(f"SELECT * FROM levels WHERE user_id = {user.id}")
        result = cursor.fetchone()
        if result is None:
            embed = discord.Embed(title="Error", description="This user does not have any levels.", color=0xff0000)
            await interaction.followup.send(embed=embed)
        else:
            cursor.execute(f"DELETE FROM levels WHERE user_id = {user.id}")
            db.commit()
            embed = discord.Embed(title="Reset Level", description=f"Reset {user.mention}'s level.", color=0x00ff00)
            await interaction.followup.send(embed=embed)
    except Exception as e:
        error_channel = bot.get_channel(config.error_channel)
        await error_channel.send(f"```Error in reset level context menu\n{e}\n```")


"""
def create_warnings_table():
    cursor.execute("CREATE TABLE IF NOT EXISTS warnings (user_id BIGINT, reason VARCHAR(255), staff_id BIGINT, timestamp BIGINT)")
    db.commit()

def create_timeout_table():
    cursor.execute("CREATE TABLE IF NOT EXISTS timeouts (user_id BIGINT, reason VARCHAR(255), staff_id BIGINT, time VARCHAR(255), timestamp BIGINT)")
    db.commit()

def create_bans_table():
    cursor.execute("CREATE TABLE IF NOT EXISTS bans (user_id BIGINT, reason VARCHAR(255), staff_id BIGINT, timestamp BIGINT)")
    db.commit()

def create_kicks_table():
    cursor.execute("CREATE TABLE IF NOT EXISTS kicks (user_id BIGINT, reason VARCHAR(255), staff_id BIGINT, timestamp BIGINT)")
    db.commit()

def create_notes_table():
    cursor.execute("CREATE TABLE IF NOT EXISTS notes (user_id BIGINT, note VARCHAR(255), staff_id BIGINT, timestamp BIGINT)")
    db.commit()

def create_levels_table():
    cursor.execute("CREATE TABLE IF NOT EXISTS levels (user_id BIGINT, xp BIGINT, level BIGINT)")
    db.commit()
"""


@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}")

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'FOUND: `{filename}`')

async def main():
    await load()
    """create_warnings_table()
    create_timeout_table()
    create_bans_table()
    create_kicks_table()
    create_notes_table()
    create_levels_table()"""
    await bot.start(os.getenv("token"))

asyncio.run(main())