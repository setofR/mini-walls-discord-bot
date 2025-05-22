import os
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Config:
    HYPIXEL_API_KEY: str = '30b4ce49-4035-40c9-8801-c49509e336c5'
    DISCORD_TOKEN: str = os.getenv('DISCORD_TOKEN', '')
    
    EMBED_PRIMARY_COLOR: int = 0x5865F2
    EMBED_SUCCESS_COLOR: int = 0x57F287
    EMBED_ERROR_COLOR: int = 0xED4245
    EMBED_WARNING_COLOR: int = 0xFEE75C
    
    COMMAND_PREFIX: str = '.'
    VALID_STATS: List[str] = field(default_factory=lambda: [
        'wins', 'finals', 'kills', 'deaths', 'wdmg', 'wkills', 
        'arrowhit', 'arrowshot', 'fkdr', 'kdr', 'fdr', 'wdd', 'wkd', 'aa'
    ])
    
    RANK_MAPPING: Dict[str, Dict[str, str]] = field(default_factory=lambda: {
        'ADMIN': {'name': 'ADMIN', 'color': '🔴'},
        'MODERATOR': {'name': 'MOD', 'color': '🟢'},
        'HELPER': {'name': 'HELPER', 'color': '🔵'},
        'YOUTUBER': {'name': 'YOUTUBE', 'color': '🔴'},
        'MVP_PLUS_PLUS': {'name': 'MVP++', 'color': '🟡'},
        'MVP_PLUS': {'name': 'MVP+', 'color': '🟦'},
        'MVP': {'name': 'MVP', 'color': '🟦'},
        'VIP_PLUS': {'name': 'VIP+', 'color': '🟩'},
        'VIP': {'name': 'VIP', 'color': '🟩'},
        'DEFAULT': {'name': 'NON', 'color': '⚪'}
    })
    
    COMMANDS_INFO: Dict[str, Dict[str, str]] = field(default_factory=lambda: {
        'stats': {
            'usage': '.s <username>',
            'description': 'Display detailed Mini Walls statistics for a player',
            'aliases': '.stats'
        },
        'compare': {
            'usage': '.c <username1> <username2>',
            'description': 'Compare statistics between two players',
            'aliases': '.compare, .vs'
        },
        'playercount': {
            'usage': '.pc',
            'description': 'Show current Mini Walls player count',
            'aliases': '.players'
        },
        'leaderboard': {
            'usage': '.lb <stat> [period]',
            'description': 'View leaderboards (coming soon)',
            'aliases': '.top'
        },
        'help': {
            'usage': '.help [command]',
            'description': 'Show this help message or details about a specific command',
            'aliases': '.h'
        }
    })

config = Config()