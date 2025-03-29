from discord.ext import commands
from dotenv import load_dotenv
from discord.ui import View, Button
import discord
from time import sleep
import json
import requests
import random
import pagination
import os

load_dotenv('.env')
BOT_TOKEN = os.getenv('DISCORD')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Error syncing commands: {e}")

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
async def coinflip(interaction: discord.Interaction):
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

    # Parse query JSON & query ID
    id = "youcanputwhateverinhere"
    raw_query_json = query
    query_id = id

    try:
        query = json.loads(raw_query_json)

    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        exit()

    # Send search request
    try:
        response = requests.post(search_url, headers=headers, json=query)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            response_json = response.json()
            query_id = response_json.get("id")
        else:
            print(f"Error Response: {response.text}")
            exit()
    except Exception as e:
        print(f"Error sending search request: {e}")
        exit()

    # Fetch item details
    result_ids = response_json.get("result", [])[:10]
    if not result_ids:
        print("No results found.")
        exit()

    result_ids_combined = ",".join(result_ids)
    fetch_snippet = f"{result_ids_combined}?query={query_id}"
    full_fetch_url = fetch_url + fetch_snippet

    # Send fetch request
    try:
        response = requests.get(full_fetch_url, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            
            #print("Fetched item data:")
            #print(json.dumps(data, indent=2))
        
            embeds = []

            for result in data['result']:
                item = result.get("item", {})
                listing = result.get("listing", {})
                account = listing.get("account", {}).get("name", "Unknown")
                price = listing.get("price", {})
                mods = item.get("explicitMods", [])
                enchant = item.get("enchantMods", [])
                icon_url = item.get("icon")

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

                if mods:
                    embed.add_field(
                        name="Explicit Mods",
                        value="\n".join(f"- {mod}" for mod in mods),
                        inline=False
                    )

                if enchant:
                    embed.add_field(
                        name="Enchant Mods",
                        value="\n".join(f"- {mod}" for mod in enchant),
                        inline=False
                    )

                embeds.append(embed)

            if embeds:
                trade_search_url = f"https://www.pathofexile.com/trade2/search/poe2/Standard/{query_id}"
                trade_button = Button(label="Open in Trade", style=discord.ButtonStyle.link, url=trade_search_url)
                view = pagination.PaginatedView(embeds)
                view.add_item(trade_button)

                await interaction.response.send_message(embed=embeds[0], view=view)
    
                print(f"Number of items found: {len(embeds)}")
            else:
                await interaction.response.send_message("No items found.", ephemeral=True)


            sleep(5)  # Avoid hammering the server
        else:
            print(f"Error Response: {response.text}")
    except Exception as e:
        print(f"Error fetching item data: {e}")



bot.run(BOT_TOKEN)