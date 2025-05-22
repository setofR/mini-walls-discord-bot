import discord
import re
from typing import List, Tuple, Optional
from config import config
from api_client import APIClient
from embed_creator import EmbedCreator

class CommandHandler:
    def __init__(self):
        self.api_client = APIClient()
        self.embed_creator = EmbedCreator(self.api_client)
    
    async def handle_command(self, message: discord.Message) -> None:
        content = message.content.lower()
        
        # Parse command and flags
        command_info = self._parse_command(message.content)
        
        # Route to appropriate handler
        if command_info['command'] in ['s', 'stats']:
            await self._handle_stats_command(message, command_info)
        elif command_info['command'] in ['c', 'compare', 'vs']:
            await self._handle_compare_command(message, command_info)
        elif command_info['command'] in ['pc', 'players', 'playercount']:
            await self._handle_player_count_command(message)
        elif command_info['command'] in ['lb', 'top', 'leaderboard']:
            await self._handle_leaderboard_command(message)
        elif command_info['command'] in ['help', 'h']:
            await self._handle_help_command(message, command_info)
        elif content == config.COMMAND_PREFIX + 's':
            await self._send_usage_error(message, "Please provide a username. Usage: `.s <username>` or `.s <username> -ext`")
        elif content == config.COMMAND_PREFIX + 'c':
            await self._send_usage_error(message, "Please provide two usernames. Usage: `.c <username1> <username2>`")
    
    def _parse_command(self, content: str) -> dict:
        """Parse command, arguments, and flags"""
        # Remove command prefix
        content = content[1:].strip()
        
        # Split into parts
        parts = content.split()
        
        if not parts:
            return {'command': '', 'args': [], 'flags': []}
        
        command = parts[0].lower()
        remaining = parts[1:] if len(parts) > 1 else []
        
        # Separate flags from arguments
        args = []
        flags = []
        
        for part in remaining:
            if part.startswith('-'):
                flags.append(part[1:].lower())  # Remove the dash
            else:
                args.append(part)
        
        return {
            'command': command,
            'args': args,
            'flags': flags
        }
    
    async def _handle_stats_command(self, message: discord.Message, command_info: dict) -> None:
        if not command_info['args']:
            await self._send_usage_error(
                message, 
                "Please provide a username. Usage: `.s <username>` or `.s <username> -ext`"
            )
            return
        
        username = command_info['args'][0]
        extended = 'ext' in command_info['flags'] or 'extended' in command_info['flags']
        
        try:
            await message.add_reaction("⏳")
        except:
            pass

        try:
            async with self.api_client:
                embed = await self.embed_creator.create_stats_embed(username, extended=extended)

            try:
                await message.remove_reaction("⏳", message.guild.me if message.guild else message.author)
            except:
                pass

            if "not found" not in (embed.description or "").lower():
                try:
                    await message.add_reaction("✅")
                except:
                    pass

            await message.channel.send(embed=embed)

        except Exception as e:
            try:
                await message.remove_reaction("⏳", message.guild.me if message.guild else message.author)
            except:
                pass

            await message.channel.send(f":x: An error occurred while fetching stats: `{str(e)}`")

    async def _send_usage_error(self, message: discord.Message, error_msg: str) -> None:
        await message.channel.send(f":warning: {error_msg}")