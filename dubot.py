# Importing
import discord
from discord import colour
from discord import guild
from discord.embeds import EmptyEmbed
from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands.converter import _get_from_guilds
from discord.ext.commands.core import has_permissions
from discord.ext.commands.core import MissingPermissions
from discord.ext.commands.core import BotMissingPermissions
from discord_slash import SlashCommand,SlashContext
from discord_slash.utils.manage_commands import create_choice,create_option
import topgg
import json
import os
import sys
import requests
import random

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
async def on_guild_join(guild):
    try:
        await bot.change_presence(status=discord.Status.online, activity=discord.Game(f"in {len(bot.guilds)} servers."))
    except Exception as e:
        owner = bot.get_user(ownerID)
        await owner.send('Failed to update status\n{}:{}'.format(type(e).__name__, e))

@bot.event
async def on_guild_leave(guild):
    try:
        await bot.change_presence(status=discord.Status.online, activity=discord.Game(f"in {len(bot.guilds)} servers."))
    except Exception as e:
        owner = bot.get_user(ownerID)
        await owner.send('Failed to update status\n{}:{}'.format(type(e).__name__, e))


# Handling Errors.
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.NotOwner) or isinstance(error, commands.NoPrivateMessage):
        return
    elif isinstance(error, commands.BotMissingPermissions):
        botPermEmbed = discord.Embed(title='ERROR',description='The Bot is missing the required permission(s).',color=0x992D22)
        permValues = ''
        for perm in error.missing_perms:
            permValues = permValues+ f"{perm}\n"
        botPermEmbed.add_field(name="Missing Permission(s):",value=permValues,inline=False)
        botPermEmbed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url
        )
        botPermEmbed.set_thumbnail(url=bot.user.avatar_url)
        await ctx.send(embed=botPermEmbed)
        return
    elif isinstance(error, commands.MissingPermissions):
        botPermEmbed = discord.Embed(title='ERROR',description='You are missing the required permission(s).',color=0x992D22)
        permValues = ''
        for perm in error.missing_perms:
            permValues = permValues+ f"{perm}\n"
        botPermEmbed.add_field(name="Missing Permission(s):",value=permValues,inline=False)
        botPermEmbed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url
        )
        botPermEmbed.set_thumbnail(url=bot.user.avatar_url)
        await ctx.send(embed=botPermEmbed)
        return
    else:
        errorEmbed = discord.Embed(title='ERROR',description=error,color=0x992D22)
        errorEmbed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url
        )
        errorEmbed.set_thumbnail(url=bot.user.avatar_url)
        await ctx.send(embed=errorEmbed)


# The commands

 # Owner commands
@bot.command(name='shutdown',description='Shuts the bot down')
@commands.is_owner()
async def _shutdown(ctx):
    await ctx.send("Bye!")
    await bot.change_presence(status=discord.Status.invisible)
    await slash.close()
    await bot.close()

@bot.command(name='restart',description='Restarts the bot')
@commands.is_owner()
async def _restart(ctx):
    await ctx.send("See you soon!")
    await bot.change_presence(activity=discord.Game("Restarting."))
    os.execv(sys.executable, ['python'] + sys.argv)

@bot.command(name='server_list',description='Gets the list of servers the bot is in.')
@commands.is_owner()
async def _serverList(ctx):
    await ctx.message.delete()
    list = ""
    for guild in bot.guilds:
        list += f"{guild.name}: {guild.id}\n"
    owner = bot.get_user(ownerID)
    await owner.send(list)

@bot.command(name='server_info_owner',description='Sends information on a server the bot is.')
@commands.is_owner()
async def _serverinfoowner(ctx,guild: commands.GuildConverter=None):
    await ctx.message.delete()
    owner = bot.get_user(ownerID)
    guild = guild or ctx.guild

    date_format = "%a, %d %b %Y %I:%M %p"

    roleList = ", ".join([str(r.name) for r in guild.roles])

    ginfoEmbed = discord.Embed(title=f'Info on {guild.name}',description=f'**Description:**\n```{guild.description}```\n**Member Count:**\n```{guild.member_count}```\n**Owner:**\n```{guild.owner}```\n**Roles:**\n```{roleList}```\n**Boost Level:**\n```{guild.premium_tier}```\n**Boost Count:**\n```{guild.premium_subscription_count}```\n**ID:**\n```{guild.id}```\n**Guild Created On:**\n```{guild.created_at.strftime(date_format)}```\n**Region:**\n```{guild.region}```',color=discord.Colour.random())
    ginfoEmbed.set_thumbnail(url=guild.icon_url)
    ginfoEmbed.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
    await owner.send(embed=ginfoEmbed)

 # Slash commands:

  # Moderation Category:

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
        await user.kick(reason=reason)
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
    await channel.set_permissions(ctx.guild.default_role,overwrite=overwrite)
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
    await channel.set_permissions(ctx.guild.default_role,overwrite=overwrite)
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
            await user.add_roles(discord.Role)
            await user.add_roles(discord.Role)
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
    role =  await guild.create_role(name='Muted',reason='Muted role was not found, so I made one.',permissions=permissions)
    for discord.TextChannel in channels:
        await discord.TextChannel.set_permissions(role,send_message=False)
    for discord.VoiceChannel in channels:
        await discord.VoiceChannel.set_permissiosn(role,speak=False)
    
    await user.add_roles(role)
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
            await user.remove_roles(discord.Role,reason="Unmuting the user.")
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
    await user.ban(reason=reason)

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
    await ctx.channel.edit(slowmode_delay=seconds)
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
    await ctx.channel.purge(limit=amount)
    msg = await ctx.send("Clear complete.")
    await msg.delete()
  # Information Category:

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
        roles = ", ".join(rolelist)
        if roles == "":
            roles=None
        date_format = "%a, %d %b %Y %I:%M %p"
        uinfoEmbed = discord.Embed(title=f'Info on {user.name}#{user.discriminator}', description=f'**ID:**\n```{user.id}```\n**Roles:**\n```{roles}```\n**Account Created On:**\n```{user.created_at.strftime(date_format)}```\n**Account Joined Guild On:**\n```{user.joined_at.strftime(date_format)}```\n**Nickname:**\n```{user.nick}```\n**Is Bot:**\n```{user.bot}```',color=discord.Colour.random())
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

        rinfoEmbed = discord.Embed(title=f'Info on {role.name}',description=f'**ID:**\n```{role.id}```\n**Can be Mentioned:**\n```{role.mentionable}```\n**Position:**\n```{role.position}```\n**Role Created On:**\n```{role.created_at.strftime(date_format)}```\n**Colour:**\n```{role.colour}```\n**Members:**\n```{memberList}```',color=role.colour)
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
    bugEmbed.set_author(name=ctx.author.name,icon_url=ctx.author.avatar_url)
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
    bugEmbed.set_author(name=ctx.author.name,icon_url=ctx.author.avatar_url)
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