import discord
from mwEmbedStats import create_stats_embed
from mwPlayerCount import handle_player_count_command
from mwCompare import compare_stats
from mwLeaderboardsa import get_leaderboard, display_leaderboard

intents = discord.Intents.all()

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.event
async def on_message(message):
    api_key = 'c756ff14-d79f-4879-b51e-bec482eb347e'  
    if message.author == bot.user:
        return

    if message.content.startswith('.s'):
        # Extract the username from the message
        username = message.content[3:].strip() 
        
        # Pass the username to create_stats_embed
        embed = await create_stats_embed(username)
        if embed:
            await message.channel.send(embed=embed)
            
    if message.content.startswith('.pc'):
        await handle_player_count_command(message, api_key)

    if message.content.startswith('.c'):
        await compare_stats(message)

    if message.content.startswith('.lb'):
        # Extract the parameters from the message
        params = message.content[4:].strip().split()

        # Check if the correct number of parameters is provided
        if len(params) < 1 or len(params) > 2:
            await message.channel.send("Please provide a valid command. Usage: `.lb stat [period]`")
            return

        # Assign parameters to variables
        stat = params[0].lower()
        period = params[1].lower() if len(params) == 2 else 'lifetime'

        # Check if the entered stat is valid
        valid_stats = ['wins', 'finals', 'kills', 'deaths', 'wdmg', 'wkills', 'arrowhit', 'arrowshot', 'fkdr', 'kdr', 'fdr', 'wdd', 'wkd', 'aa']
        if stat not in valid_stats:
            await message.channel.send("Invalid stat. Valid stats are: wins, finals, kills, deaths, wdmg, wkills, arrowhit, arrowshot, fkdr, kdr, fdr, wdd, wkd, aa")
            return

        # Fetch leaderboard data
        leaderboard = await get_leaderboard(api_key, stat, period)

        # Display the leaderboard
        await display_leaderboard(message, leaderboard)

bot.run('MTAwNjI2NTY1NTEyNjkzNzY4MA.GcnM5j.Ki68TMFhNKiR5jAUNaT7GaFEIpmk11421Z9nvg')
