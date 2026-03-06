import discord
from discord.ext import commands
from discord import app_commands
import os
import config
from dotenv import load_dotenv
import asyncio
import traceback
import mysql.connector
from contextlib import contextmanager

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

@contextmanager
def get_db():
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

# --- Admin Sync Commands ---

@bot.command()
async def sync(ctx):
    if ctx.author.id in config.bot_authors and ctx.channel.id == 922273598801084506:
        fmt = await ctx.bot.tree.sync()
        await ctx.send(embed=discord.Embed(title="Synced", description=f"Synced {len(fmt)} global commands.", color=0x00ff00))
    else:
        await ctx.send(embed=discord.Embed(title="Error", description="Unauthorized.", color=0xff0000))

# --- Context Menus ---

@bot.tree.context_menu(name="Level", guilds=[discord.Object(id=config.server_id)])
async def level(interaction: discord.Interaction, user: discord.User):
    await interaction.response.defer(ephemeral=False)
    try:
        with get_db() as (db, cursor):
            cursor.execute("SELECT xp, level FROM levels WHERE user_id = %s", (user.id,))
            result = cursor.fetchone()
            
            if result is None:
                return await interaction.followup.send(f"{user.mention} has not chatted yet!")
            
            xp, level_val = result
            embed = discord.Embed(title="Level Stats", description=f"{user.mention} is level **{level_val}** with **{xp}** XP.", color=0x00ff00)
            embed.set_author(name=user.name, icon_url=user.display_avatar.url)
            await interaction.followup.send(embed=embed)
    except Exception:
        await bot.get_channel(config.error_channel).send(f"```python\n{traceback.format_exc()}```")

@bot.tree.context_menu(name="Level Leaderboard", guilds=[discord.Object(id=config.server_id)])
async def level_leaderboard(interaction: discord.Interaction, user: discord.User):
    await interaction.response.defer()
    try:
        with get_db() as (db, cursor):
            cursor.execute("SELECT COUNT(*) FROM levels")
            count = cursor.fetchone()[0]
            
            cursor.execute("SELECT user_id, xp, level FROM levels ORDER BY level DESC, xp DESC LIMIT 10")
            results = cursor.fetchall()
            
            embed = discord.Embed(color=0x00ff00)
            embed.set_author(name="Leaderboard for Pit Community", icon_url=bot.user.display_avatar.url)
            
            description_lines = []
            for i, (uid, xp, lv) in enumerate(results):
                member = bot.get_user(uid) or await bot.fetch_user(uid)
                mention = member.mention if member else f"Unknown ({uid})"
                
                line = f"**{i+1}.** {mention}\nLevel `{lv}` with `{xp}` XP"
                if uid == user.id:
                    line = f"**{i+1}.** **{mention} (YOU)**\nLevel `{lv}` with `{xp}` XP"
                
                description_lines.append(line)
            
            embed.description = "\n".join(description_lines)
            embed.set_footer(text=f"Showing 1-10 out of {count}")
            await interaction.followup.send(embed=embed)
    except Exception:
        await bot.get_channel(config.error_channel).send(f"```python\n{traceback.format_exc()}```")

@bot.tree.context_menu(name="Reset Level", guilds=[discord.Object(id=config.server_id)])
async def reset_level(interaction: discord.Interaction, user: discord.User):
    await interaction.response.send_message(f"⚠️ Are you sure you want to reset {user.mention}'s levels? Type `yes` to confirm.", ephemeral=True)
    
    def check(m):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id and m.content.lower() == "yes"

    try:
        await bot.wait_for('message', check=check, timeout=15)
        with get_db() as (db, cursor):
            cursor.execute("DELETE FROM levels WHERE user_id = %s", (user.id,))
            db.commit()
            await interaction.followup.send(f"✅ Reset {user.mention}'s levels.", ephemeral=True)
    except asyncio.TimeoutError:
        await interaction.followup.send("❌ Reset cancelled (Timed out).", ephemeral=True)
    except Exception:
        await bot.get_channel(config.error_channel).send(f"```python\n{traceback.format_exc()}```")

# --- Initialization ---

@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}")

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'LOADED COG: {filename}')

async def main():
    async with bot:
        await load()
        await bot.start(os.getenv("token"))

if __name__ == "__main__":
    asyncio.run(main())