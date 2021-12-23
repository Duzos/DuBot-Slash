# Importing
import discord
from discord import colour
from discord import guild
from discord.embeds import EmptyEmbed
from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands.converter import _get_from_guilds
from discord.ext.commands.core import has_permissions, is_nsfw
from discord.ext.commands.core import MissingPermissions
from discord.ext.commands.core import BotMissingPermissions
from discord_slash import SlashCommand,SlashContext
from discord_slash.utils.manage_commands import create_choice,create_option
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
from discord_slash import context
import topgg
import json
import os
import sys
import requests
import random
from datetime import datetime
import praw
# Setting up the Bot.
intents = discord.Intents.default()
intents.presences = True
intents.members = True

with open('config.json') as f:
    config = json.load(f)
token = config['token']
guildIDs = config['guildIDs']
ownerID = config['ownerID']
topToken = config['topToken']
redditID = config['redditID']
redditSecret = config['redditSecret']
redditAgent = config['redditAgent']
reddit = praw.Reddit(client_id=redditID,client_secret=redditSecret,user_agent=redditAgent,check_for_async=False)

bot = commands.Bot(command_prefix="db.", intents=intents, case_insensitive=True)
slash = SlashCommand(bot,sync_commands=True)
bot.topgg = topgg.DBLClient(bot=bot,token=topToken)
bot.topgg_webhook = topgg.WebhookManager(bot).dbl_webhook(route='/dblwebhook',auth_key='password')
bot.topgg_webhook.run(5000)
bot.remove_command('help')


# When the bot starts
@bot.event
async def on_ready():
    try:
        await bot.change_presence(status=discord.Status.online, activity=discord.Game(f"in {len(bot.guilds)} servers."))
    except Exception as e:
        owner = bot.get_user(ownerID)
        await owner.send('Failed to update status\n{}:{}'.format(type(e).__name__, e))
    bot.start_time = datetime.utcnow()
    print(f'{bot.user.name} is ready!')

# TopGG Stuff (Remove if you dont have TopGG)
@tasks.loop(minutes=30)
async def update_stats():
    try:
        await bot.topgg.post_guild_count()
    except Exception as e:
        owner = bot.get_user(ownerID)
        await owner.send('Failed to post server count\n{}: {}'.format(type(e).__name__, e))
update_stats.start()

@bot.event
async def on_dbl_test(data):
    user = bot.get_user(int(data['user']))
    print(f"Recieved test vote:\n{data}")
    testEmbed = discord.Embed(title='Test Vote Successful',description=f'Thank you for voting {user.mention}',color=discord.Colour.random())
    testEmbed.add_field(name='Raw Data',value=data)
    testEmbed.set_thumbnail(url="https://clipart.info/images/ccovers/1518056315Dark-Red-Heart-Transparent-Background.png")
    await user.send(embed=testEmbed)

@bot.event
async def on_dbl_vote(data):
    if data['type'] == 'test':
        return bot.dispatch('dbl_test',data)
    user = bot.get_user(int(data['user']))
    voteEmbed = discord.Embed(title=f'Thank you for voting for {bot.user.name}!',description=f'Thank you for voting {user.mention}',color=discord.Colour.random())
    voteEmbed.set_thumbnail(url="https://clipart.info/images/ccovers/1518056315Dark-Red-Heart-Transparent-Background.png")
    await user.send(embed=voteEmbed)

# Guild amount status
@bot.event
async def on_guild_join():
    try:
        await bot.change_presence(status=discord.Status.online, activity=discord.Game(f"in {len(bot.guilds)} servers."))
    except Exception as e:
        owner = bot.get_user(ownerID)
        await owner.send('Failed to update status\n{}:{}'.format(type(e).__name__, e))

@bot.event
async def on_guild_remove():
    try:
        await bot.change_presence(status=discord.Status.online, activity=discord.Game(f"in {len(bot.guilds)} servers."))
    except Exception as e:
        owner = bot.get_user(ownerID)
        await owner.send('Failed to update status\n{}:{}'.format(type(e).__name__, e))

# Leave and Welcome messages
@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild

    with open('json/data.json','r') as f:
        jsonData = json.load(f)

    guildID = str(guild.id)
    try:
        choice = jsonData[f"{guildID} welcome"]
    except:
        return
    if choice == "False":
        return
    elif choice == "True":
        welcomeEmbed = discord.Embed(title='New Member', description=f'{member.mention} joined',color=discord.Colour.random())
        welcomeEmbed.set_thumbnail(url=member.avatar_url)
        welcomeEmbed.set_author(
            name=bot.user.display_name,
            icon_url=bot.user.avatar_url
        )
        await bot.get_channel(jsonData[f"{guildID} welcomeChannel"]).send(embed=welcomeEmbed)
        return
    
@bot.event
async def on_member_remove(member: discord.Member):
    guild = member.guild

    with open('json/data.json','r') as f:
        jsonData = json.load(f)

    guildID = str(guild.id)
    try:
        choice = jsonData[f"{guildID} leave"]
    except:
        return
    if choice == "False":
        return
    elif choice == "True":
        leaveEmbed = discord.Embed(title='Member Left', description=f'{member.mention} left',color=discord.Colour.random())
        leaveEmbed.set_thumbnail(url=member.avatar_url)
        leaveEmbed.set_author(
            name=bot.user.display_name,
            icon_url=bot.user.avatar_url
        )
        await bot.get_channel(jsonData[f"{guildID} leaveChannel"]).send(embed=leaveEmbed)
        return
    

# Handling Errors.
@bot.event
async def on_slash_command_error(ctx, error):
    errorEmbed = discord.Embed(title='ERROR',description=error,color=0x992D22)
    await ctx.send(embed=errorEmbed)


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
    await bot.change_presence(activity=discord.Game("Restarting."))
    os.execv(sys.executable, ['python'] + sys.argv)

 # Slash commands:

  # Moderation Category:

@slash.slash(name='toggle_tickets',description='Turn tickets on or off.',options=[
    create_option(
        name='choice',
        description='Whether you want it on or off.',
        required=True,
        option_type=3,
        choices=[
            create_choice(
                name='Off',
                value="False"
            ),
            create_choice(
                name='On',
                value="True"
            )
        ]
    )
])
@has_permissions(manage_channels=True)
async def _toggletickets(ctx, choice: str=None):
    with open('json/data.json','r') as f:
        jsonData = json.load(f)

    guildID = str(ctx.guild.id)

    if choice == "True":
        choice = True
        jsonData[f'{guildID} tickets'] = choice
        await ctx.reply("Tickets are now on.")
    elif choice == "False":
        choice = False
        jsonData[f'{guildID} tickets'] = choice
        await ctx.reply("Tickets are now off.")
    
    with open('json/data.json','w') as f:
        json.dump(jsonData, f, indent=4)

