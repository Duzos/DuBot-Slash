# Importing
import discord
from discord.embeds import EmptyEmbed
from discord.ext import commands
from discord.ext.commands.converter import _get_from_guilds
from discord_slash import SlashCommand,SlashContext
from discord_slash.utils.manage_commands import create_choice,create_option
import json
import os
import sys
import requests
import random

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
        inviteEmbed.add_field(name='Support Server',value="[Server Invite](https://discord.gg/Raakw6367z)")
        await ctx.send(embed=inviteEmbed)

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
    diceEmbed.set_thumbnail(bot.avatar_url)
    await ctx.send(diceEmbed)

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
            resultEmbed.set_thumbnail(bot.avatar_url)
            await ctx.send(embed=resultEmbed)
            return
        elif computers_answer == "rock":
            if player == "paper":
                resultEmbed = discord.Embed(title='You win!',description=f'Your opponent picked {computers_answer}.',color=discord.Colour.random())
                resultEmbed.set_thumbnail(bot.avatar_url)
                await ctx.send(embed=resultEmbed)
                return
            if player == "scissors":
                resultEmbed = discord.Embed(title='You lose.',description=f'Your opponent picked {computers_answer}.',color=discord.Colour.random())
                resultEmbed.set_thumbnail(bot.avatar_url)
                await ctx.send(embed=resultEmbed)
                return
        elif computers_answer == "paper":
            if player == "scissors":
                resultEmbed = discord.Embed(title='You win!',description=f'Your opponent picked {computers_answer}.',color=discord.Colour.random())
                resultEmbed.set_thumbnail(bot.avatar_url)
                await ctx.send(embed=resultEmbed)
                return
            if player == "rock":
                resultEmbed = discord.Embed(title='You lose.',description=f'Your opponent picked {computers_answer}.',color=discord.Colour.random())
                resultEmbed.set_thumbnail(bot.avatar_url)
                await ctx.send(embed=resultEmbed)
                return
        elif computers_answer == "scissors":
            if player == "rock":
                resultEmbed = discord.Embed(title='You win!',description=f'Your opponent picked {computers_answer}.',color=discord.Colour.random())
                resultEmbed.set_thumbnail(bot.avatar_url)
                await ctx.send(embed=resultEmbed)
                return
            if player == "paper":
                resultEmbed = discord.Embed(title='You lose.',description=f'Your opponent picked {computers_answer}.',color=discord.Colour.random())
                resultEmbed.set_thumbnail(bot.avatar_url)
                await ctx.send(embed=resultEmbed)
                return
        else:
            return

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
    customEmbed.set_thumbnail(bot.avatar_url)
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
    ynEmbed.set_thumbnail(bot.avatar_url)
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
        ballEmbed.set_thumbnail(bot.avatar_url)
        await ctx.send(embed=ballEmbed)


# Run the bot
bot.run(token)