# Imports
import interactions
import json
from datetime import datetime
import requests
import praw
import random

# Setting up the bot

with open('config.json','r') as f:
    config = json.load(f)
token = config['token']
guildIDs = config['guildIDs']
redditID = config['redditID']
redditSecret = config['redditSecret']
redditAgent = config['redditAgent']
reddit = praw.Reddit(client_id=redditID,client_secret=redditSecret,user_agent=redditAgent,check_for_async=False)

bot = interactions.Client(token=token)

@bot.event
async def on_ready():
    bot.start_time = datetime.utcnow()
    print(f"{bot.me.name} is ready.")

# Commands
 # Information Category

# idk how to do permissions in this bruh
# @bot.command(name='poll',description='Run a poll',scope=guildIDs)
# async def _poll(ctx):
#     await ctx.send(ctx.member.permissions)
#     await ctx.send('test')

@bot.command(name='information',description='Sends info on the bot.')
async def _information(ctx):
    embed = interactions.Embed(title='discord-interactions',description='by <@!327807253052653569>\n[Github Page](https://github.com/Duzos/dbs-new)\n[Support Server](https://discord.gg/Raakw6367z)',thumbnail=interactions.EmbedImageStruct(url='https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/768px-Python-logo-notext.svg.png')._json,color=0xFF6E00)
    await ctx.send(embeds=[embed],ephemeral=True)

@bot.command(type=interactions.ApplicationCommandType.USER,name='Get Avatar')
async def _getavatar(ctx: interactions.CommandContext):
    embed = interactions.Embed(title=f'{ctx.target.nick}\'s Avatar',image=interactions.EmbedImageStruct(url=f'https://cdn.discordapp.com/avatars/{ctx.target.id}/{ctx.target.avatar}')._json)
    await ctx.send(embeds=[embed])

@bot.command(name='uptime',description='Tells you how long the bot has been online for.')
async def _uptime(ctx):
    delta_uptime = datetime.utcnow() - bot.start_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    embed = interactions.Embed(title='Uptime',description=f"{days}d, {hours}h, {minutes}m, {seconds}s",thumbnail=interactions.EmbedImageStruct(url=f'https://cdn.discordapp.com/avatars/{bot.me.id}/{bot.me.icon}')._json)
    await ctx.send(embeds=[embed],ephemeral=True)

@bot.command(name='bitcoin',description='Sends the current price of bitcoin.',options=[
    interactions.Option(
        type=interactions.OptionType.INTEGER,
        name='amount',
        description='The amount of bitcoin.',
        min_value=1,
        required=False
    )
])
async def _bitcoin(ctx, amount=1):
    response_API = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
    data = response_API.text
    parse_json = json.loads(data)
    bitcoinGBP = parse_json['bpi']['GBP']['rate_float']
    bitcoinUSD = parse_json['bpi']['USD']['rate_float']
    bitcoinEUR = parse_json['bpi']['EUR']['rate_float']


    embed = interactions.Embed(title=f'Price of {amount} bitcoin',fields=[interactions.EmbedField(name='(???)EUR',value=round(bitcoinEUR * amount))._json,interactions.EmbedField(name='(??)GBP',value=round(bitcoinGBP * amount))._json,interactions.EmbedField(name='($)USD',value=round(bitcoinUSD * amount))._json],thumbnail=interactions.EmbedImageStruct(url="https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/64px-Bitcoin.svg.png")._json,footer=interactions.EmbedFooter(text='API by coindesk')._json,color=0xffd700)
    await ctx.send(embeds=[embed])


@bot.command(name='invite',description='Gives you the bots invite')
async def _invite(ctx):
        embed = interactions.Embed(title="Invite Link",description="[Bot Invite](https://discord.com/api/oauth2/authorize?client_id=900481597311172660&permissions=0&scope=bot%20applications.commands)",fields=[interactions.EmbedField(name='Support Server',value="[Server Invite](https://discord.gg/Raakw6367z)")._json,interactions.EmbedField(name='Get Dubot!'"[Dubot Invite](https://discord.com/api/oauth2/authorize?client_id=865190020179296267&permissions=0&scope=bot%20applications.commands)")._json])
        await ctx.send(embeds=[embed],ephemeral=True)

 # Fun Category

