import discord
from discord import app_commands, TextStyle, utils
from discord.ext import commands
import config
from dotenv import load_dotenv
import traceback
load_dotenv()



class TicketsModal(discord.ui.Modal, title="Ticket - Pit Community"):
    ign = discord.ui.TextInput(label="In-Game Name", placeholder="e.g. Jzcob", min_length=3, max_length=16, required=True, style= TextStyle.short)
    question = discord.ui.TextInput(label="What's your question for our staff?", style=TextStyle.long, required=True, max_length=4000)
    async def on_submit(self, interaction: discord.Interaction):
        ticket = utils.get(interaction.guild.channels, name=f"ticket-{interaction.user.name.lower()}")
        if ticket is not None:
            return await interaction.response.send_message(content="You already have a ticket open!", ephemeral=True)
        try:
            discord_user = interaction.user
            staffPing = discord.utils.get(interaction.user.guild.roles, id=config.staffTicketPing)
            try:
                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    interaction.guild.me: discord.PermissionOverwrite(read_messages=True),
                    interaction.guild.get_role(config.staff): discord.PermissionOverwrite(read_messages=True),
                    discord_user: discord.PermissionOverwrite(read_messages=True),
                }
                ticketCategory = discord.utils.get(interaction.guild.categories, id=922271313228361829)
                ticketLog = interaction.client.get_channel(config.ticketLog)
                ticketChannel = await interaction.guild.create_text_channel(name=f"ticket-{discord_user.name.lower()}", category=ticketCategory, overwrites=overwrites, reason=f"Ticket opened by {discord_user}")
                embed = discord.Embed(description=f"You have opened a ticket, congratulations\nSomeone will be with you soon.\nOnce we respond, please respond back in a timely manner\n*Don't just ghost us :(*\n\nIGN: {self.ign}\nMessage:\n{self.question}", color=0x00ff00)
                await interaction.response.send_message(content="Ticket created!", ephemeral=True)
                await ticketChannel.send(f"{discord_user.mention} {staffPing.mention}", embed=embed)
                await ticketLog.send(f"Ticket created by {discord_user.mention} in {ticketChannel.mention}")
            except Exception as e:
                print(e)
        except:
            error_channel = self.bot.get_channel(config.error_channel)
            string = f"{traceback.format_exc()}"
            await error_channel.send(f"```{string}```")
            await interaction.response.send_message(content="There was an error submitting your ticket. I have alerted the Developers!", ephemeral=True)



class tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("LOADED: `tickets.py`")
    
    @app_commands.command(name="ticket", description="Open a ticket with the staff team.")
    async def ticket(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_modal(TicketsModal())
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"<@920797181034778655> Error with Tickets!\n ```{e}```")
            await interaction.response.send_message("There was an error opening the ticket. I have alerted the Developers!", ephemeral=True)

    @app_commands.command(name="close", description="Close a ticket.")
    @app_commands.checks.has_any_role(config.staff)

    async def close(self, interaction: discord.Interaction):
        try:
            if interaction.channel.name.startswith("ticket-") and interaction.channel.category_id == 922271313228361829:
                await interaction.response.send_message("Closing the ticket", ephemeral=True)
                try:
                    messages = interaction.channel.history(limit=None)
                    transcriptList = []
                    async for message in messages:
                        timestamp = message.created_at.strftime("%m/%d/%Y @ %H:%M:%S")
                        transcriptList.append(f"{message.author.name} ({timestamp}): {message.content}\n\n")
                    transcript = ""
                    for trans in reversed(transcriptList):
                        transcript += trans
                    with open("transcript.txt", "w", encoding="utf-8") as file:
                        file.write(transcript)
                except Exception as e:
                    error_channel = self.bot.get_channel(config.error_channel)
                    await error_channel.send(f"<@920797181034778655> Error with Tickets!\n ```{e}```")
                    return await interaction.followup.send("There was an error closing the ticket. I have alerted the Developers!", ephemeral=True)
                ticketLog = interaction.client.get_channel(config.ticketLog)
                adminTicketLog = interaction.client.get_channel(config.adminTicketLog)
                await adminTicketLog.send(file=discord.File("transcript.txt"), content=f"Ticket closed by {interaction.user.name}")
                await ticketLog.send(content=f"`{interaction.channel.name}` closed by `{interaction.user.name}`")
                await interaction.channel.delete(reason=f"Ticket closed by {interaction.user}")
                
            else:
                await interaction.response.send_message("This is not a ticket channel!", ephemeral=True)
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"<@920797181034778655> Error with Tickets!\n ```{e}```")
            await interaction.response.send_message("There was an error closing the ticket. I have alerted the Developers!", ephemeral=True)
            with open("transcript.txt", "w", encoding="utf-8") as file:
                file.write("")

async def setup(bot):
    await bot.add_cog(tickets(bot), guilds=[discord.Object(id=config.server_id)])