@slash.slash(name='create_ticket',description='Creates a support ticket if enabled.',options=[
    create_option(
        name='reason',
        description='What you need help with',
        required=False,
        option_type=3
    )
])
async def _createticket(ctx, reason: str=None):
    guildID = str(ctx.guild.id)
    guild = ctx.guild

    with open('json/data.json','r') as f:
        jsonData = json.load(f)
    
    if jsonData[f'{guildID} tickets'] == False:
        return await ctx.reply("Tickets are turned off.")
    
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        ctx.author: discord.PermissionOverwrite(read_messages=True)
    }
    try:
        channel = await guild.create_text_channel(f'ticket-{ctx.author}', overwrites=overwrites,reason='Ticket System.')
    except discord.Forbidden:
        permsEmbed = discord.Embed(title='ERROR',description=f'{bot.user.name} is missing the required permission(s) to run this command.',color=discord.Colour.red())
        permsEmbed.set_thumbnail(bot.user.avatar_url)
        return await ctx.reply(embed=permsEmbed)

    try:
        message = await channel.send(ctx.author.mention)
        await message.delete()
    except discord.Forbidden:
        pass

    embed = discord.Embed(title='Ticket',description=f'Created by {ctx.author.mention}',color=discord.Colour.random())
    embed.add_field(name='Reason:',value=reason)
    buttons = [
        manage_components.create_button(
            style=ButtonStyle.danger,
            label='Lock Ticket',
            custom_id='lock_button'
        )
    ]   
    action_row= manage_components.create_actionrow(*buttons)

    await channel.send(embed=embed, components=[action_row])
    await ctx.reply("Ticket Created.")

    button_ctx: context.ComponentContext = await manage_components.wait_for_component(bot, components=action_row)
    buttons = [
        manage_components.create_button(
            style=ButtonStyle.danger,
            label='Lock Ticket',
            custom_id='lock_button',
            disabled=True
        )
    ]   
    action_row= manage_components.create_actionrow(*buttons)
    await button_ctx.edit_origin(embed=embed, components=[action_row])
    

    try:
        await channel.set_permissions(ctx.author,reason='Ticket System',read_messages=False)
    except discord.Forbidden:
        permsEmbed = discord.Embed(title='ERROR',description=f'{bot.user.name} is missing the required permission(s) to run this command.',color=discord.Colour.red())
        permsEmbed.set_thumbnail(bot.user.avatar_url)
        return await ctx.reply(embed=permsEmbed)

    await channel.send("Ticket Locked.")


@slash.slash(name='kick',description='Kicks a user.',options=[
    create_option(
        name='user',
        description='The user you want to kick',
        required=True,
        option_type=6
    ),
    create_option(
        name='reason',
        description='The reason for the kick.',
        required=False,
        option_type=3
    )
])
@has_permissions(kick_members=True)
async def _kick(ctx, user: str, reason: str=None):
    try:
        await user.kick(reason=reason)
    except discord.Forbidden:
        botPermEmbed = discord.Embed(title='ERROR',description=f'{bot.user.name} is missing the required permission(s) to run this command.',color=0x992D22)
        botPermEmbed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url
        )
        botPermEmbed.set_thumbnail(url=bot.user.avatar_url)
        try:
            await ctx.reply(embed=botPermEmbed)
        except:
            await ctx.send(embed=botPermEmbed)
        return
    kickEmbed = discord.Embed(title='Kick',description=f'{user.mention} has been kicked.',color=discord.Colour.random())
    kickEmbed.set_thumbnail(url=user.avatar_url)
    kickEmbed.add_field(name='Reason:',value=reason)
    await ctx.send(embed=kickEmbed)
    kickEmbed = discord.Embed(title='Kick',description=f'{user.mention} has been kicked.',color=discord.Colour.random())
    kickEmbed.set_thumbnail(url=ctx.guild.icon_url)
    kickEmbed.add_field(name='Reason:',value=reason)
    kickEmbed.add_field(name='Server:',value=ctx.guild.name)
    await user.send(embed=kickEmbed)

@slash.slash(name='lockchannel',description='Locks the channel',options=[
    create_option(
        name='channel',
        description='Specify a channel (leave blank for current)',
        required=False,
        option_type=7
    )
])
@has_permissions(manage_channels=True)
async def _lockchannel(ctx, channel: str=None):
    channel = channel or ctx.channel
    overwrite=channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    try:
        await channel.set_permissions(ctx.guild.default_role,overwrite=overwrite)
    except discord.Forbidden:
        botPermEmbed = discord.Embed(title='ERROR',description=f'{bot.user.name} is missing the required permission(s) to run this command.',color=0x992D22)
        botPermEmbed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url
        )
        botPermEmbed.set_thumbnail(url=bot.user.avatar_url)
        try:
            await ctx.reply(embed=botPermEmbed)
        except:
            await ctx.send(embed=botPermEmbed)
        return
    await ctx.send("Channel locked. :lock:")

@slash.slash(name='unlockchannel',description='Unlocks the channel',options=[
    create_option(
        name='channel',
        description='Specify a channel (leave blank for current)',
        required=False,
        option_type=7
    )
])
@has_permissions(manage_channels=True)
async def _unlockchannel(ctx, channel: str=None):
    channel = channel or ctx.channel
    overwrite=channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    try:
        await channel.set_permissions(ctx.guild.default_role,overwrite=overwrite)
    except discord.Forbidden:
        botPermEmbed = discord.Embed(title='ERROR',description=f'{bot.user.name} is missing the required permission(s) to run this command.',color=0x992D22)
        botPermEmbed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url
        )
        botPermEmbed.set_thumbnail(url=bot.user.avatar_url)
        try:
            await ctx.reply(embed=botPermEmbed)
        except:
            await ctx.send(embed=botPermEmbed)
        return
    await ctx.send("Channel unlocked. :unlock:")
    
