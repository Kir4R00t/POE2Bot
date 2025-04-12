from discord.ext import commands
from discord.ui import Button
from discord import app_commands
import discord

from dotenv import load_dotenv
from time import sleep
import json
import requests
import random
import os

from poe2bot import pagination
from poe2bot import item_emojis

import logging

# Add Logging
logger = logging.getLogger("poe2bot_discord")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(filename="poe2bot_discord.log", encoding="utf-8", mode="w")
logger.addHandler(console_handler)
logger.addHandler(file_handler)

load_dotenv('.env')
BOT_TOKEN = os.getenv('DISCORD')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    # Main bot guild
    global guild
    for guild in bot.guilds:
        if guild.name == guild:
            break

    # Bot connection info
    logger.info(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    # Commands sync
    try:
        logger.info("Synced commands: \n")
        synced = await bot.tree.sync()
        for x in synced:
            logger.info(f'{x}\n')
        if synced is None:
            logger.info(f'{x} is not synced\n')

    except Exception as error:
        logger.error(error)

# Message reactions
@bot.event
async def on_message(message):
    if message.content.lower() == 'ping':
        await message.channel.send('pong')
    
    if message.content.lower() == 'ding':
        await message.channel.send('dong')

# Coinflip
@bot.tree.command(name="coinflip", description="Flip a coin")
async def coinflip(interaction: discord.Interaction):
    coin = random.randint(1, 2)
    if coin == 1:
        await interaction.response.send_message("Heads", ephemeral=False)
    else:
        await interaction.response.send_message("Tails", ephemeral=False)


# RTD
@bot.tree.command(name="rtd", description="Roll the dice")
async def rtd(interaction: discord.Interaction):
    dice = random.randint(1, 6)
    await interaction.response.send_message(f"You have rolled {dice}", ephemeral=False)

# CATSSS
@bot.tree.command(name="gibcat", description="Get a random image of a cat :3")
async def gibcat(interaction: discord.Interaction):
    load_dotenv('.env')
    api_key = os.getenv('CAT_API')
    url = f"https://api.thecatapi.com/v1/images/search?&api_key={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        cat_photo_url = (data[0]['url'])
        if data:
            await interaction.response.send_message(cat_photo_url, ephemeral=False)
        else:
            await interaction.response.send_message("No data from API", ephemeral=False)
    else:
        await interaction.response.send_message(f"API ERROR: {response.status_code}", ephemeral=False)

# Poe2 Trade
@bot.tree.command(name="trade", description="Issue a query to poe2 trade API")
async def trade(interaction: discord.Interaction, query: str): # , id: str
    load_dotenv('.env')
    
    # API endpoint
    base_url = "https://www.pathofexile.com/api/trade2/"
    search_url = base_url + "search/poe2/Standard"
    fetch_url = base_url + "fetch/"
    poe_session_id = os.getenv('POE_SESSION_ID')

    # Headers
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': '5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Cookie': f'POESESSID={poe_session_id}',
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }

    # Decode query
    try:
        query = json.loads(query)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        exit()

    # Send search request
    try:
        response = requests.post(search_url, headers=headers, json=query)
        logger.info(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            response_json = response.json()
            query_id = response_json.get("id")
        else:
            logger.warning(f"Error Response: {response.text}")
            exit()
    except Exception as e:
        logger.error(f"Error sending search request: {e}")
        exit()

    # Fetch item details
    result_ids = response_json.get("result", [])[:10]
    if not result_ids:
        logger.warning("No results found.")
        exit()

    result_ids_combined = ",".join(result_ids)
    fetch_snippet = f"{result_ids_combined}?query={query_id}"
    full_fetch_url = fetch_url + fetch_snippet

    # Send fetch request
    try:
        response = requests.get(full_fetch_url, headers=headers)
        logger.info(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()

            embeds = []
            for result in data['result']:
                item = result.get("item", {})
                listing = result.get("listing", {})
                account = listing.get("account", {}).get("name", "Unknown")
                price = listing.get("price", {})
                mods = item.get("explicitMods", [])
                enchant = item.get("enchantMods", [])
                icon_url = item.get("icon")
                socketed_items = item.get("socketedItems", [])
                socket_count = len(item.get("sockets", []))

                # Create embed for this item
                embed = discord.Embed(
                    title=f"{item.get('name', '')} {item.get('typeLine', '')}",
                    description=(
                        f"**iLvl**: {item.get('ilvl')}\n"
                        f"**League**: {item.get('league')}\n"
                        f"**Corrupted**: {item.get('corrupted')}\n"
                        f"**Note**: {item.get('note', 'N/A')}"
                    ),
                    color=discord.Color.gold()
                )
                embed.set_thumbnail(url=icon_url)
                embed.set_footer(text=f"Seller: {account} | Price: {price.get('amount')} {price.get('currency')}")

                # Sockets
                if socketed_items:
                    socketed_text = "\n".join(
                        f"- {s.get('name', '')} {s.get('typeLine', '')}".strip()
                        for s in socketed_items
                    )
                    embed.add_field(name="Sockets", value=str(socket_count), inline=True)
                    embed.add_field(name="Socketed Items", value=socketed_text, inline=False)
                
                # Explicit
                if mods:
                    embed.add_field(
                        name="Explicit Mods",
                        value="\n".join(f"- {mod}" for mod in mods),
                        inline=False
                    )

                # Enchants
                if enchant:
                    embed.add_field(
                        name="Enchant Mods",
                        value="\n".join(f"- {mod}" for mod in enchant),
                        inline=False
                    )

                embeds.append(embed)

            # Create pagination & add trade_url button
            if embeds:
                trade_search_url = f"https://www.pathofexile.com/trade2/search/poe2/Standard/{query_id}"
                trade_button = Button(label="Open in Trade", style=discord.ButtonStyle.link, url=trade_search_url)
                view = pagination.PaginatedView(embeds)
                view.add_item(trade_button)

                await interaction.response.send_message(embed=embeds[0], view=view)
            else:
                await interaction.response.send_message("No items found.", ephemeral=True)

            sleep(5)  # Avoid hammering the server
        else:
            logger.error(f"Error Response: {response.text}")

    except Exception as e:
        logger.error(f"Error fetching item data: {e}")

# Currency market check
# https://poe2scout.com/api/swagger
@bot.tree.command(name="poe2scout", description="Check the current market prices for specified item category")
@app_commands.describe(category="Select the category of currency")
@app_commands.choices(category=[
    app_commands.Choice(name="Currency", value="currency"),
    app_commands.Choice(name="Soul Cores", value="soul_cores"),
    app_commands.Choice(name="Breachstones", value="breachstones"),
    app_commands.Choice(name="Distilled Emotions", value="distilled"),
    app_commands.Choice(name="Essences", value="essences")

])
async def poe2scout(interaction: discord.Interaction, category: app_commands.Choice[str]):
    # Load emojis
    emojis = item_emojis.list

    # Get desired category
    selected = category.value
    if selected == "currency":
        url = 'https://poe2scout.com/api/items/currency/currency'
    elif selected == "soul_cores":
        url = 'https://poe2scout.com/api/items/currency/ultimatum'
    elif selected == "breachstones":
        url = 'https://poe2scout.com/api/items/currency/breachcatalyst' 
    elif selected == "distilled":
        url = 'https://poe2scout.com/api/items/currency/deliriuminstill'
    elif selected == "essences":
        url = 'https://poe2scout.com/api/items/currency/essences'            
    else:
        await interaction.response.send_message("Unknown category.", ephemeral=True)
        return
        
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
  
        embed = discord.Embed(
            title=f"{emojis['divine']} Currency prices {emojis['divine']}",
            description="Current rates for basic currency. NOTE: data is collected from poe2scout and they collect data every 3hrs",
            color=discord.Color.gold()
        )

        # Load item data & match with emoji
        for line in data['items']:
            item_name = line['apiId']
            item_emoji = emojis[item_name]
            price = line['currentPrice']
            
            embed.add_field(
                name=f"{item_emoji} {item_name}",
                value=f"price = {round(price, 3)} {emojis['exalted']} ",
                inline=True
            )

        await interaction.response.send_message(embed=embed)
    
    else:
        await interaction.response.send_message('poe2scout API is down', ephemeral=True)
        logger.warning("Did not get a response ... poe2scout API may be down")

# Run the bot
bot.run(BOT_TOKEN)
