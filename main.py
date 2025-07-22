import os
import discord
import requests
from bs4 import BeautifulSoup
import asyncio

TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

posted_links = set()

async def check_private_placements():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while not client.is_closed():
        try:
            url = 'https://www.privateplacements.com/financings'
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')

            rows = soup.select('table tbody tr')

            for row in rows:
                cells = row.find_all('td')
                if len(cells) < 6:
                    continue

                company = cells[0].get_text(strip=True)
                sector = cells[1].get_text(strip=True)
                amount = cells[2].get_text(strip=True)
                price = cells[3].get_text(strip=True)
                date = cells[5].get_text(strip=True)
                link_tag = cells[0].find('a')
                if not link_tag or not link_tag.get('href'):
                    continue

                link = 'https://www.privateplacements.com' + link_tag['href']

                if 'mining' not in sector.lower():
                    continue

                if link in posted_links:
                    continue

                msg = (
                    f"🧾 **New Private Placement Alert**\n"
                    f"🔸 **Company:** {company}\n"
                    f"🔸 **Amount:** {amount} @ {price}\n"
                    f"🔸 **Date:** {date}\n"
                    f"🔗 {link}"
                )
                await channel.send(msg)
                posted_links.add(link)

        except Exception as e:
            print(f"Error occurred: {e}")

        await asyncio.sleep(600)  # Wait 10 minutes


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    channel = client.get_channel(CHANNEL_ID)
    asyncio.create_task(channel.send("✅ Test message from Private Placement Bot — we're live!"))

@client.event
async def setup_hook():
    client.loop.create_task(check_private_placements())

client.run(TOKEN)