@bot.command(name='insult',description='Produces an insult for you')
async def _insult(ctx):
    url = 'https://insult.mattbas.org/api/insult.json'
    responseApi = requests.get(url).json()
    insult = responseApi['insult']

    embed = interactions.Embed(title='Insult',description=insult,footer=interactions.EmbedFooter(text=f"API: {url}")._json,color=0xED1C06)
    await ctx.send(embeds=[embed])

@bot.command(name='spaceweights',description='Get your weight on other planets.',options=[
    interactions.Option(
        type=interactions.OptionType.INTEGER,
        name='weight',
        description='Your weight in kg',
        required=True
    ),
    interactions.Option(
        type=interactions.OptionType.STRING,
        name='planet',
        description='The planet you want to find out your weight on.',
        required=True
    )
])
async def _spaceweights(ctx, weight: int, planet: str):
    planet = planet.lower()
        
    planets = {
    "sun": 27.01,
    "mercury": 0.38,
    "venus": 0.91,
    "moon": 0.166,
    "mars": 0.38,
    "jupiter": 2.34,
    "saturn": 1.06,
    "uranus": 0.92,
    "neptune": 1.19,
    "pluto": 0.06,
    "earth": 1,
    "io": 0.183,
    "europa": 0.133,
    "ganymede": 0.144,
    "callisto": 0.126
    }


    if planet not in planets:
        planetList = ""
        for val in planets:
            planetList = planetList + val + "\n"
        return await ctx.send(f"Please provide a valid planet:\n{planetList}")

    multiple = planets[planet]
    embed = interactions.Embed(title='Space Weights', description=f"Your weight on {planet} is {weight * multiple}kg.")
    await ctx.send(embeds=[embed])

@bot.command(name='truthordare',description='Play truth or dare')
async def _tod(ctx):
    url = 'https://gist.githubusercontent.com/deepakshrma/9498a19a3ed460fc662c536d138c29b1/raw/f29d323b9b3f0a82f66ed58c7117fb9b599fb8d5/truth-n-dare.json'
    responseApi = requests.get(url).json()
    sfw_list = [
        item
        for item in responseApi
        if int(item['level']) < 4
    ]
    choice = random.choice(sfw_list)
    choiceID = choice['id']
    choiceLevel = choice['level']
    choiceType = choice['type']
    choiceSum = choice['summary']


    embed = interactions.Embed(title=choiceType,description=choiceSum,color=0xA7C7E7,footer=interactions.EmbedFooter(text=f'ID: {choiceID} | Level: {choiceLevel}')._json)
    await ctx.send(embeds=[embed])

@bot.command(name='truth',description='Pick a truth')
async def _truth(ctx):
    url = 'https://gist.githubusercontent.com/deepakshrma/9498a19a3ed460fc662c536d138c29b1/raw/f29d323b9b3f0a82f66ed58c7117fb9b599fb8d5/truth-n-dare.json'
    responseApi = requests.get(url).json()
    truth_list = [
        item
        for item in responseApi
        if item["type"] == "Truth"
    ]

    choice = random.choice(truth_list)
    choiceType = choice['type']
    choiceID = choice['id']
    choiceLevel = choice['level']
    choiceSum = choice['summary']

    embed = interactions.Embed(title=choiceType,description=choiceSum,color=0xA7C7E7,footer=interactions.EmbedFooter(text=f'ID: {choiceID} | Level: {choiceLevel}')._json)
    await ctx.send(embeds=[embed])

@bot.command(name='dare',description='Pick a dare')
async def _dare(ctx):
    url = 'https://gist.githubusercontent.com/deepakshrma/9498a19a3ed460fc662c536d138c29b1/raw/f29d323b9b3f0a82f66ed58c7117fb9b599fb8d5/truth-n-dare.json'
    responseApi = requests.get(url).json()
    dare_list = [
        item
        for item in responseApi
        if item["type"] == "Dare"
    ]

    choice = random.choice(dare_list)
    choiceType = choice['type']
    choiceID = choice['id']
    choiceLevel = choice['level']
    choiceSum = choice['summary']
    embed = interactions.Embed(title=choiceType,description=choiceSum,color=0xA7C7E7,footer=interactions.EmbedFooter(text=f'ID: {choiceID} | Level: {choiceLevel}')._json)
    await ctx.send(embeds=[embed])


