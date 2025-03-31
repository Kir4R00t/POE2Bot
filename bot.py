from discord.ext import commands
from discord.ui import Button
from discord import app_commands
import discord

from dotenv import load_dotenv
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
    # Main bot guild
    global guild
    for guild in bot.guilds:
        if guild.name == guild:
            break

    # Bot connection info
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    # Commands sync
    try:
        print("Synced commands: \n")
        synced = await bot.tree.sync()
        for x in synced:
            print(f'{x}\n')
        if synced is None:
            print(f'{x} is not synced\n')

    except Exception as error:
        print(error)

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
            print(f"Error Response: {response.text}")

    except Exception as e:
        print(f"Error fetching item data: {e}")

# Currency market check
@bot.tree.command(name="poe2scout", description="Check the current market prices for basic currency !")
@app_commands.describe(category="Select the category of currency")
@app_commands.choices(category=[
    app_commands.Choice(name="Currency", value="currency"),
    app_commands.Choice(name="Soul Cores", value="soul_cores"),
    app_commands.Choice(name="Breachstones", value="breachstones")
])
async def poe2scout(interaction: discord.Interaction, category: app_commands.Choice[str]):
    # Get desired category
    selected = category.value
    if selected == "currency":
        url = 'https://poe2scout.com/api/items/currency'
    elif selected == "soul_cores":
        url = 'https://poe2scout.com/api/items/ultimatum'
    elif selected == "breachstones":
        url = 'https://poe2scout.com/api/items/breachcatalyst'    
    else:
        await interaction.response.send_message("Unknown category.", ephemeral=True)
        return
        
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
  
        embed = discord.Embed(
            title="<:div:1355492390353502388> Currency prices <:div:1355492390353502388>",
            description=("Current rates for basic currency. NOTE: data is collected from poe2scout and they collect data every 3hrs"),
            color=discord.Color.gold()
        )

        # Discord emoji ids
        emojis = {
            # Currency
            'alch': '<:alchemy:1355494399416471764>',
            'annul': '<:annulment:1355494427501662311>',
            'etcher': '<:arcanists_etcher:1356180485071441940>',
            'artificers': '<:artificers_orb:1356180614209863730>',
            'artificers-shard': '<:artificers_shard:1356180664013291643>',
            'aug': '<:augment:1355494457923080222>',
            'chance': '<:chance:1355493353004863488>',
            'chaos': '<:chaos:1355492533236535366>',
            'divine': '<:div:1355492390353502388>',
            'exalted': '<:exalt:1355493424207237210>',
            'gcp': '<:gemcutters_prism:1356180779012587632>',
            'bauble': '<:glassblowers_bauble:1356180826903285825>',
            "Greater Jeweller's Orb": '<:greater_jewellers_orb:1356180894485844009>',
            "Lesser Jeweller's Orb": '<:lesser_jewellers_orb:1356180955731329115>',
            'mirror': '<:mirrorr:1355493390401147023>',
            "Perfect Jeweller's Orb": '<:perfect_jewellers_orb:1356181022227697694>',
            'regal': '<:regal:1355494330571165736>',
            'scrap': '<:scrap:1356180559076003850>',
            'wisdom': '<:scroll_of_wisdom:1356181080993960088>',
            'vaal': '<:vaal:1355492657375215646>',
            'whetstone': '<:whetstone:1356180728844652567>',
            'regal-shard': '<:regal_shard:1356184910464815225>',
            'transmutation-shard': '<:transmutation_shard:1356185270705455195>',
            'transmute': '<:transmutation:1355494366713745468>',
            
            # Soul
            'soul-core-of-atmohua':'<:Soul_Core_of_Atmohua:1356330777222189187>',
            'soul-core-of-azcapa':'<:Soul_Core_of_Azcapa:1356330778845516006>',
            'soul-core-of-cholotl':'<:Soul_Core_of_Cholotl:1356330780107739366>',
            'soul-core-of-citaqualotl':'<:Soul_Core_of_Citaqualotl:1356330752358355251>',
            'soul-core-of-jiquani':'<:Soul_Core_of_Jiquani:1356330754283667670>',
            'soul-core-of-opiloti':'<:Soul_Core_of_Opiloti:1356330756057862375>',
            'soul-core-of-puhuarte':'<:Soul_Core_of_Puhuarte:1356330726651461672>',
            'soul-core-of-quipolatl':'<:Soul_Core_ofQuipolatl:1356330728195096696>',
            'soul-core-of-tacati':'<:Soul_Core_of_Tacati:1356330730069954791>',
            'soul-core-of-ticaba':'<:Soul_Core_of_Ticaba:1356330731990679706>',
            'soul-core-of-topotante':'<:Soul_Core_of_Topotante:1356330689863094356>',
            'soul-core-of-tzamoto':'<:Soul_Core_of_Tzamoto:1356330691524034791>',
            'soul-core-of-xopec':'<:Soul_Core_of_Xopec:1356330692673536152>',
            'soul-core-of-zalatl':'<:Soul_Core_of_Zalatl:1356330693650550920>',
            'soul-core-of-zantipi':'<:Soul_Core_of_Zantipi:1356330662310838423>',

            # Breach catalysts
            'skittering-catalyst': '<:Skittering_Catalyst:1356334422189670470>',
            'sibilant-catalyst': '<:Sibilant_Catalyst:1356334420826787901>',
            'reaver-catalyst': '<:Reaver_Catalyst:1356334419182358719>',
            'neural-catalyst': '<:Neural_Catalyst:1356334497939067147>',
            'flesh-catalyst': '<:Flesh_Catalyst:1356334496978305194>',
            'eshs-catalyst': '<:Eshs_Catalyst:1356334495661428889>',
            'chayulas-catalyst': '<:Chayulas_Catalyst:1356334494344544366>',
            'carapace-catalyst': '<:Carapace_Catalyst:1356334492805107933>',
            'adaptive-catalyst': '<:Adaptive_Catalyst:1356334491269988503>',
            'xophs-catalyst': '<:Xophs_Catalyst:1356334426149093386>',
            'uul-netols-catalyst': '<:UulNetols_Catalyst:1356334424941396069>',
            'tuls-catalyst': '<:Tuls_Catalyst:1356334423100100832>'
        }

        # Load item data & match with emoji
        for line in data['items']:
            item_name = line['id']
            item_emoji = emojis[item_name]
            price = line['latest_price']['price']
            
            embed.add_field(
                name=f"{item_emoji} {item_name}",
                value=f"price = {round(price, 3)} {emojis['exalted']} ",
                inline=True
            )

        await interaction.response.send_message(embed=embed)
    
    else:
        print("ERROR: didn't get a response ...")

# Run the bot
bot.run(BOT_TOKEN)