@slash.slash(name='mute',description='Mutes a user',options=[
    create_option(
        name='user',
        description='The user you want to mute',
        required=True,
        option_type=6
    ),
    create_option(
        name='reason',
        description='The reason for the mute.',
        required=False,
        option_type=3
    )
])
@has_permissions(manage_roles=True)
async def _mute(ctx,user: str, reason: str=None):
    guild = ctx.guild
    roles = await guild.fetch_roles()
    channels = await guild.fetch_channels()

    for discord.Role in roles:
        if discord.Role.name.upper() == "MUTED":
            try:
                await user.add_roles(discord.Role)
            except discord.Forbidden:
                botPermEmbed = discord.Embed(title='ERROR',description=f'{bot.user.name} is missing the required permission(s) to run this command.',color=0x992D22)
                botPermEmbed.set_author(
                    name=ctx.message.author.name,
                    icon_url=ctx.message.author.avatar_url
                )
                botPermEmbed.set_thumbnail(url=bot.user.avatar_url)
                try:
                    await ctx.reply(embed=botPermEmbed)
                except:
                    await ctx.send(embed=botPermEmbed)
                return
            muteEmbed = discord.Embed(title='Mute',description=f'Muted {user.mention}.',color=discord.Colour.random())
            muteEmbed.set_thumbnail(url=user.avatar_url)
            muteEmbed.add_field(name='Reason:',value=reason)
            await ctx.send(embed=muteEmbed)
            muteEmbed = discord.Embed(title='Mute',description=f'Muted {user.mention}.',color=discord.Colour.random())
            muteEmbed.set_thumbnail(url=ctx.guild.icon_url)
            muteEmbed.add_field(name='Reason:',value=reason)
            muteEmbed.add_field(name='Server:',value=ctx.guild.name)
            await user.send(embed=muteEmbed)
            return
        
    msg = await ctx.send("Please wait while I setup a muted role.")
    permissions = discord.Permissions(permissions=0,send_message=False,speak=False)
    try:
        role =  await guild.create_role(name='Muted',reason='Muted role was not found, so I made one.',permissions=permissions)
    except discord.Forbidden:
        botPermEmbed = discord.Embed(title='ERROR',description=f'{bot.user.name} is missing the required permission(s) to run this command.',color=0x992D22)
        botPermEmbed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url
        )
        botPermEmbed.set_thumbnail(url=bot.user.avatar_url)
        try:
            await ctx.reply(embed=botPermEmbed)
        except:
            await ctx.send(embed=botPermEmbed)
        return
    for discord.TextChannel in channels:
        await discord.TextChannel.set_permissions(role,send_message=False)
    for discord.VoiceChannel in channels:
        await discord.VoiceChannel.set_permissiosn(role,speak=False)
    try:
        await user.add_roles(role)
    except discord.Forbidden:
        botPermEmbed = discord.Embed(title='ERROR',description=f'{bot.user.name} is missing the required permission(s) to run this command.',color=0x992D22)
        botPermEmbed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url
        )
        botPermEmbed.set_thumbnail(url=bot.user.avatar_url)
        try:
            await ctx.reply(embed=botPermEmbed)
        except:
            await ctx.send(embed=botPermEmbed)
        return
    muteEmbed = discord.Embed(title='Mute',description=f'Muted {user.mention}.',color=discord.Colour.random())
    muteEmbed.set_thumbnail(url=user.avatar_url)
    muteEmbed.add_field(name='Reason:',value=reason)
    await msg.edit(embed=muteEmbed)
    muteEmbed = discord.Embed(title='Mute',description=f'Muted {user.mention}.',color=discord.Colour.random())
    muteEmbed.set_thumbnail(url=ctx.guild.icon_url)
    muteEmbed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url
        )
    muteEmbed.add_field(name='Reason:',value=reason)
    muteEmbed.add_field(name='Server:',value=ctx.guild.name)
    await user.send(embed=muteEmbed)

@slash.slash(name='unmute',description='Unmutes a user',options=[
    create_option(
        name='user',
        description='The user you want to unmute',
        required=True,
        option_type=6
    )
])
@has_permissions(manage_roles=True)
async def _unmute(ctx, user: str):
    roles = user.roles

    for discord.Role in roles:
        if discord.Role.name.upper() == "MUTED":
            try:
                await user.remove_roles(discord.Role,reason="Unmuting the user.")
            except discord.Forbidden:
                botPermEmbed = discord.Embed(title='ERROR',description=f'{bot.user.name} is missing the required permission(s) to run this command.',color=0x992D22)
                botPermEmbed.set_author(
                    name=ctx.message.author.name,
                    icon_url=ctx.message.author.avatar_url
                )
                botPermEmbed.set_thumbnail(url=bot.user.avatar_url)
                try:
                    await ctx.reply(embed=botPermEmbed)
                except:
                    await ctx.send(embed=botPermEmbed)
                return
            unmuteEmbed = discord.Embed(title='Unmute',description=f'Unmuted {user.mention}',color=discord.Colour.random())
            unmuteEmbed.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=unmuteEmbed)
            unmuteEmbed = discord.Embed(title='Unmute',description=f'Unmuted {user.mention}',color=discord.Colour.random())
            unmuteEmbed.set_thumbnail(url=ctx.guild.icon_url)
            unmuteEmbed.add_field(name='Server:',value=ctx.guild.name)
            await user.send(embed=unmuteEmbed)
            return

    await ctx.send(f"{user.mention} is not muted!")

@slash.slash(name='ban',description='Bans a user.',options=[
    create_option(
        name='user',
        description='The user you want to ban',
        required=True,
        option_type=6
    ),
    create_option(
        name='reason',
        description='The reason for the ban.',
        required=False,
        option_type=3
    )
])
@has_permissions(ban_members=True)
async def _ban(ctx, user: str, reason: str=None):
    try:
        await user.ban(reason=reason)
    except discord.Forbidden:
        botPermEmbed = discord.Embed(title='ERROR',description=f'{bot.user.name} is missing the required permission(s) to run this command.',color=0x992D22)
        botPermEmbed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url
        )
        botPermEmbed.set_thumbnail(url=bot.user.avatar_url)
        try:
            await ctx.reply(embed=botPermEmbed)
        except:
            await ctx.send(embed=botPermEmbed)
        return

    banEmbed = discord.Embed(title='Ban',description=f'{user.mention} has been banned.', color=discord.Colour.random())
    banEmbed.set_thumbnail(url=user.avatar_url)
    banEmbed.add_field(name='Reason:',value=reason)
    await ctx.send(embed=banEmbed)
    banEmbed = discord.Embed(title='Ban',description=f'{user.mention} has been banned.', color=discord.Colour.random())
    banEmbed.set_thumbnail(url=ctx.guild.icon_url)
    banEmbed.add_field(name='Reason:',value=reason)
    banEmbed.add_field(name='Server:',value=ctx.guild.name)
    await user.send(embed=banEmbed)

