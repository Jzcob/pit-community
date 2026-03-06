import discord
from discord.ext import commands
import config
from datetime import datetime
import asyncio

class logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("LOADED: `logs.py`")

    def get_log_channel(self):
        return self.bot.get_channel(config.log_channel)

    async def get_audit_entry(self, guild, action):
        """Finds the most recent audit log entry for a specific action within 5 seconds."""
        try:
            async for entry in guild.audit_logs(limit=1, action=action):
                if (discord.utils.utcnow() - entry.created_at).total_seconds() < 5:
                    return entry
        except:
            return None
        return None

    # --- Server Events ---
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if not isinstance(channel, (discord.TextChannel, discord.VoiceChannel)): return
        embed = discord.Embed(title="Channel Created", color=0x2ecc71, timestamp=datetime.now())
        embed.add_field(name="Name", value=f"{channel.name} ({channel.mention})")
        embed.add_field(name="Category", value=getattr(channel.category, "name", "None"))
        
        entry = await self.get_audit_entry(channel.guild, discord.AuditLogAction.channel_create)
        if entry: embed.set_footer(text=f"Created by {entry.user}", icon_url=entry.user.display_avatar.url)
        await self.get_log_channel().send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        embed = discord.Embed(title="Channel Deleted", color=0xe74c3c, timestamp=datetime.now())
        embed.add_field(name="Name", value=channel.name)
        
        entry = await self.get_audit_entry(channel.guild, discord.AuditLogAction.channel_delete)
        if entry: embed.set_footer(text=f"Deleted by {entry.user}", icon_url=entry.user.display_avatar.url)
        await self.get_log_channel().send(embed=embed)

    # --- Member Events ---
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        log_channel = self.get_log_channel()
        if before.nick != after.nick:
            embed = discord.Embed(title="Nickname Updated", color=0x3498db)
            embed.set_author(name=after.display_name, icon_url=after.display_avatar.url)
            embed.add_field(name="Before", value=before.nick or "None")
            embed.add_field(name="After", value=after.nick or "None")
            await log_channel.send(embed=embed)

        if before.roles != after.roles:
            embed = discord.Embed(color=0x3498db, timestamp=datetime.now())
            embed.set_author(name=after.display_name, icon_url=after.display_avatar.url)
            if len(before.roles) < len(after.roles):
                new_role = next(role for role in after.roles if role not in before.roles)
                embed.title = "Role Added"
                embed.description = f"{after.mention} was given the {new_role.mention} role."
            else:
                removed_role = next(role for role in before.roles if role not in after.roles)
                embed.title = "Role Removed"
                embed.description = f"{after.mention} lost the {removed_role.mention} role."
            
            entry = await self.get_audit_entry(after.guild, discord.AuditLogAction.member_role_update)
            if entry: embed.set_footer(text=f"Staff: {entry.user}")
            await log_channel.send(embed=embed)

    # --- Message Events ---
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.content: return
        embed = discord.Embed(title="Message Deleted", color=0xe74c3c, timestamp=datetime.now())
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.description = f"**Channel:** {message.channel.mention}\n**Content:**\n{message.content[:1024]}"
        
        entry = await self.get_audit_entry(message.guild, discord.AuditLogAction.message_delete)
        if entry and entry.target.id == message.author.id:
            embed.set_footer(text=f"Moderator: {entry.user}")
        await self.get_log_channel().send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content: return
        embed = discord.Embed(title="Message Edited", color=0xf1c40f, timestamp=datetime.utcnow())
        embed.set_author(name=before.author.display_name, icon_url=before.author.display_avatar.url)
        embed.add_field(name="Before", value=before.content[:1024] or "Empty", inline=False)
        embed.add_field(name="After", value=after.content[:1024] or "Empty", inline=False)
        await self.get_log_channel().send(embed=embed)

    # --- Voice Events ---
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot or before.channel == after.channel: return
        embed = discord.Embed(timestamp=datetime.utcnow())
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        
        if before.channel is None:
            embed.title, embed.color, embed.description = "Voice Join", 0x2ecc71, f"Joined {after.channel.mention}"
        elif after.channel is None:
            embed.title, embed.color, embed.description = "Voice Leave", 0xe74c3c, f"Left {before.channel.mention}"
        else:
            embed.title, embed.color, embed.description = "Voice Move", 0x3498db, f"{before.channel.name} -> {after.channel.name}"
        
        await self.get_log_channel().send(embed=embed)

    # --- Join/Leave ---
    @commands.Cog.listener()
    async def on_member_join(self, member):
        invite_log = self.bot.get_channel(499001163278975006)
        count = len(member.guild.members)
        suffix = 'th' if 11 <= (count % 100) <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(count % 10, 'th')
        embed = discord.Embed(title="Member Joined", description=f"{member.mention} is member **#{count}{suffix}**", color=0x2ecc71)
        embed.set_thumbnail(url=member.display_avatar.url)
        await invite_log.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        invite_log = self.bot.get_channel(499001163278975006)
        roles = ", ".join([r.mention for r in member.roles[1:]])[:1024] or "None"
        embed = discord.Embed(title="Member Left", color=0xe74c3c, timestamp=datetime.utcnow())
        embed.set_author(name=member.name, icon_url=member.display_avatar.url)
        embed.add_field(name="Roles", value=roles)
        
        entry = await self.get_audit_entry(member.guild, discord.AuditLogAction.kick)
        if entry and entry.target.id == member.id:
            embed.title = "Member Kicked"
            embed.add_field(name="By", value=entry.user.mention)
        await invite_log.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        if message.attachments:
            img_log = self.bot.get_channel(736794546767396864)
            for attach in message.attachments:
                if "image" in (attach.content_type or ""):
                    await img_log.send(f"Image from {message.author.mention} in {message.channel.mention}:\n{attach.url}")

async def setup(bot):
    await bot.add_cog(logs(bot))