import aiohttp
import asyncio
import discord
from discord import Embed

async def get_mini_walls_player_count(api_key):
    base_url = f'https://api.hypixel.net/gameCounts?key={api_key}'

    async with aiohttp.ClientSession() as session:
        async with session.get(base_url) as response:
            data = await response.json()

            if data.get('success', False):
                games = data.get('games', {})
                mini_walls = games.get('MiniWalls', {})
                player_count = mini_walls.get('players', 0)

                return player_count
            else:
                # Handle API error
                return None

async def handle_player_count_command(message, api_key):
    player_count = await get_mini_walls_player_count(api_key)

    if player_count is not None:
        embed = Embed(
            title="Mini Walls Player Count",
            description=f"> Players: {player_count}",
            color=0x2B2D31
        )
        await message.channel.send(embed=embed)
    else:
        await message.channel.send("Failed to retrieve player count. Please try again later.")
