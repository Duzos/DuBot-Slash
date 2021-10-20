# Importing
import discord
from discord.ext import commands
from discord.ext.commands.converter import _get_from_guilds
from discord_slash import SlashCommand,SlashContext
from discord_slash.utils.manage_commands import create_choice,create_option
import json
import os
import sys

# Setting up the Bot.
intents = discord.Intents.default()
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix="db.", intents=intents, case_insensitive=True)
slash = SlashCommand(bot,sync_commands=True)
bot.remove_command('help')

with open('config.json') as f:
    config = json.load(f)

token = config['token']
guildIDs = config['guildIDs']

# When the bot starts
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("in Python"))
    print(f'{bot.user.name} is ready!')

# The commands

 # Owner commands
@bot.command(name='shutdown',description='Shuts the bot down')
@commands.is_owner()
async def _shutdown(ctx):
    await ctx.send("Bye!")
    await bot.change_presence(status=discord.Status.invisible)
    await bot.close()

@bot.command(name='restart',description='Restarts the bot')
@commands.is_owner()
async def _restart(ctx):
    await ctx.send("See you soon!")
    await bot.change_presence(status=discord.Status.invisible)
    os.execv(sys.executable, ['python'] + sys.argv)

 # Slash commands:
@slash.slash(name='ping',description='Tells you the bots ping')
async def _ping(ctx):
        pingEmbed = discord.Embed(title=f'Ping of {bot.user.name}',description=f':stopwatch:  {round(bot.latency * 1000)}ms',color=discord.Colour.random())
        pingEmbed.set_thumbnail(url=bot.user.avatar_url)
        await ctx.send(embed=pingEmbed)

@slash.slash(name='userinfo',description='Gets information on a user',options=[
    create_option(
        name='user',
        description='Select a user',
        required=True,
        option_type=6
    )
])
async def _userinfo(ctx, user:str):
        rolelist = [r.name for r in user.roles if r != ctx.guild.default_role]
        roles = ", ".join(rolelist)
        date_format = "%a, %d %b %Y %I:%M %p"
        uinfoEmbed = discord.Embed(title=f'Info on {user.name}#{user.discriminator}', description=f'**ID:**\n```{user.id}```\n**Roles:**\n```{roles}```\n**Account Created On:**\n```{user.created_at.strftime(date_format)}```\n**Account Joined Guild On:**\n```{user.joined_at.strftime(date_format)}```\n**Nickname:**\n```{user.nick}```\n**Is Bot:**\n```{user.bot}```',color=discord.Colour.random())
        uinfoEmbed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=uinfoEmbed)

@slash.slash(name='guildinfo',description='Gives you information on the current Guild.')
async def _guildinfo(ctx):
        guild = ctx.guild
        date_format = "%a, %d %b %Y %I:%M %p"

        roleList = ", ".join([str(r.name) for r in guild.roles])

        ginfoEmbed = discord.Embed(title=f'Info on {guild.name}',description=f'**Description:**\n```{guild.description}```\n**Member Count:**\n```{guild.member_count}```\n**Owner:**\n```{guild.owner}```\n**Roles:**\n```{roleList}```\n**Boost Level:**\n```{guild.premium_tier}```\n**Boost Count:**\n```{guild.premium_subscription_count}```\n**ID:**\n```{guild.id}```\n**Guild Created On:**\n```{guild.created_at.strftime(date_format)}```\n**Region:**\n```{guild.region}```',color=discord.Colour.random())
        ginfoEmbed.set_thumbnail(url=guild.icon_url)
        await ctx.send(embed=ginfoEmbed)

@slash.slash(name='roleinfo',description='Gives you information on a role.',options=[
    create_option(
        name='role',
        description='Select a role',
        required=True,
        option_type=8
    )
])
async def _roleinfo(ctx,role:str):
        date_format = "%a, %d %b %Y %I:%M %p"
        memberList = ", ".join([str(m.name) for m in role.members])

        rinfoEmbed = discord.Embed(title=f'Info on {role.name}',description=f'**ID:**\n```{role.id}```\n**Can be Mentioned:**\n```{role.mentionable}```\n**Position:**\n```{role.position}```\n**Role Created On:**\n```{role.created_at.strftime(date_format)}```\n**Colour:**\n```{role.colour}```\n**Members:**\n```{memberList}```',color=role.colour)
        await ctx.send(embed=rinfoEmbed)

@slash.slash(name='channelinfo',description='Gives you information on a channel.',options=[
    create_option(
        name='channel',
        description='Select a channnel',
        required=True,
        option_type=7
    )
])
async def _channelinfo(ctx, channel:str):
        date_format = "%a, %d %b %Y %I:%M %p"

        cinfoEmbed = discord.Embed(title=f'Info on {channel.name}',description=f'**Topic:**\n```{channel.topic}```\n**ID:**\n```{channel.id}```\n**Type:**\n```{channel.type}```\n**Category:**\n```{channel.category}```\n**Channel Created On:**\n```{channel.created_at.strftime(date_format)}```',color=discord.Colour.random())
        await ctx.send(embed=cinfoEmbed)

@slash.slash(name='invite',description='Gives you the bots invite')
async def _invite(ctx):
        inviteEmbed = discord.Embed(title="Invite Link",description="[Bot Invite](https://discord.com/api/oauth2/authorize?client_id=900481597311172660&permissions=0&scope=bot%20applications.commands)",color=discord.Colour.random())
        inviteEmbed.add_field(name='Support Server',value="[Server Invite](https://discord.gg/Raakw6367z)")
        await ctx.send(embed=inviteEmbed)

# Run the bot
bot.run(token)