@slash.slash(name='slowmode',description='Adds slowmode to a channel',options=[
    create_option(
        name='seconds',
        description='The length of the slowmode (Limit is 21600)',
        required=True,
        option_type=4
    )
])
@has_permissions(manage_channels=True)
async def _slowmode(ctx, seconds: int):
    try:
        await ctx.channel.edit(slowmode_delay=seconds)
    except discord.Forbidden:
        botPermEmbed = discord.Embed(title='ERROR',description=f'{bot.user.name} is missing the required permission(s) to run this command.',color=0x992D22)
        botPermEmbed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url
        )
        botPermEmbed.set_thumbnail(url=bot.user.avatar_url)
        try:
            await ctx.reply(embed=botPermEmbed)
        except:
            await ctx.send(embed=botPermEmbed)
        return
    slowEmbed = discord.Embed(title='Slowmode',description=f'Slowmode is now on **{seconds}** seconds.',color=discord.Colour.random())
    slowEmbed.set_thumbnail(url=bot.user.avatar_url)
    await ctx.send(embed=slowEmbed)

@slash.slash(name='clear',description='Clears a certain amount of messages',options=[
    create_option(
        name='amount',
        description='The amount of messages you want deleted',
        required=True,
        option_type=4
    )
])
@has_permissions(manage_messages=True)
async def _clear(ctx, amount: int):
    try:
        await ctx.channel.purge(limit=amount)
    except discord.Forbidden:
        botPermEmbed = discord.Embed(title='ERROR',description=f'{bot.user.name} is missing the required permission(s) to run this command.',color=0x992D22)
        botPermEmbed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url
        )
        botPermEmbed.set_thumbnail(url=bot.user.avatar_url)
        try:
            await ctx.reply(embed=botPermEmbed)
        except:
            await ctx.send(embed=botPermEmbed)
        return
    msg = await ctx.send("Clear complete.")
    await msg.delete()
  # Information Category:

@slash.slash(name='information',description='Tells you information on the bot.')
async def _info(ctx):
    embed = discord.Embed(title='discord.py | discord-interactions | python',description='by <@!327807253052653569>\n[Github Page](https://github.com/Duzos/DuBot-Slash)\n[Support Server](https://discord.gg/Raakw6367z)',color=discord.Colour.random())
    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/768px-Python-logo-notext.svg.png")
    await ctx.reply(embed=embed)

@slash.slash(name='uptime',description='Tells you how long the bot has been online.')
async def _uptime(ctx):
    delta_uptime = datetime.utcnow() - bot.start_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    uptimeEmbed = discord.Embed(title='Uptime',description=f"{days}d, {hours}h, {minutes}m, {seconds}s",color=discord.Color.random())
    uptimeEmbed.set_thumbnail(url=bot.user.avatar_url)
    await ctx.send(embed=uptimeEmbed)

@slash.slash(name='bitcoin',description='Tells you the current value of Bitcoin.',options=[
    create_option(
        name='amount',
        description='The amount of bitcoin.',
        required=False,
        option_type=4
    )
])
async def _bitcoin(ctx,amount: int=1):
        response_API = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
        data = response_API.text
        parse_json = json.loads(data)
        bitcoinGBP = parse_json['bpi']['GBP']['rate_float']
        bitcoinUSD = parse_json['bpi']['USD']['rate_float']
        bitcoinEUR = parse_json['bpi']['EUR']['rate_float']


        bitcoinEmbed = discord.Embed(title=f'Price of {amount} bitcoin',color=discord.Colour.gold())
        bitcoinEmbed.add_field(name='(€)EUR',value=round(bitcoinEUR * amount),inline=True)
        bitcoinEmbed.add_field(name='(£)GBP',value=round(bitcoinGBP*amount),inline=True)
        bitcoinEmbed.add_field(name='($)USD',value=round(bitcoinUSD*amount),inline=True)
        bitcoinEmbed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/64px-Bitcoin.svg.png")
        await ctx.send(embed=bitcoinEmbed)

@slash.slash(name='ping',description='Tells you the bots ping')
async def _ping(ctx):
        pingEmbed = discord.Embed(title=f'Ping of {bot.user.name}',description=f':stopwatch:  {round(bot.latency * 1000)}ms',color=discord.Colour.random())
        pingEmbed.set_thumbnail(url=bot.user.avatar_url)
        await ctx.send(embed=pingEmbed)

@slash.slash(name='avatar',description='Sends the avatar of a user',options=[
    create_option(
        name='user',
        description='Select a user',
        required=True,
        option_type=6
    )
])
async def _avatar(ctx, user: str):
    avatarembed = discord.Embed(description=f'Avatar of {user.mention}',color=discord.Colour.random(),type='image')
    avatarembed.set_image(url=user.avatar_url)
    await ctx.send(embed=avatarembed)

@slash.slash(name='user_info',description='Gets information on a user',options=[
    create_option(
        name='user',
        description='Select a user',
        required=True,
        option_type=6
    )
])
async def _userinfo(ctx, user:str):
        rolelist = [r.name for r in user.roles if r != ctx.guild.default_role]
        permissionList = ', '.join([perm[0] for perm in user.guild_permissions if perm[1]])
        roles = ", ".join(rolelist)
        if roles == "":
            roles=None
        date_format = "%a, %d %b %Y %I:%M %p"
        uinfoEmbed = discord.Embed(title=f'Info on {user.name}#{user.discriminator}', description=f'**ID:**\n```{user.id}```\n**Roles:**\n```{roles}```\n**Account Created On:**\n```{user.created_at.strftime(date_format)}```\n**Account Joined Guild On:**\n```{user.joined_at.strftime(date_format)}```\n**Nickname:**\n```{user.nick}```\n**Is Bot:**\n```{user.bot}```\n**Permissions:**\n```{permissionList}```',color=discord.Colour.random())
        uinfoEmbed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=uinfoEmbed)

@slash.slash(name='guild_info',description='Gives you information on the current Guild.')
async def _guildinfo(ctx):
        guild = ctx.guild
        date_format = "%a, %d %b %Y %I:%M %p"

        roleList = ", ".join([str(r.name) for r in guild.roles])

        ginfoEmbed = discord.Embed(title=f'Info on {guild.name}',description=f'**Description:**\n```{guild.description}```\n**Member Count:**\n```{guild.member_count}```\n**Owner:**\n```{guild.owner}```\n**Roles:**\n```{roleList}```\n**Boost Level:**\n```{guild.premium_tier}```\n**Boost Count:**\n```{guild.premium_subscription_count}```\n**ID:**\n```{guild.id}```\n**Guild Created On:**\n```{guild.created_at.strftime(date_format)}```\n**Region:**\n```{guild.region}```',color=discord.Colour.random())
        ginfoEmbed.set_thumbnail(url=guild.icon_url)
        await ctx.send(embed=ginfoEmbed)

