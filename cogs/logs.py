import discord
from discord.ext import commands
from discord import app_commands
import mysql.connector
import config
from datetime import datetime
import datetime
import discord
#Server Events
"""
channel creation
update channel
channel deletion
role creation
role updates
role deletion
server updates
emoji changes
"""
#Member events
"""
role updates
name changes
avatar changes
member bans
member unbans
member timeouts
member remove timeouts
"""
#Message events
"""
delete messages
edit messages
purged messages (bulk delete)
discord invites
"""
#Voice events
"""
join voice channel
move between voice channels
leave voice channel
"""
#Member Join and Leave
"""
member joining
member leaving
"""

class logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("LOADED: `logs.py")

##### Server Events #####
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        embed = discord.Embed(title="Channel Created", description=f"Channel {channel.mention} created.", color=0x00ff00)
        embed.add_field(name="Name", value=channel.name, inline=False)
        embed.add_field(name="Topic", value=channel.topic, inline=False)
        embed.add_field(name="Category", value=channel.category, inline=False)
        embed.add_field(name="Position", value=channel.position, inline=False)
        embed.add_field(name="Slowmode Delay", value=channel.slowmode_delay, inline=False)
        embed.add_field(name="NSFW", value=channel.is_nsfw(), inline=False)
        embed.add_field(name="Is Announcement Channel", value=channel.is_news(), inline=False)
        embed.add_field(name="Is Synced", value=channel.is_synced(), inline=False)
        embed.add_field(name="Permissions Synced", value=channel.permissions_synced(), inline=False)
        embed.add_field(name="Permissions Locked", value=channel.permissions_locked(), inline=False)
        embed.add_field(name="Overwrites", value=channel.overwrites, inline=False)
        embed.add_field(name="Type", value=channel.type, inline=False)
        embed.add_field(name="ID", value=channel.id, inline=False)
        logs = self.bot.get_channel(config.log_channel)
        await logs.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        embed = discord.Embed(title="Channel Updated", description=f"Channel {after.mention} updated.", color=0x00ff00)
        if before.name != after.name:
            embed.add_field(name="Name Before", value=before.name, inline=False)
            embed.add_field(name="Name After", value=after.name, inline=False)
        elif before.topic != after.topic:
            embed.add_field(name="Topic Before", value=before.topic, inline=False)
            embed.add_field(name="Topic After", value=after.topic, inline=False)
        elif before.category != after.category:
            embed.add_field(name="Category Before", value=before.category, inline=False)
            embed.add_field(name="Category After", value=after.category, inline=False)
        elif before.slowmode_delay != after.slowmode_delay:
            embed.add_field(name="Slowmode Before", value=before.slowmode_delay, inline=False)
            embed.add_field(name="Position After", value=after.slowmode_delay, inline=False)
        elif before.is_nsfw() != after.is_nsfw():
            embed.add_field(name="NSFW state Before", value=before.is_nsfw(), inline=False)
            embed.add_field(name="NSFW state After", value=after.is_nsfw(), inline=False)
        elif before.is_news() != after.is_news():
            embed.add_field(name="Is Announcement Channel Before", value=before.is_news(), inline=False)
            embed.add_field(name="Is Announcement Channel After", value=after.is_news(), inline=False)
        elif before.is_synced() != after.is_synced():
            embed.add_field(name="Is Synced Before", value=before.is_synced(), inline=False)
            embed.add_field(name="Is Synced After", value=after.is_synced(), inline=False)
        elif before.permissions_synced() != after.permissions_synced():
            embed.add_field(name="Permissions Synced Before", value=before.permissions_synced(), inline=False)
            embed.add_field(name="Permissions Synced After", value=after.permissions_synced(), inline=False)
        elif before.permissions_locked() != after.permissions_locked():
            embed.add_field(name="Permissions Locked Before", value=before.permissions_locked(), inline=False)
            embed.add_field(name="Permissions Locked After", value=after.permissions_locked(), inline=False)
        elif before.overwrites != after.overwrites:
            embed.add_field(name="Overwrites Before", value=before.overwrites, inline=False)
            embed.add_field(name="Overwrites After", value=after.overwrites, inline=False)
        elif before.type != after.type:
            embed.add_field(name="Type Before", value=before.type, inline=False)
            embed.add_field(name="Type After", value=after.type, inline=False)
        elif before.id != after.id:
            embed.add_field(name="ID Before", value=before.id, inline=False)
            embed.add_field(name="ID After", value=after.id, inline=False)
        else:
            embed.add_field(name="Unknown Change", value="Unknown Change", inline=False)
        logs = self.bot.get_channel(config.log_channel)
        await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        embed = discord.Embed(title="Channel Deleted", description=f"Channel {channel.mention} deleted.", color=0x00ff00)
        embed.add_field(name="Name", value=channel.name, inline=False)
        embed.add_field(name="Topic", value=channel.topic, inline=False)
        embed.add_field(name="Category", value=channel.category, inline=False)
        embed.add_field(name="Position", value=channel.position, inline=False)
        embed.add_field(name="Slowmode Delay", value=channel.slowmode_delay, inline=False)
        embed.add_field(name="NSFW", value=channel.is_nsfw(), inline=False)
        embed.add_field(name="Is Announcement Channel", value=channel.is_news(), inline=False)
        embed.add_field(name="Is Synced", value=channel.is_synced(), inline=False)
        embed.add_field(name="Permissions Synced", value=channel.permissions_synced(), inline=False)
        embed.add_field(name="Permissions Locked", value=channel.permissions_locked(), inline=False)
        embed.add_field(name="Overwrites", value=channel.overwrites, inline=False)
        embed.add_field(name="Type", value=channel.type, inline=False)
        embed.add_field(name="ID", value=channel.id, inline=False)
        logs = self.bot.get_channel(config.log_channel)
        await logs.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        embed = discord.Embed(title="Role Created", description=f"Role {role.mention} created.", color=0x00ff00)
        embed.add_field(name="Name", value=role.name, inline=False)
        embed.add_field(name="Color", value=role.color, inline=False)
        embed.add_field(name="Hoist", value=role.hoist, inline=False)
        embed.add_field(name="Position", value=role.position, inline=False)
        embed.add_field(name="Permissions", value=role.permissions, inline=False)
        embed.add_field(name="Managed", value=role.managed, inline=False)
        embed.add_field(name="Mentionable", value=role.mentionable, inline=False)
        embed.add_field(name="ID", value=role.id, inline=False)
        logs = self.bot.get_channel(config.log_channel)
        await logs.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        embed = discord.Embed(title="Role Updated", description=f"Role {after.mention} updated.", color=0x00ff00)
        if before.name != after.name:
            embed.add_field(name="Name Before", value=before.name, inline=False)
            embed.add_field(name="Name After", value=after.name, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.color != after.color:
            embed.add_field(name="Color Before", value=before.color, inline=False)
            embed.add_field(name="Color After", value=after.color, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.hoist != after.hoist:
            embed.add_field(name="Hoist Before", value=before.hoist, inline=False)
            embed.add_field(name="Hoist After", value=after.hoist, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.permissions != after.permissions:
            if before.permissions.administrator != after.permissions.administrator:
                embed.add_field(name="Administrator Before", value=before.permissions.administrator, inline=False)
                embed.add_field(name="Administrator After", value=after.permissions.administrator, inline=False)
            elif before.permissions.create_instant_invite != after.permissions.create_instant_invite:
                embed.add_field(name="Create Instant Invite Before", value=before.permissions.create_instant_invite, inline=False)
                embed.add_field(name="Create Instant Invite After", value=after.permissions.create_instant_invite, inline=False)
            elif before.permissions.kick_members != after.permissions.kick_members:
                embed.add_field(name="Kick Members Before", value=before.permissions.kick_members, inline=False)
                embed.add_field(name="Kick Members After", value=after.permissions.kick_members, inline=False)
            elif before.permissions.ban_members != after.permissions.ban_members:
                embed.add_field(name="Ban Members Before", value=before.permissions.ban_members, inline=False)
                embed.add_field(name="Ban Members After", value=after.permissions.ban_members, inline=False)
            elif before.permissions.manage_channels != after.permissions.manage_channels:
                embed.add_field(name="Manage Channels Before", value=before.permissions.manage_channels, inline=False)
                embed.add_field(name="Manage Channels After", value=after.permissions.manage_channels, inline=False)
            elif before.permissions.manage_guild != after.permissions.manage_guild:
                embed.add_field(name="Manage Guild Before", value=before.permissions.manage_guild, inline=False)
                embed.add_field(name="Manage Guild After", value=after.permissions.manage_guild, inline=False)
            elif before.permissions.add_reactions != after.permissions.add_reactions:
                embed.add_field(name="Add Reactions Before", value=before.permissions.add_reactions, inline=False)
                embed.add_field(name="Add Reactions After", value=after.permissions.add_reactions, inline=False)
            elif before.permissions.view_audit_log != after.permissions.view_audit_log:
                embed.add_field(name="View Audit Log Before", value=before.permissions.view_audit_log, inline=False)
                embed.add_field(name="View Audit Log After", value=after.permissions.view_audit_log, inline=False)
            elif before.permissions.priority_speaker != after.permissions.priority_speaker:
                embed.add_field(name="Priority Speaker Before", value=before.permissions.priority_speaker, inline=False)
                embed.add_field(name="Priority Speaker After", value=after.permissions.priority_speaker, inline=False)
            elif before.permissions.stream != after.permissions.stream:
                embed.add_field(name="Stream Before", value=before.permissions.stream, inline=False)
                embed.add_field(name="Stream After", value=after.permissions.stream, inline=False)
            elif before.permissions.view_channel != after.permissions.view_channel:
                embed.add_field(name="View Channel Before", value=before.permissions.view_channel, inline=False)
                embed.add_field(name="View Channel After", value=after.permissions.view_channel, inline=False)
            elif before.permissions.send_messages != after.permissions.send_messages:
                embed.add_field(name="Send Messages Before", value=before.permissions.send_messages, inline=False)
                embed.add_field(name="Send Messages After", value=after.permissions.send_messages, inline=False)
            elif before.permissions.send_tts_messages != after.permissions.send_tts_messages:
                embed.add_field(name="Send TTS Messages Before", value=before.permissions.send_tts_messages, inline=False)
                embed.add_field(name="Send TTS Messages After", value=after.permissions.send_tts_messages, inline=False)
            elif before.permissions.manage_messages != after.permissions.manage_messages:
                embed.add_field(name="Manage Messages Before", value=before.permissions.manage_messages, inline=False)
                embed.add_field(name="Manage Messages After", value=after.permissions.manage_messages, inline=False)
            elif before.permissions.embed_links != after.permissions.embed_links:
                embed.add_field(name="Embed Links Before", value=before.permissions.embed_links, inline=False)
                embed.add_field(name="Embed Links After", value=after.permissions.embed_links, inline=False)
            elif before.permissions.attach_files != after.permissions.attach_files:
                embed.add_field(name="Attach Files Before", value=before.permissions.attach_files, inline=False)
                embed.add_field(name="Attach Files After", value=after.permissions.attach_files, inline=False)
            elif before.permissions.read_message_history != after.permissions.read_message_history:
                embed.add_field(name="Read Message History Before", value=before.permissions.read_message_history, inline=False)
                embed.add_field(name="Read Message History After", value=after.permissions.read_message_history, inline=False)
            elif before.permissions.mention_everyone != after.permissions.mention_everyone:
                embed.add_field(name="Mention Everyone Before", value=before.permissions.mention_everyone, inline=False)
                embed.add_field(name="Mention Everyone After", value=after.permissions.mention_everyone, inline=False)
            elif before.permissions.use_external_emojis != after.permissions.use_external_emojis:
                embed.add_field(name="Use External Emojis Before", value=before.permissions.use_external_emojis, inline=False)
                embed.add_field(name="Use External Emojis After", value=after.permissions.use_external_emojis, inline=False)
            elif before.permissions.view_guild_insights != after.permissions.view_guild_insights:
                embed.add_field(name="View Guild Insights Before", value=before.permissions.view_guild_insights, inline=False)
                embed.add_field(name="View Guild Insights After", value=after.permissions.view_guild_insights, inline=False)
            elif before.permissions.connect != after.permissions.connect:
                embed.add_field(name="Connect Before", value=before.permissions.connect, inline=False)
                embed.add_field(name="Connect After", value=after.permissions.connect, inline=False)
            elif before.permissions.speak != after.permissions.speak:
                embed.add_field(name="Speak Before", value=before.permissions.speak, inline=False)
                embed.add_field(name="Speak After", value=after.permissions.speak, inline=False)
            elif before.permissions.mute_members != after.permissions.mute_members:
                embed.add_field(name="Mute Members Before", value=before.permissions.mute_members, inline=False)
                embed.add_field(name="Mute Members After", value=after.permissions.mute_members, inline=False)
            elif before.permissions.deafen_members != after.permissions.deafen_members:
                embed.add_field(name="Deafen Members Before", value=before.permissions.deafen_members, inline=False)
                embed.add_field(name="Deafen Members After", value=after.permissions.deafen_members, inline=False)
            elif before.permissions.move_members != after.permissions.move_members:
                embed.add_field(name="Move Members Before", value=before.permissions.move_members, inline=False)
                embed.add_field(name="Move Members After", value=after.permissions.move_members, inline=False)
            elif before.permissions.use_voice_activation != after.permissions.use_voice_activation:
                embed.add_field(name="Use Voice Activation Before", value=before.permissions.use_voice_activation, inline=False)
                embed.add_field(name="Use Voice Activation After", value=after.permissions.use_voice_activation, inline=False)
            elif before.permissions.change_nickname != after.permissions.change_nickname:
                embed.add_field(name="Change Nickname Before", value=before.permissions.change_nickname, inline=False)
                embed.add_field(name="Change Nickname After", value=after.permissions.change_nickname, inline=False)
            elif before.permissions.manage_nicknames != after.permissions.manage_nicknames:
                embed.add_field(name="Manage Nicknames Before", value=before.permissions.manage_nicknames, inline=False)
                embed.add_field(name="Manage Nicknames After", value=after.permissions.manage_nicknames, inline=False)
            elif before.permissions.manage_roles != after.permissions.manage_roles:
                embed.add_field(name="Manage Roles Before", value=before.permissions.manage_roles, inline=False)
                embed.add_field(name="Manage Roles After", value=after.permissions.manage_roles, inline=False)
            elif before.permissions.manage_webhooks != after.permissions.manage_webhooks:
                embed.add_field(name="Manage Webhooks Before", value=before.permissions.manage_webhooks, inline=False)
                embed.add_field(name="Manage Webhooks After", value=after.permissions.manage_webhooks, inline=False)
            elif before.permissions.manage_emojis != after.permissions.manage_emojis:
                embed.add_field(name="Manage Emojis Before", value=before.permissions.manage_emojis, inline=False)
                embed.add_field(name="Manage Emojis After", value=after.permissions.manage_emojis, inline=False)
            else:
                return
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.managed != after.managed:
            embed.add_field(name="Managed Before", value=before.managed, inline=False)
            embed.add_field(name="Managed After", value=after.managed, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.mentionable != after.mentionable:
            embed.add_field(name="Mentionable Before", value=before.mentionable, inline=False)
            embed.add_field(name="Mentionable After", value=after.mentionable, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.id != after.id:
            embed.add_field(name="ID Before", value=before.id, inline=False)
            embed.add_field(name="ID After", value=after.id, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        else:
            return
    
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        embed = discord.Embed(title="Role Deleted", description=f"Role {role.mention} deleted.", color=0x00ff00)
        embed.add_field(name="Name", value=role.name, inline=False)
        embed.add_field(name="Color", value=role.color, inline=False)
        embed.add_field(name="Hoist", value=role.hoist, inline=False)
        embed.add_field(name="Position", value=role.position, inline=False)
        embed.add_field(name="Permissions", value=role.permissions, inline=False)
        embed.add_field(name="Managed", value=role.managed, inline=False)
        embed.add_field(name="Users", value=len(role.members), inline=False)
        embed.add_field(name="Mentionable", value=role.mentionable, inline=False)
        embed.add_field(name="ID", value=role.id, inline=False)
        logs = self.bot.get_channel(config.log_channel)
        await logs.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        embed = discord.Embed(title="Server Updated", description=f"Server {after.name} updated.", color=0x00ff00)
        if before.name != after.name:
            embed.add_field(name="Name Before", value=before.name, inline=False)
            embed.add_field(name="Name After", value=after.name, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.region != after.region:
            embed.add_field(name="Region Before", value=before.region, inline=False)
            embed.add_field(name="Region After", value=after.region, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.afk_timeout != after.afk_timeout:
            embed.add_field(name="AFK Timeout Before", value=before.afk_timeout, inline=False)
            embed.add_field(name="AFK Timeout After", value=after.afk_timeout, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.afk_channel != after.afk_channel:
            embed.add_field(name="AFK Channel Before", value=before.afk_channel, inline=False)
            embed.add_field(name="AFK Channel After", value=after.afk_channel, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.icon != after.icon:
            embed.add_field(name="Icon Before", value=before.icon, inline=False)
            embed.add_field(name="Icon After", value=after.icon, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.owner != after.owner:
            embed.add_field(name="Owner Before", value=before.owner, inline=False)
            embed.add_field(name="Owner After", value=after.owner, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.splash != after.splash:
            embed.add_field(name="Splash Before", value=before.splash, inline=False)
            embed.add_field(name="Splash After", value=after.splash, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.discovery_splash != after.discovery_splash:
            embed.add_field(name="Discovery Splash Before", value=before.discovery_splash, inline=False)
            embed.add_field(name="Discovery Splash After", value=after.discovery_splash, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.system_channel != after.system_channel:
            embed.add_field(name="System Channel Before", value=before.system_channel, inline=False)
            embed.add_field(name="System Channel After", value=after.system_channel, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.rules_channel != after.rules_channel:
            embed.add_field(name="Rules Channel Before", value=before.rules_channel, inline=False)
            embed.add_field(name="Rules Channel After", value=after.rules_channel, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.public_updates_channel != after.public_updates_channel:
            embed.add_field(name="Public Updates Channel Before", value=before.public_updates_channel, inline=False)
            embed.add_field(name="Public Updates Channel After", value=after.public_updates_channel, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.preferred_locale != after.preferred_locale:
            embed.add_field(name="Preferred Locale Before", value=before.preferred_locale, inline=False)
            embed.add_field(name="Preferred Locale After", value=after.preferred_locale, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.mfa_level != after.mfa_level:
            embed.add_field(name="MFA Level Before", value=before.mfa_level, inline=False)
            embed.add_field(name="MFA Level After", value=after.mfa_level, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.verification_level != after.verification_level:
            embed.add_field(name="Verification Level Before", value=before.verification_level, inline=False)
            embed.add_field(name="Verification Level After", value=after.verification_level, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.explicit_content_filter != after.explicit_content_filter:
            embed.add_field(name="Explicit Content Filter Before", value=before.explicit_content_filter, inline=False)
            embed.add_field(name="Explicit Content Filter After", value=after.explicit_content_filter, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.features != after.features:
            embed.add_field(name="Features Before", value=before.features, inline=False)
            embed.add_field(name="Features After", value=after.features, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.premium_tier != after.premium_tier:
            embed.add_field(name="Premium Tier Before", value=before.premium_tier, inline=False)
            embed.add_field(name="Premium Tier After", value=after.premium_tier, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.premium_subscription_count != after.premium_subscription_count:
            embed.add_field(name="Premium Subscription Count Before", value=before.premium_subscription_count, inline=False)
            embed.add_field(name="Premium Subscription Count After", value=after.premium_subscription_count, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.description != after.description:
            embed.add_field(name="Description Before", value=before.description, inline=False)
            embed.add_field(name="Description After", value=after.description, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.max_presences != after.max_presences:
            embed.add_field(name="Max Presences Before", value=before.max_presences, inline=False)
            embed.add_field(name="Max Presences After", value=after.max_presences, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.max_members != after.max_members:
            embed.add_field(name="Max Members Before", value=before.max_members, inline=False)
            embed.add_field(name="Max Members After", value=after.max_members, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.max_video_channel_users != after.max_video_channel_users:
            embed.add_field(name="Max Video Channel Users Before", value=before.max_video_channel_users, inline=False)
            embed.add_field(name="Max Video Channel Users After", value=after.max_video_channel_users, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        elif before.vanity_url_code != after.vanity_url_code:
            embed.add_field(name="Vanity URL Code Before", value=before.vanity_url_code, inline=False)
            embed.add_field(name="Vanity URL Code After", value=after.vanity_url_code, inline=False)
            logs = self.bot.get_channel(config.log_channel)
            await logs.send(embed=embed)
        else:
            return
        
    
    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        embed = discord.Embed(title="Emoji Updated", description=f"Emoji {after.name} updated.", color=0x00ff00)
        if before.name != after.name:
            embed.add_field(name="Name Before", value=before.name, inline=False)
            embed.add_field(name="Name After", value=after.name, inline=False)
        else:
            embed.add_field(name="Unknown Change", value="Unknown Change", inline=False)
        logs = self.bot.get_channel(config.log_channel)
        await logs.send(embed=embed)
    
##### Member Events #####
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.bot:
            return
        else:
            try:
                if before.nick != after.nick:
                    embed = discord.Embed(title="Member Nickname Updated", color=0x00ff00)
                    embed.add_field(name="Before", value=before.nick, inline=False)
                    embed.add_field(name="After", value=after.nick, inline=False)
                    embed.set_author(name=before.name, icon_url=before.avatar)
                    logs = self.bot.get_channel(config.log_channel)
                    await logs.send(embed=embed)
                elif len(before.roles) < len(after.roles):
                    newRole = next(role for role in after.roles if role not in before.roles)
                    embed = discord.Embed(title=f"Role Added",description=newRole.mention, color=0x00ff00)
                    embed.set_author(name=before.name, icon_url=before.avatar)
                    embed.set_footer(text=f"ID: {before.id}")
                    logs = self.bot.get_channel(config.log_channel)
                    await logs.send(embed=embed)
                elif len(before.roles) > len(after.roles):
                    newRole = next(role for role in before.roles if role not in after.roles)
                    embed = discord.Embed(title=f"Role Removed",description=newRole.mention, color=0x00ff00)
                    embed.set_author(name=before.name, icon_url=before.avatar)
                    embed.set_footer(text=f"ID: {before.id}")
                    logs = self.bot.get_channel(config.log_channel)
                    await logs.send(embed=embed)
            except Exception as e:
                error_channel = self.bot.get_channel(config.error_channel)
                await error_channel.send(f"Error in on_member_update: {e}")
    
    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        if before.bot:
            return
        else:
            try:
                if before.name != after.name:
                    embed = discord.Embed(title="User Updated", color=0x00ff00)
                    embed.add_field(name="Name Before", value=before.name, inline=False)
                    embed.add_field(name="Name After", value=after.name, inline=False)
                    embed.set_author(name=before, icon_url=before.avatar)
                    logs = self.bot.get_channel(config.log_channel)
                    await logs.send(embed=embed)
                elif before.avatar != after.avatar:
                    embed = discord.Embed(title="User Avatar Updated", color=0x00ff00)
                    embed.set_thumbnail(url=after.avatar)
                    embed.set_author(name=before, icon_url=after.avatar)
                    logs = self.bot.get_channel(config.log_channel)
                    await logs.send(embed=embed)
                elif before.discriminator != after.discriminator:
                    embed = discord.Embed(title="User Discriminator Updated", color=0x00ff00)
                    embed.add_field(name="Before", value=before.discriminator, inline=False)
                    embed.add_field(name="After", value=after.discriminator, inline=False)
                    embed.set_author(name=before, icon_url=before.avatar)
                    logs = self.bot.get_channel(config.log_channel)
                    await logs.send(embed=embed)
                else:
                    embed = discord.Embed(title="User Updated", color=0x00ff00)
                    embed.add_field(name="Before", value=before, inline=False)
                    embed.add_field(name="After", value=after, inline=False)
                    embed.set_author(name=before, icon_url=before.avatar)
                    logs = self.bot.get_channel(config.log_channel)
                    await logs.send(embed=embed)
            except Exception as e:
                error_channel = self.bot.get_channel(config.error_channel)
                await error_channel.send(f"Error in on_user_update: {e}")

##### Message Events #####
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        else:
            try:
                if message.content == "":
                    return
                embed = discord.Embed(title="Message Deleted", description=f"Message from {message.author.mention} deleted in {message.channel.mention}.", color=0x00ff00)
                embed.add_field(name="Message", value=message.content, inline=False)
                embed.set_author(name=message.author.name, icon_url=message.author.avatar)
                logs = self.bot.get_channel(config.log_channel)
                await logs.send(embed=embed)
            except Exception as e:
                error_channel = self.bot.get_channel(config.error_channel)
                await error_channel.send(f"Error in on_message_delete: {e}")
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        else:
            try:
                if before.content == after.content:
                    return
                embed = discord.Embed(title="Message Edited", description=f"Message from {before.author.mention} edited in {before.channel.mention}.", color=0x00ff00)
                embed.add_field(name="Before", value=before.content, inline=False)
                embed.add_field(name="After", value=after.content, inline=False)
                embed.set_author(name=before.author.name, icon_url=before.author.avatar)
                logs = self.bot.get_channel(config.log_channel)
                await logs.send(embed=embed)
            except Exception as e:
                error_channel = self.bot.get_channel(config.error_channel)
                await error_channel.send(f"Error in on_message_edit: {e}")
        
    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        if messages.author.bot:
            return
        else:
            try:
                embed = discord.Embed(title="Messages Purged", description=f"{len(messages)} messages purged in {messages[0].channel.mention}.", color=0x00ff00)
                embed.set_author(name=messages[0].author.name, icon_url=messages[0].author.avatar)
                logs = self.bot.get_channel(config.log_channel)
                await logs.send(embed=embed)
            except Exception as e:
                error_channel = self.bot.get_channel(config.error_channel)
                await error_channel.send(f"Error in on_bulk_message_delete: {e}")

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        created_at = invite.created_at.strftime("%Y-%m-%d %H:%M:%S")
        created_at = datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        embed = discord.Embed(title="Invite Created", description=f"Invite {invite.code} created by {invite.inviter.mention}.", color=0x00ff00)
        embed.add_field(name="Channel", value=invite.channel.mention, inline=False)
        embed.add_field(name="Max Uses", value=invite.max_uses, inline=False)
        embed.add_field(name="Temporary", value=invite.temporary, inline=False)
        embed.add_field(name="Created At", value=created_at, inline=False)
        embed.set_author(name=invite.inviter.name, icon_url=invite.inviter.avatar)
        logs = self.bot.get_channel(config.log_channel)
        await logs.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        created_at = invite.created_at.strftime("%Y-%m-%d %H:%M:%S")
        created_at = datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        embed = discord.Embed(title="Invite Deleted", description=f"Invite {invite.code} deleted.", color=0x00ff00)
        embed.set_author(name=invite.inviter.name, icon_url=invite.inviter.avatar)
        embed.add_field(name="Channel", value=invite.channel.mention, inline=False)
        embed.add_field(name="Max Uses", value=invite.max_uses, inline=False)
        embed.add_field(name="Temporary", value=invite.temporary, inline=False)
        embed.add_field(name="Created At", value=created_at, inline=False)
        logs = self.bot.get_channel(config.log_channel)
        await logs.send(embed=embed)

##### Voice Events #####
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        else:
            try:
                if before.channel != after.channel:
                    if before.channel is None:
                        embed = discord.Embed(title="Voice Channel Joined", description=f"Member {member.mention} joined {after.channel.mention}.", color=0x00ff00)
                        embed.set_author(name=member.name, icon_url=member.avatar)
                        logs = self.bot.get_channel(config.log_channel)
                        await logs.send(embed=embed)
                    elif after.channel is None:
                        embed = discord.Embed(title="Voice Channel Left", description=f"Member {member.mention} left {before.channel.mention}.", color=0x00ff00)
                        embed.set_author(name=member.name, icon_url=member.avatar)
                        logs = self.bot.get_channel(config.log_channel)
                        await logs.send(embed=embed)
                    else:
                        embed = discord.Embed(title="Voice Channel Moved", description=f"Member {member.mention} moved from {before.channel.mention} to {after.channel.mention}.", color=0x00ff00)
                        embed.set_author(name=member.name, icon_url=member.avatar)
                        logs = self.bot.get_channel(config.log_channel)
                        await logs.send(embed=embed)
            except Exception as e:
                error_channel = self.bot.get_channel(config.error_channel)
                await error_channel.send(f"Error in on_voice_state_update: {e}")

##### Member Join and Leave #####
    @commands.Cog.listener()

    async def on_member_join(self, member: discord.Member):
        invite_log = 499001163278975006
        logs = self.bot.get_channel(invite_log)
        memberCount = f"{len(member.guild.members)}"
        if memberCount.endswith("1"):
            memberCount = f"{len(member.guild.members)}st"
        elif memberCount.endswith("2"):
            memberCount = f"{len(member.guild.members)}nd"
        elif memberCount.endswith("3"):
            memberCount = f"{len(member.guild.members)}rd"
        else:
            memberCount = f"{len(member.guild.members)}th"
        embed = discord.Embed(title="Member Joined", description=f"Member {member.mention} joined.\nThey are the {memberCount} to join.", color=0x00ff00)
        embed.set_author(name=member.name, icon_url=member.avatar)
        await logs.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        invite_log = 499001163278975006
        joined_at = member.joined_at.strftime("%Y-%m-%d %H:%M:%S")
        joined_at = datetime.datetime.strptime(joined_at, "%Y-%m-%d %H:%M:%S")
        for i in len(member.roles):
            roles = f"{member.roles[i].mention}\n"
        embed = discord.Embed(title="Member Left", description=f"Member {member.mention} left.\nJoined on {joined_at}\n**Roles**\n{roles}", color=0x00ff00)
        embed.set_author(name=member.name, icon_url=member.avatar)
        logs = self.bot.get_channel(invite_log)
        await logs.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        try:
            if message.author == self.bot.user:
                return
            for attachment in message.attachments:
                if attachment.content_type.startswith('image/'):
                    logs_channel = self.bot.get_channel(736794546767396864)
                    await logs_channel.send(f"Attachments:\n{attachment}")
        except Exception as e:
            error_channel = self.bot.get_channel(config.error_channel)
            await error_channel.send(f"Error in on_message: {e}")

async def setup(bot):
    await bot.add_cog(logs(bot))