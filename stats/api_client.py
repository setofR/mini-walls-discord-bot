import aiohttp
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from config import config
from models import PlayerStats

class APIError(Exception):
    pass

class APIClient:
    def __init__(self):
        self.api_key = config.HYPIXEL_API_KEY
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            headers={'User-Agent': 'MiniWalls-Discord-Bot/2.0'}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_uuid(self, username: str) -> Optional[str]:
        if not self.session:
            raise APIError("API client not initialized")
            
        url = f'https://api.mojang.com/users/profiles/minecraft/{username}'
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('id')
                elif response.status == 404:
                    return None
                else:
                    raise APIError(f"Mojang API error: {response.status}")
        except asyncio.TimeoutError:
            raise APIError("Request timed out")
        except Exception as e:
            raise APIError(f"Failed to get UUID: {str(e)}")
    
    async def fetch_player_data(self, uuid: str) -> Optional[Dict[str, Any]]:
        if not self.session:
            raise APIError("API client not initialized")
            
        url = f'https://api.hypixel.net/player?key={self.api_key}&uuid={uuid.replace("-", "")}'
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        return data.get('player')
                    else:
                        raise APIError(f"Hypixel API error: {data.get('cause', 'Unknown error')}")
                else:
                    raise APIError(f"Hypixel API error: {response.status}")
        except asyncio.TimeoutError:
            raise APIError("Request timed out")
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"Failed to fetch player data: {str(e)}")
    
    async def get_player_stats(self, username: str) -> Optional[PlayerStats]:
        try:
            uuid = await self.get_uuid(username)
            if not uuid:
                return None
            
            player_data = await self.fetch_player_data(uuid)
            if not player_data:
                return None
            
            return self._parse_player_stats(player_data)
        except APIError:
            return None
    
    async def get_mini_walls_player_count(self) -> Optional[int]:
        if not self.session:
            raise APIError("API client not initialized")
            
        url = f'https://api.hypixel.net/gameCounts?key={self.api_key}'
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        games = data.get('games', {})
                        return games.get('MINI_WALLS', {}).get('players', 0)
                    else:
                        raise APIError(f"Hypixel API error: {data.get('cause', 'Unknown error')}")
                else:
                    raise APIError(f"Hypixel API error: {response.status}")
        except asyncio.TimeoutError:
            raise APIError("Request timed out")
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"Failed to get player count: {str(e)}")
    
    def _parse_player_stats(self, player_data: Dict[str, Any]) -> PlayerStats:
        arcade_stats = player_data.get('stats', {}).get('Arcade', {})
        
        # Extract basic stats
        wins = arcade_stats.get('wins_mini_walls', 0)
        finals = arcade_stats.get('final_kills_mini_walls', 0)
        kills = arcade_stats.get('kills_mini_walls', 0)
        deaths = arcade_stats.get('deaths_mini_walls', 0)
        wither_damage = arcade_stats.get('wither_damage_mini_walls', 0)
        wither_kills = arcade_stats.get('wither_kills_mini_walls', 0)
        arrows_hit = arcade_stats.get('arrows_hit_mini_walls', 0)
        arrows_shot = arcade_stats.get('arrows_shot_mini_walls', 0)
        
        # Extract rank information
        rank = self._determine_rank(player_data)
        display_name = player_data.get('displayname', 'Unknown')
        
        # Extract login times
        first_login = player_data.get('firstLogin')
        last_login = player_data.get('lastLogin')
        
        return PlayerStats(
            displayname=display_name,
            rank=rank,
            wins=wins,
            finals=finals,
            kills=kills,
            kills_overall=finals + kills,
            deaths=deaths,
            wither_damage=wither_damage,
            wither_kills=wither_kills,
            arrows_hit=arrows_hit,
            arrows_shot=arrows_shot,
            first_login=first_login,
            last_login=last_login
        )
    
    def _determine_rank(self, player_data: Dict[str, Any]) -> str:
        # Check for staff ranks first
        rank = player_data.get('rank', '').upper()
        if rank in config.RANK_MAPPING:
            return rank
        
        # Check for package ranks
        package_rank = player_data.get('newPackageRank', '').upper()
        monthly_package_rank = player_data.get('monthlyPackageRank', '').upper()
        
        # Monthly ranks take priority
        if monthly_package_rank == 'SUPERSTAR':
            return 'MVP_PLUS_PLUS'
        elif package_rank in config.RANK_MAPPING:
            return package_rank
        
        return 'DEFAULT'