@slash.slash(name='role_info',description='Gives you information on a role.',options=[
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
        permissionList = ', '.join([perm[0] for perm in role.permissions if perm[1]])

        rinfoEmbed = discord.Embed(title=f'Info on {role.name}',description=f'**ID:**\n```{role.id}```\n**Can be Mentioned:**\n```{role.mentionable}```\n**Position:**\n```{role.position}```\n**Role Created On:**\n```{role.created_at.strftime(date_format)}```\n**Colour:**\n```{role.colour}```\n**Permissions:**\n```{permissionList}```\n**Members:**\n```{memberList}```',color=role.colour)
        await ctx.send(embed=rinfoEmbed)

@slash.slash(name='channel_info',description='Gives you information on a channel.',options=[
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
        inviteEmbed.add_field(name='Support Server',value="[Server Invite](https://discord.gg/Raakw6367z)",inline=False)
        inviteEmbed.add_field(name='Get Dubot!',value="[Dubot Invite](https://discord.com/api/oauth2/authorize?client_id=865190020179296267&permissions=0&scope=bot%20applications.commands)",inline=False)
        await ctx.send(embed=inviteEmbed)

  # Fun category

@slash.slash(name='randomreddit',description='Gets posts from a random subreddit.')
async def _randomreddit(ctx):
    sb_random = reddit.random_subreddit()
    sb_submissions=sb_random.hot()
    post_to_pick = random.randint(1,20)
    for i in range(0,post_to_pick):
        submission = next(x for x in sb_submissions if not x.stickied)


    sb_extension = submission.url[len(submission.url) - 3 :].lower()
    if sb_extension == "jpg" or sb_extension == "png" or sb_extension == "gif":
        sbEmbed = discord.Embed(title=sb_random.display_name,description=f'[{submission.title}]({submission.url})',color=discord.Colour.random(),type='image')
        sbEmbed.set_image(url=submission.url)
        await ctx.send(embed=sbEmbed)
        return
    sbEmbed = discord.Embed(title=sb_random.display_name,description=f'[{submission.title}]({submission.url})',color=discord.Colour.random())
    await ctx.send(embed=sbEmbed)

@slash.slash(name='subreddit',description='Get posts from a subreddit.',options=[
    create_option(
        name='subreddit',
        description='The subreddit you want found.',
        required=True,
        option_type=3
    )
])
async def _subreddit(ctx, subreddit):
    sb_submissions = reddit.subreddit(subreddit).hot()
    post_to_pick = random.randint(1,20)
    for i in range(0,post_to_pick):
        submission = next(x for x in sb_submissions if not x.stickied)

    sb_extension = submission.url[len(submission.url) - 3 :].lower()
    if sb_extension == "jpg" or sb_extension == "png" or sb_extension == "gif":
        sbEmbed = discord.Embed(title=subreddit,description=f'[{submission.title}]({submission.url})',color=discord.Colour.random(),type='image')
        sbEmbed.set_image(url=submission.url)
        await ctx.send(embed=sbEmbed)
        return
    sbEmbed = discord.Embed(title=subreddit,description=f'[{submission.title}]({submission.url})',color=discord.Colour.random())
    await ctx.send(embed=sbEmbed)

@slash.slash(name='meme',description='Sends a random meme.')
async def _meme(ctx):
    memes_submissions = reddit.subreddit('memes').hot()
    post_to_pick = random.randint(1, 10)
    for i in range(0, post_to_pick):
        submission = next(x for x in memes_submissions if not x.stickied)

    memeEmbed = discord.Embed(title='Meme',color=discord.Colour.random(),type='image')
    memeEmbed.set_image(url=submission.url)
    memeEmbed.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=memeEmbed)

@slash.slash(name='random_name',description='Gives you a random name.')
async def _randomname(ctx):

        r = requests.get('http://api.randomuser.me/?format=json&?nat=gb')
        results = json.loads(r.text)
        results = results['results'][0]
        name=results['name']
        picture=results['picture']
        dob=results['dob']

        nameTitle=name['title']
        firstName=name['first']
        lastName=name['last']
        nameThumbnail=picture['large']
        nameAge=dob['age']
        nameDate=dob['date'][0:][:10]

        nameEmbed = discord.Embed(title='Random Person',color=discord.Colour.random(),type='image')
        nameEmbed.set_image(url=nameThumbnail)
        nameEmbed.add_field(name='Name',value=f"{nameTitle} {firstName} {lastName}",inline=False)
        nameEmbed.add_field(name='Age',value=f'{nameAge}\n{nameDate}')
        nameEmbed.add_field(name='Gender',value=results['gender'])
        await ctx.send(embed=nameEmbed)
    
@slash.slash(name='fact',description='Gives you a random fact.')
async def _fact(ctx):
        responseAPI = requests.get("https://uselessfacts.jsph.pl/random.json?language=en").json()   
        factID = responseAPI["id"]
        factResponse = responseAPI["text"]
        factLink = responseAPI["permalink"]

        factEmbed = discord.Embed(title='Fact',description=f'{factResponse}',color=discord.Colour.random())
        factEmbed.set_footer(text=f"ID: {factID}")
        factEmbed.add_field(name='Link',value=f'[Click!]({factLink})')      
        await ctx.send(embed=factEmbed)

@slash.slash(name='cat',description='Gives you a random cat picture.')
async def _cat(ctx):
        for i in requests.get("https://api.thecatapi.com/v1/images/search").json():
            catURL = i["url"]
            catID = i["id"]

        catEmbed = discord.Embed(title='Cat',color=discord.Colour.random(),type='image')
        catEmbed.set_image(url=catURL)
        catEmbed.set_footer(text=f'ID: {catID}',icon_url=EmptyEmbed)
        await ctx.send(embed=catEmbed)

@slash.slash(name='activity',description='Gives you a random activity.')
async def _activity(ctx):
        response_API = requests.get("https://www.boredapi.com/api/activity/")
        data = response_API.text
        parse_json = json.loads(data)
        activityCurrent = parse_json['activity']
        activityType = parse_json['type']
        activityKey = parse_json['key']
        activityPeople = parse_json['participants']

        activityEmbed = discord.Embed(title='Activity',color=discord.Colour.random())
        activityEmbed.add_field(name='Activity:',value=activityCurrent,inline=False)
        activityEmbed.add_field(name='Type:',value=activityType,inline=False)
        activityEmbed.add_field(name='Number of People:',value=activityPeople,inline=False)
        activityEmbed.set_footer(text=f"ID: {activityKey}",icon_url=EmptyEmbed)
        activityEmbed.set_thumbnail(url=bot.user.avatar_url)
        await ctx.send(embed=activityEmbed)   

@slash.slash(name='advice',description='Gives you advice')
async def _advice(ctx):
        response_API = requests.get("https://api.adviceslip.com/advice")
        data = response_API.text
        parse_json = json.loads(data)
        currentAdvice = parse_json['slip']['advice']
        currentAdviceID = parse_json['slip']['id']

        adviceEmbed = discord.Embed(title='Advice',description=currentAdvice,color=discord.Colour.random())
        adviceEmbed.set_footer(text=f"ID: {currentAdviceID}",icon_url=EmptyEmbed)
        adviceEmbed.set_thumbnail(url=bot.user.avatar_url)
        await ctx.send(embed=adviceEmbed)

@slash.slash(name='e',description='e',options=[
    create_option(
        name='amount',
        description='Amount of E',
        required=False,
        option_type=4
    )
])
async def _e(ctx,amount: int=None):
        eList = ""
        if amount != None:
            amount = int(amount)
        if amount == None:
            amount = random.randint(1,100)
        elif amount > 2000:
            amount = 2000
            await ctx.send("Limit is 2000.")

        while 0 < amount:
            eList = eList + "e"
            amount = amount - 1
        await ctx.send(eList)

@slash.slash(name='say',description='Repeats what you say.',options=[
    create_option(
        name='message',
        description='The thing you want repeated.',
        required=True,
        option_type=3
    )
])
async def _say(ctx,message: str):
    if "@everyone" in message or "@here" in message:
        await ctx.send("You cannot have `@everyone` or `@here` in your message!")
        return
    await ctx.send(message)

@slash.slash(name='reverse',description='Reverses what you say.',options=[
    create_option(
        name='message',
        description='The thing you want reversed.',
        required=True,
        option_type=3
    )
])
async def _reverse(ctx, message: str):
    await ctx.send(message[::-1])

@slash.slash(name='coin',description='Flips a coin.')
async def _coin(ctx):
        coin = ['Heads', 'Tails']
        result = random.choice(coin)
        
        flipEmbed = discord.Embed(title=':coin:',description=f'The coin landed on **{result}**.',color=discord.Colour.random())
        flipEmbed.set_thumbnail(url=bot.user.avatar_url)
        await ctx.send(embed=flipEmbed)

@slash.slash(name='roll',description='Rolls a dice.',options=[
    create_option(
        name='lowest',
        description='The lowest number.',
        required=False,
        option_type=4
    ),
    create_option(
        name='highest',
        description="The highest number.",
        required=False,
        option_type=4
    )
])
async def _roll(ctx,lowest: int=1,highest: int=6):
    diceResult = random.randint(lowest,highest)
    diceEmbed = discord.Embed(title=":game_die:",description=f'The dice rolled a **{diceResult}**.',color=discord.Colour.random())
    diceEmbed.set_thumbnail(url=bot.user.avatar_url)
    await ctx.send(embed=diceEmbed)

@slash.slash(name='rps',description='Rock, Paper, Scissors!',options=[
    create_option(
        name='player',
        description='Rock, Paper or Scissors.',
        required=True,
        option_type=3,
        choices=[
            create_choice(
                name='rock',
                value='rock'
            ),
            create_choice(
                name='paper',
                value='paper'
            ),
            create_choice(
                name='scissors',
                value='scissors'
            )
        ]
    )
])
async def _rps(ctx,player: str):
        choices = ["rock", "paper", "scissors"]
        computers_answer = random.choice(choices)

        if computers_answer == player:
            resultEmbed = discord.Embed(title='Tie.',description=f'You both picked {player}.',color=discord.Colour.random())
            resultEmbed.set_thumbnail(url=bot.user.avatar_url)
            await ctx.send(embed=resultEmbed)
            return
        elif computers_answer == "rock":
            if player == "paper":
                resultEmbed = discord.Embed(title='You win!',description=f'Your opponent picked {computers_answer}.',color=discord.Colour.random())
                resultEmbed.set_thumbnail(url=bot.user.avatar_url)
                await ctx.send(embed=resultEmbed)
                return
            if player == "scissors":
                resultEmbed = discord.Embed(title='You lose.',description=f'Your opponent picked {computers_answer}.',color=discord.Colour.random())
                resultEmbed.set_thumbnail(url=bot.user.avatar_url)
                await ctx.send(embed=resultEmbed)
                return
        elif computers_answer == "paper":
            if player == "scissors":
                resultEmbed = discord.Embed(title='You win!',description=f'Your opponent picked {computers_answer}.',color=discord.Colour.random())
                resultEmbed.set_thumbnail(url=bot.user.avatar_url)
                await ctx.send(embed=resultEmbed)
                return
            if player == "rock":
                resultEmbed = discord.Embed(title='You lose.',description=f'Your opponent picked {computers_answer}.',color=discord.Colour.random())
                resultEmbed.set_thumbnail(url=bot.user.avatar_url)
                await ctx.send(embed=resultEmbed)
                return
        elif computers_answer == "scissors":
            if player == "rock":
                resultEmbed = discord.Embed(title='You win!',description=f'Your opponent picked {computers_answer}.',color=discord.Colour.random())
                resultEmbed.set_thumbnail(url=bot.user.avatar_url)
                await ctx.send(embed=resultEmbed)
                return
            if player == "paper":
                resultEmbed = discord.Embed(title='You lose.',description=f'Your opponent picked {computers_answer}.',color=discord.Colour.random())
                resultEmbed.set_thumbnail(url=bot.user.avatar_url)
                await ctx.send(embed=resultEmbed)
                return
        else:
            return

@slash.slash(name='number_guess',description='Guess a number from 1-10',options=[
    create_option(
        name='guess',
        description='Your guess',
        required=True,
        option_type=4,
        choices=[
            create_choice(
                name='1',
                value=1
            ),
            create_choice(
                name='2',
                value=2
            ),
            create_choice(
                name='3',
                value=3
            ),
            create_choice(
                name='4',
                value=4
            ),
            create_choice(
                name='5',
                value=5
            ),
            create_choice(
                name='6',
                value=6
            ),
            create_choice(
                name='7',
                value=7
            ),
            create_choice(
                name='8',
                value=8
            ),
            create_choice(
                name='9',
                value=9
            ),
            create_choice(
                name='10',
                value=10
            )
        ]
    )
])
async def _numberguess(ctx, guess: int):
    computerNumber = random.randint(1,10)
    if guess == computerNumber:
        winEmbed = discord.Embed(title=f'Your number is {guess}',color=discord.Colour.green())
        winEmbed.add_field(name='You won!',value=f'The winning number was: {computerNumber}')
        await ctx.send(embed=winEmbed)
        return
    else:
        loseEmbed = discord.Embed(title=f'Your number is {guess}',color=discord.Colour.red())
        loseEmbed.add_field(name='You lost',value=f'The correct number was: {computerNumber}')
        await ctx.send(embed=loseEmbed)

@slash.slash(name='gay',description='Find out how gay you are (joke)',options=[
    create_option(
        name='user',
        description='Select a user',
        required=True,
        option_type=6
    )
])
async def _gay(ctx,user: str):
    gayness = random.randint(0,100)
    gayembed = discord.Embed(title=f'How gay is {user.display_name}?', description=f'{user.mention} is **{gayness}%** gay.',color=discord.Colour.random(),type='image')
    gayembed.set_image(url='https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Gay_Pride_Flag.svg/383px-Gay_Pride_Flag.svg.png')
    await ctx.send(embed=gayembed)

@slash.slash(name='embed',description='Embed creator',options=[
    create_option(
        name='title',
        description='Title of the embed',
        required=True,
        option_type=3
    ),
    create_option(
        name='description',
        description='Description of the embed',
        required=True,
        option_type=3
    )
])
async def _embed(ctx,title: str, description: str):
    customEmbed = discord.Embed(title=title,description=description,color=discord.Colour.random())
    customEmbed.set_thumbnail(url=bot.user.avatar_url)
    await ctx.send(embed=customEmbed)

@slash.slash(name='yn',description='Gives you a yes or no answer',options=[
    create_option(
        name='question',
        description='The question you want answered',
        required=True,
        option_type=3
    )
])
async def _yn(ctx,question: str):
    responses=['Yes','No']
    ynAnswer = random.choice(responses)
    ynEmbed = discord.Embed(title=question,description=ynAnswer,color=discord.Colour.random())
    ynEmbed.set_thumbnail(url=bot.user.avatar_url)
    await ctx.send(embed=ynEmbed)

@slash.slash(name='8ball',description='Gives you a random answer',options=[
    create_option(
        name='question',
        description='The question you want answered',
        required=True,
        option_type=3
    )
])
async def _8ball(ctx,question: str):
        responses = [
        "It is certain",
        "It is decidedly so",
        "Without a doubt",
        "Yes, definitely",
        "You may rely on it",
        "As I see it, yes",
        "Most likely",
        "Outlook good",
        "Yes",
        "Signs point to yes",
        "Reply hazy try again",
        "Ask again later",
        "Better not tell you now",
        "Cannot predict now",
        "Concentrate and ask again",
        "Don't count on it",
        "My reply is no",
        "My sources say no",
        "Outlook not so good",
        "Very doubtful"]
        ballAnswer = random.choice(responses)
        ballEmbed = discord.Embed(title=question,description=ballAnswer,color=discord.Colour.random())
        ballEmbed.set_thumbnail(url=bot.user.avatar_url)
        await ctx.send(embed=ballEmbed)

   # Other category

@slash.slash(name='welcome_option',description='Toggle welcome messages.',options=[
    create_option(
        name='choice',
        description='Whether you want it on or off.',
        required=True,
        option_type=3,
        choices=[
            create_choice(
                name='Off',
                value="False"
            ),
            create_choice(
                name='On',
                value="True"
            )
        ]
    ),
    create_option(
        name='channel',
        description='The channel you want the welcome messages sent in.',
        required=False,
        option_type=7
    )
])
@has_permissions(manage_channels=True)
async def _welcomeoption(ctx,choice: str=None,channel: str=None):
    with open('json/data.json', 'r') as f:
        welcomeJson = json.load(f)

    channel = channel or ctx.channel
    idGuild = str(ctx.guild.id)

    if choice == "False":
        try:
            welcomeJson[f"{idGuild} welcome"].pop()
            welcomeJson[f"{idGuild} welcomeChannel"].pop()
            await ctx.reply("Successfully disabled welcome messages.")
            return
        except:
            await ctx.reply("Successfully disabled welcome messages.")
            return

    channelID = channel.id 

    welcomeJson[f"{idGuild} welcome"] = choice
    welcomeJson[f"{idGuild} welcomeChannel"] = channelID

    with open('json/data.json','w') as f:
        json.dump(welcomeJson, f, indent=4)

    await ctx.reply("Successfully enabled welcome messages.")
    
@slash.slash(name='leave_option',description='Toggle leave messages.',options=[
    create_option(
        name='choice',
        description='Whether you want it on or off.',
        required=True,
        option_type=3,
        choices=[
            create_choice(
                name='Off',
                value="False"
            ),
            create_choice(
                name='On',
                value="True"
            )
        ]
    ),
    create_option(
        name='channel',
        description='The channel you want the leave messages sent in.',
        required=False,
        option_type=7
    )
])
@has_permissions(manage_channels=True)
async def _leaveoption(ctx,choice: str=None,channel: str=None):
    with open('json/data.json', 'r') as f:
        leaveJson = json.load(f)

    channel = channel or ctx.channel
    idGuild = str(ctx.guild.id)

    if choice == "False":
        try:
            leaveJson[f"{idGuild} leave"].pop()
            leaveJson[f"{idGuild} leaveChannel"].pop()
            await ctx.reply("Successfully disabled leave messages.")
            return
        except:
            await ctx.reply("Successfully disabled leave messages.")
            return

    channelID = channel.id 

    leaveJson[f"{idGuild} leave"] = choice
    leaveJson[f"{idGuild} leaveChannel"] = channelID

    with open('json/data.json','w') as f:
        json.dump(leaveJson, f, indent=4)

    await ctx.reply("Successfully enabled leave messages.")

@slash.slash(name='nsfw',description='Finds a nsfw image of what you request.',options=[
    create_option(
        name='request',
        description='Your nsfw request.',
        required=False,
        option_type=3
    )
])
@is_nsfw()
async def _nsfw(ctx, request: str=None):
    if request == None:
        nsfwJson = requests.get("http://api.rule34.xxx//index.php?page=dapi&s=post&q=index&json=1").json()
    else:
        nsfwJson = requests.get("http://api.rule34.xxx//index.php?page=dapi&s=post&q=index&json=1&tags="+request).json()
    chosenKey = random.choice(nsfwJson)
    nsfwFile = chosenKey["file_url"]
    nsfwID = chosenKey["id"]
    nsfwTags = chosenKey["tags"].split()

    tagMessage = ""
    for i in nsfwTags:
        tagMessage = tagMessage + f"`{i}` "


    nsfw_extension = nsfwFile[len(nsfwFile) - 3 :].lower()
    if nsfw_extension == "mp4":
        nsfwPreview = chosenKey["preview_url"]
        nsfwEmbed = discord.Embed(title="Click description for full video.",description=f"[{request}]({nsfwFile})",color=discord.Colour.random(),type='image')
        nsfwEmbed.set_image(url=nsfwPreview)
        nsfwEmbed.add_field(name='Tags:',value=tagMessage)
        nsfwEmbed.set_footer(text=f"ID: {nsfwID} | API by api.rule34.xxx")
        await ctx.reply(embed=nsfwEmbed)
        return
    if nsfw_extension == "jpg" or nsfw_extension == "peg" or nsfw_extension == "png" or nsfw_extension == "gif":
        nsfwEmbed = discord.Embed(title="NSFW",description=f'[{request}]({nsfwFile})',color=discord.Colour.random(),type='image')
        nsfwEmbed.set_image(url=nsfwFile)
        nsfwEmbed.add_field(name='Tags:',value=tagMessage)
        nsfwEmbed.set_footer(text=f"ID: {nsfwID} | API by api.rule34.xxx")
        await ctx.reply(embed=nsfwEmbed)
        return
    await ctx.reply("An error occured while trying to get data from the API.")
            

@slash.slash(name='nsfwreddit',description='Gets posts from a random nsfw subreddit.')
@is_nsfw()
async def _nsfwreddit(ctx):
    sb_random = reddit.random_subreddit(nsfw=True)
    sb_submissions=sb_random.hot()
    post_to_pick = random.randint(1,20)
    for i in range(0,post_to_pick):
        submission = next(x for x in sb_submissions if not x.stickied)


    sb_extension = submission.url[len(submission.url) - 3 :].lower()
    if sb_extension == "jpg" or sb_extension == "png" or sb_extension == "gif":
        sbEmbed = discord.Embed(title=sb_random.display_name,description=f'[{submission.title}]({submission.url})',color=discord.Colour.random(),type='image')
        sbEmbed.set_image(url=submission.url)
        await ctx.send(embed=sbEmbed)
        return
    sbEmbed = discord.Embed(title=sb_random.display_name,description=f'[{submission.title}]({submission.url})',color=discord.Colour.random())
    await ctx.send(embed=sbEmbed)

@slash.slash(name='vote',description=f'vote for this bot.')
async def _vote(ctx):
    voteEmbed = discord.Embed(title=f'Vote',description=f'[top.gg](https://top.gg/bot/{bot.user.id}/vote)',color=discord.Colour.random())
    voteEmbed.set_thumbnail(url=bot.user.avatar_url)
    await ctx.send(embed=voteEmbed)

@slash.slash(name='math',description='Runs basic calculation',options=[
    create_option(
        name='first',
        description='The first number.',
        option_type=4,
        required=True
    ),
    create_option(
        name='operator',
        description='The operator.',
        option_type=3,
        required=True,
        choices=[
            create_choice(
                name='+',
                value='+'
            ),
            create_choice(
                name='-',
                value='-'
            ),
            create_choice(
                name='/',
                value='/'
            ),
            create_choice(
                name='*',
                value='*'
            )
        ]
    ),
    create_option(
        name='second',
        description='The second number.',
        option_type=4,
        required=True
    ),
])
async def _math(ctx,first: int,operator: str,second: int):
    if operator == "+":
        numberEmbed = discord.Embed(title=f'{first} {operator} {second}',description=first+second,color=discord.Colour.random())
        numberEmbed.set_thumbnail(url=bot.user.avatar_url)
        await ctx.send(embed=numberEmbed)
        return
    elif operator == "-":
        numberEmbed = discord.Embed(title=f'{first} {operator} {second}',description=first-second,color=discord.Colour.random())
        numberEmbed.set_thumbnail(url=bot.user.avatar_url)
        await ctx.send(embed=numberEmbed)
        return
    elif operator == "/":
        numberEmbed = discord.Embed(title=f'{first} {operator} {second}',description=first/second,color=discord.Colour.random())
        numberEmbed.set_thumbnail(url=bot.user.avatar_url)
        await ctx.send(embed=numberEmbed)
        return
    elif operator == "*":
        numberEmbed = discord.Embed(title=f'{first} {operator} {second}',description=first*second,color=discord.Colour.random())
        numberEmbed.set_thumbnail(url=bot.user.avatar_url)
        await ctx.send(embed=numberEmbed)
        return
    else:
        await ctx.send("An error occured.")
        return

@slash.slash(name='colour',description='Sends a random colour')
async def _colour(ctx):
    chosenColour = discord.Colour.random()
    colourEmbed = discord.Embed(title=chosenColour,color=chosenColour)
    colourEmbed.set_thumbnail(url=bot.user.avatar_url)
    await ctx.send(embed=colourEmbed)

@slash.slash(name='bug',description='Report a bug.',options=[
    create_option(
        name='bug',
        description='The bug',
        option_type=3,
        required=True
    )
])
async def _bug(ctx,bug: str):
    # Make the embed to send
    bugEmbed = discord.Embed(title="New Bug:",color=discord.Colour.random())
    bugEmbed.set_author(name=ctx.author.display_name,icon_url=ctx.author.avatar_url)
    bugEmbed.add_field(name='Bug:',value=bug)
    bugEmbed.add_field(name='Reported by:',value=f'<@!{ctx.author.id}>')
    owner = bot.get_user(ownerID)
    await owner.send(embed=bugEmbed)
    
    # Make other embed for user
    confirmEmbed = discord.Embed(title='Bug recieved!',color=discord.Colour.random())
    confirmEmbed.add_field(name='Bug:',value=bug)
    confirmEmbed.set_footer(text='Thank you for reporting!')
    await ctx.send(embed=confirmEmbed)

@slash.slash(name='idea',description='Give me ideas.',options=[
    create_option(
        name='idea',
        description='The idea',
        option_type=3,
        required=True
    )
])
async def _idea(ctx,idea: str):
    # Make the embed to send
    bugEmbed = discord.Embed(title="New idea:",color=discord.Colour.random())
    bugEmbed.set_author(name=ctx.author.display_name,icon_url=ctx.author.avatar_url)
    bugEmbed.add_field(name='Idea:',value=idea)
    bugEmbed.add_field(name='Made by:',value=f'<@!{ctx.author.id}>')
    owner = bot.get_user(ownerID)
    await owner.send(embed=bugEmbed)
    
    # Make other embed for user
    confirmEmbed = discord.Embed(title='Idea recieved!',color=discord.Colour.random())
    confirmEmbed.add_field(name='Idea:',value=idea)
    confirmEmbed.set_footer(text='Thank you for your ideas!')
    await ctx.send(embed=confirmEmbed)


# Run the bot
bot.run(token)