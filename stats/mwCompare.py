import discord
from mwStats import calculate_ratios

async def compare_stats(message):
    # Extract usernames from the message
    usernames = message.content[3:].strip().split()

    # Check if two usernames are provided
    if len(usernames) != 2:
        await message.channel.send("Please provide exactly two usernames for comparison.")
        return

    # Fetch stats for both players
    stats1 = await calculate_ratios(usernames[0])
    stats2 = await calculate_ratios(usernames[1])

    if stats1 is None or stats2 is None:
        await message.channel.send("Failed to fetch stats for one or both users.")
        return

    # Create an embed with side-by-side comparison
    embed = discord.Embed(title=f"{stats1['displayname']} vs {stats2['displayname']}", color=0x2B2D31)

    # Function to add comparison indicators
    def add_comparison_indicator(value1, value2, stat_name, is_ratio=False):
        if stat_name == 'Deaths':
            indicator = '<:greaterthan:1167439156566315039>' if value1 < value2 else '<:lessthan:1167439160139849738>'
        else:
            indicator = '<:greaterthan:1167439156566315039>' if value1 > value2 else '<:lessthan:1167439160139849738>'
        format_string = "{:,.2f}" if is_ratio else "{:,}"
        return f"{indicator} **{stat_name}**\n<:blanksort:1167444202934771792>`{format_string}` | `{format_string}`\n".format(value1, value2)

    # Stats column
    stats_column = (
        add_comparison_indicator(stats1['wins'], stats2['wins'], 'Wins')
        + add_comparison_indicator(stats1['kills'], stats2['kills'], 'Kills')
        + add_comparison_indicator(stats1['finals'], stats2['finals'], 'Finals')
        + add_comparison_indicator(stats1['witherDmg'], stats2['witherDmg'], 'Wither Damage')
        + add_comparison_indicator(stats1['witherKills'], stats2['witherKills'], 'Wither Kills')
        + add_comparison_indicator(stats1['deaths'], stats2['deaths'], 'Deaths')
    )

    # Ratios column
    ratios_column = (
        add_comparison_indicator(stats1['kdRatio'], stats2['kdRatio'], 'K/D', is_ratio=True)
        + add_comparison_indicator(stats1['kdNoFinalsRatio'], stats2['kdNoFinalsRatio'], 'K/D (no finals)', is_ratio=True)
        + add_comparison_indicator(stats1['fdRatio'], stats2['fdRatio'], 'F/D', is_ratio=True)
        + add_comparison_indicator(stats1['wdRatio'], stats2['wdRatio'], 'WD/D', is_ratio=True)
        + add_comparison_indicator(stats1['wkRatio'], stats2['wkRatio'], 'WK/D', is_ratio=True)
        + add_comparison_indicator(stats1['arrowAccuracy'], stats2['arrowAccuracy'], 'Arrow Accuracy', is_ratio=True)
    )

    # Add the columns to the embed
    embed.add_field(name="━━━━━━ Stats ━━━━━", value=stats_column, inline=True)
    embed.add_field(name="━━━━━ Ratios ━━━━━", value=ratios_column, inline=True)

    await message.channel.send(embed=embed)
