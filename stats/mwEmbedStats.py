import discord
from mwStats import calculate_ratios, get_uuid

async def create_stats_embed(username):
    stats = await calculate_ratios(username)

    if stats is None:
        return None
        
    displayname = stats.get('displayname', 'Unknown')
    rank = stats.get('rank', 'Unknown')
    
    embed = discord.Embed(title=f"[{rank}] {displayname}", color=0x2B2D31)
    
    # Format numbers with commas
    formatted_stats = {key: f'{value:,.0f}' if isinstance(value, (int, float)) else value
                       for key, value in stats.items()}

    embed.add_field(name="Stats", value=f"> Wins: `{formatted_stats['wins']}`\n"
                                        f"> Finals: `{formatted_stats['finals']}`\n"
                                        f"> Kills: `{formatted_stats['kills']}`\n"
                                        f"> Overall Kills: `{formatted_stats['killsOverall']}`\n"
                                        f"> Deaths: `{formatted_stats['deaths']}`\n"
                                        f"> Wither Damage: `{formatted_stats['witherDmg']}`\n"
                                        f"> Wither Kills: `{formatted_stats['witherKills']}`\n"
                                        f"> Arrows Hit: `{formatted_stats['arrowsHit']}`\n"
                                        f"> Arrows Shot: `{formatted_stats['arrowsShot']}`", inline=True)

    # Use f-string directly for the "Ratios" field value
    embed.add_field(name="Ratios", value=f"> K/D: `{stats.get('kdRatio', 0):.2f}`\n"
                                        f"> K/D (no finals): `{stats.get('kdNoFinalsRatio', 0):.2f}`\n"
                                        f"> F/D: `{stats.get('fdRatio', 0):.2f}`\n"
                                        f"> WD/D: `{stats.get('wdRatio', 0):.2f}`\n"
                                        f"> WK/D: `{stats.get('wkRatio', 0):.2f}`\n"
                                        f"> Arrow Accuracy: `{stats.get('arrowAccuracy', 0):.0f}%`", inline=True)
    
    uuid = await get_uuid(username)
    embed.set_thumbnail(url=f"https://mc-heads.net/avatar/{uuid}/100/{username}.png")

    return embed
