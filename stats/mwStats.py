import requests
import locale

locale.setlocale(locale.LC_ALL, '')

async def get_uuid(username):
    api_url = f'https://api.mojang.com/users/profiles/minecraft/{username}'
    response = requests.get(api_url)

    if response.status_code == 200:
        return response.json().get('id')
    else:
        return None

async def fetch_stats(api_key, uuid):
    base_url = f'https://api.hypixel.net/player?key={api_key}&uuid={uuid.replace("-", "")}'  # Remove dashes from UUID

    try:
        response = requests.get(base_url)
        data = response.json()

        if data.get('success', False):
            return data.get('player')  # Return the entire player data
        else:
            print(f"Failed to fetch stats for {uuid}. API response: {data}")
            return None
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

async def calculate_ratios(username):
    api_key = 'c756ff14-d79f-4879-b51e-bec482eb347e'
    uuid = await get_uuid(username)
    player_data = await fetch_stats(api_key, uuid)

    if player_data is None:
        return None

    # Extracting relevant stats
    wins = int(player_data['stats']['Arcade'].get('wins_mini_walls', 0))
    finals = int(player_data['stats']['Arcade'].get('final_kills_mini_walls', 0))
    kills = int(player_data['stats']['Arcade'].get('kills_mini_walls', 0))
    killsOverall = finals + kills
    deaths = int(player_data['stats']['Arcade'].get('deaths_mini_walls', 0))
    wither_damage = int(player_data['stats']['Arcade'].get('wither_damage_mini_walls', 0))
    wither_kills = int(player_data['stats']['Arcade'].get('wither_kills_mini_walls', 0))
    arrows_hit = int(player_data['stats']['Arcade'].get('arrows_hit_mini_walls', 0))
    arrows_shot = int(player_data['stats']['Arcade'].get('arrows_shot_mini_walls', 0))

    # Extract newPackageRank and displayname
    rank = player_data.get('newPackageRank', 'Unknown')
    display_name = player_data.get('displayname', 'Unknown')
    
    if rank == "MVP_PLUS":
        display_rank = "MVP+"
    elif rank == "MVP":
        display_rank = "MVP"
    elif rank == "VIP_PLUS":
        display_rank = "VIP+"
    elif rank == "VIP":
        display_rank = "VIP"
    else:
        display_rank = rank

    # Calculate ratios
    kd_ratio = killsOverall / deaths if deaths != 0 else 0
    kd_no_finals_ratio = kills / deaths if deaths != 0 else 0
    fd_ratio = finals / deaths if deaths != 0 else 0
    wd_ratio = wither_damage / deaths if deaths != 0 else 0
    wk_ratio = wither_kills / deaths if deaths != 0 else 0
    arrow_accuracy = (arrows_hit / arrows_shot) * 100 if arrows_shot != 0 else 0

    return {
        'displayname': display_name,
        'rank': display_rank,
        'wins': wins,
        'finals': finals,
        'kills': kills,
        'killsOverall': killsOverall,
        'deaths': deaths,
        'witherDmg': wither_damage,
        'witherKills': wither_kills,
        'arrowsHit': arrows_hit,
        'arrowsShot': arrows_shot,
        'kdRatio': kd_ratio,
        'kdNoFinalsRatio': kd_no_finals_ratio,
        'fdRatio': fd_ratio,
        'wdRatio': wd_ratio,
        'wkRatio': wk_ratio,
        'arrowAccuracy': arrow_accuracy,
    }
