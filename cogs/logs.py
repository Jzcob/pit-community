import discord
from discord.ext import commands
import config
from datetime import datetime
import traceback
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
        """Attempts to find the most recent audit log entry for a specific action."""
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
        embed = discord.Embed(title="Channel Created", color=0x2ecc71, timestamp=datetime.utcnow())
        embed.add_field(name="Name", value=f"{channel.name} ({channel.mention})")
        embed.add_field(name="Type", value=str(channel.type).upper())
        embed.add_field(name="Category", value=getattr(channel.category, "name", "None"))
        
        entry = await self.get_audit_entry(channel.guild, discord.AuditLogAction.channel_create)
        if entry: embed.set_footer(text=f"Created by {entry.user}", icon_url=entry.user.display_avatar.url)
        
        await self.get_log_channel().send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        embed = discord.Embed(title="Channel Deleted", color=0xe74c3c, timestamp=datetime.utcnow())
        embed.add_field(name="Name", value=channel.name)
        embed.add_field(name="ID", value=channel.id)
        
        entry = await self.get_audit_entry(channel.guild, discord.AuditLogAction.channel_delete)
        if entry: embed.set_footer(text=f"Deleted by {entry.user}", icon_url=entry.user.display_avatar.url)
        
        await self.get_log_channel().send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        embed = discord.Embed(title="Role Created", color=role.color if role.color.value != 0 else 0x2ecc71, timestamp=datetime.utcnow())
        embed.add_field(name="Name", value=role.name)
        embed.add_field(name="ID", value=role.id)
        
        entry = await self.get_audit_entry(role.guild, discord.AuditLogAction.role_create)
        if entry: embed.set_footer(text=f"Created by {entry.user}")
        
        await self.get_log_channel().send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        embed = discord.Embed(title="Role Deleted", color=0xe74c3c, timestamp=datetime.utcnow())
        embed.add_field(name="Name", value=role.name)
        
        entry = await self.get_audit_entry(role.guild, discord.AuditLogAction.role_delete)
        if entry: embed.set_footer(text=f"Deleted by {entry.user}")
        
        await self.get_log_channel().send(embed=embed)

    # --- Member Events ---

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        log_channel = self.get_log_channel()
        
        # Nickname Change
        if before.nick != after.nick:
            embed = discord.Embed(title="Nickname Update", color=0x3498db)
            embed.set_author(name=after.display_name, icon_url=after.display_avatar.url)
            embed.add_field(name="Before", value=before.nick or "None")
            embed.add_field(name="After", value=after.nick or "None")
            await log_channel.send(embed=embed)

        # Role Changes
        if before.roles != after.roles:
            embed = discord.Embed(color=0x3498db, timestamp=datetime.utcnow())
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
            if entry: embed.set_footer(text=f"Responsible Staff: {entry.user}")
            
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.name != after.name or before.avatar != after.avatar:
            embed = discord.Embed(title="User Profile Updated", color=0x9b59b6)
            embed.set_author(name=after.name, icon_url=after.display_avatar.url)
            if before.name != after.name:
                embed.add_field(name="Username", value=f"{before.name} -> {after.name}")
            if before.avatar != after.avatar:
                embed.set_thumbnail(url=after.display_avatar.url)
                embed.description = "User changed their avatar."
            await self.get_log_channel().send(embed=embed)

    # --- Message Events ---

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.content: return
        
        embed = discord.Embed(title="Message Deleted", color=0xe74c3c, timestamp=datetime.utcnow())
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.description = f"**Channel:** {message.channel.mention}\n**Content:**\n{message.content[:1024]}"
        
        entry = await self.get_audit_entry(message.guild, discord.AuditLogAction.message_delete)
        if entry and entry.target.id == message.author.id:
            embed.set_footer(text=f"Deleted by {entry.user}")
            
        await self.get_log_channel().send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content: return
        
        embed = discord.Embed(title="Message Edited", color=0xf1c40f, timestamp=datetime.utcnow())
        embed.set_author(name=before.author.display_name, icon_url=before.author.display_avatar.url)
        embed.add_field(name="Before", value=before.content[:1024] or "Empty", inline=False)
        embed.add_field(name="After", value=after.content[:1024] or "Empty", inline=False)
        embed.set_footer(text=f"Channel: #{before.channel.name}")
        
        await self.get_log_channel().send(embed=embed)

    # --- Voice Events ---

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot: return
        log_channel = self.get_log_channel()
        
        if before.channel != after.channel:
            embed = discord.Embed(timestamp=datetime.utcnow())
            embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
            
            if before.channel is None:
                embed.title, embed.color = "Voice Join", 0x2ecc71
                embed.description = f"{member.mention} joined {after.channel.mention}"
            elif after.channel is None:
                embed.title, embed.color = "Voice Leave", 0xe74c3c
                embed.description = f"{member.mention} left {before.channel.mention}"
            else:
                embed.title, embed.color = "Voice Move", 0x3498db
                embed.description = f"{member.mention} moved: {before.channel.mention} -> {after.channel.mention}"
            
            await log_channel.send(embed=embed)

    # --- Member Join/Leave ---

    @commands.Cog.listener()
    async def on_member_join(self, member):
        invite_log = self.bot.get_channel(499001163278975006)
        count = len(member.guild.members)
        
        suffix = 'th' if 11 <= (count % 100) <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(count % 10, 'th')

        embed = discord.Embed(title="Member Joined", description=f"{member.mention} is our **{count}{suffix}** member!", color=0x2ecc71)
        embed.set_thumbnail(url=member.display_avatar.url)
        await invite_log.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        invite_log = self.bot.get_channel(499001163278975006)
        roles = ", ".join([r.mention for r in member.roles[1:]]) or "None"
        
        embed = discord.Embed(title="Member Left / Kicked", color=0xe74c3c, timestamp=datetime.utcnow())
        embed.set_author(name=member.name, icon_url=member.display_avatar.url)
        embed.add_field(name="Roles Held", value=roles[:1024])
        
        entry = await self.get_audit_entry(member.guild, discord.AuditLogAction.kick)
        if entry and entry.target.id == member.id:
            embed.title = "Member Kicked"
            embed.add_field(name="Kicked by", value=entry.user.mention)
            embed.add_field(name="Reason", value=entry.reason or "No reason provided")

        await invite_log.send(embed=embed)

async def setup(bot):
    await bot.add_cog(logs(bot))