@bot.command(name='random-reddit',description='Gets a post from a random subreddit.')
async def _randomreddit(ctx):
    await ctx.defer()
    sb_random = reddit.random_subreddit()
    sb_submissions=sb_random.hot()
    post_to_pick = random.randint(1,20)
    for i in range(0,post_to_pick):
        submission = next(x for x in sb_submissions if not x.stickied)


    sb_extension = submission.url[len(submission.url) - 3 :].lower()
    if sb_extension == "jpg" or sb_extension == "png" or sb_extension == "gif":
        embed = interactions.Embed(title=sb_random.display_name,description=f'[{submission.title}]({submission.url})',type="image",image=interactions.EmbedImageStruct(url=submission.url)._json)
        await ctx.send(embeds=[embed])
        return
    embed = interactions.Embed(title=sb_random.display_name,description=f'[{submission.title}]({submission.url})')
    await ctx.send(embeds=[embed])

@bot.command(name='subreddit',description='Gets a post from the provided subreddit.',options=[
    interactions.Option(
        type=interactions.OptionType.STRING,
        name='subreddit',
        description='The subreddit.',
        required=True
    )
])
async def _subreddit(ctx, subreddit):
    await ctx.defer()
    sb_submissions = reddit.subreddit(subreddit).hot()
    post_to_pick = random.randint(1,20)
    for i in range(0,post_to_pick):
        submission = next(x for x in sb_submissions if not x.stickied)

    sb_extension = submission.url[len(submission.url) - 3 :].lower()
    if sb_extension == "jpg" or sb_extension == "png" or sb_extension == "gif":
        embed = interactions.Embed(title=subreddit,description=f'[{submission.title}]({submission.url})',image=interactions.EmbedImageStruct(url=submission.url)._json,type='image')
        await ctx.send(embeds=[embed])
        return
    embed = interactions.Embed(title=subreddit,description=f'[{submission.title}]({submission.url})')
    await ctx.send(embeds=[embed])

@bot.command(name='say',description='Repeats what you say.',options=[
    interactions.Option(
        type=interactions.OptionType.STRING,
        name='message',
        description='What you want the bot to say.',
        required=True
    )
])
async def _say(ctx, message: str):
    if "@everyone" in message or "@here" in message:
        await ctx.send("You cannot have `@everyone` or `@here` in your message!")
        return
    await ctx.send(message)

# Tests

# @bot.command(name='modal-test',description='modal test',scope=guildIDs)
# async def _modal_test(ctx):
#     modal = interactions.Modal(
#         title='modal test',
#         custom_id='modal-test-id',
#         components=[interactions.TextInput(
#             style=interactions.TextStyleType.SHORT,
#             label='what a cool test',
#             custom_id="text_input_response",
#             min_length=1,
#             max_length=3
#         )]
#     )

#     await ctx.popup(modal)

# @bot.modal('modal-test-id')
# async def modal_test_response(ctx, response: str):
#     await ctx.send(f"You wrote: {response}")

# @bot.command(name='test',description='simple test command for interactions library',scope=guildIDs)
# async def _test(ctx):
#     await ctx.send("HI")
#     embed = interactions.Embed(title='embed test',description='test',author=interactions.EmbedAuthor(name='Name')._json,thumbnail=interactions.EmbedImageStruct(url="https://cdn.discordapp.com/attachments/827389916894724099/923323428323348590/IMG_5706.png")._json,fields=[interactions.EmbedField(name='field 1',value='field 1 value')._json],footer=interactions.EmbedFooter(text='footer')._json,color=0xff0000)
#     button = interactions.Button(style=interactions.ButtonStyle.PRIMARY,label='I AM A BUTTON',custom_id='test_button')
#     await ctx.send(embeds=[embed], components=button)

# @bot.command(type=interactions.ApplicationCommandType.USER,name='context menu test',scope=guildIDs)
# async def _contexttest(ctx):
#     await ctx.send(f"You used a context menu on <@!{ctx.target.id}>!")



bot.start()
