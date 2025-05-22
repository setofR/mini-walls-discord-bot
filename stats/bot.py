import discord
import asyncio
import logging
from config import config
from command_handler import CommandHandler

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MiniWallsBot:
    def __init__(self):
        # Configure intents
        intents = discord.Intents.default()
        intents.message_content = True
        
        self.bot = discord.Client(intents=intents)
        self.command_handler = CommandHandler()
        self._setup_events()
    
    def _setup_events(self):
        @self.bot.event
        async def on_ready():
            logger.info(f"🤖 {self.bot.user} is now online!")
            logger.info(f"📊 Connected to {len(self.bot.guilds)} servers")
            
            # Set bot status
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name="Mini Walls stats | .help"
            )
            await self.bot.change_presence(activity=activity)
        
        @self.bot.event
        async def on_message(message):
            if message.author.bot:
                return
            
            await self._handle_message(message)
        
        @self.bot.event
        async def on_command_error(ctx, error):
            logger.error(f"Command error: {error}")
    
    async def _handle_message(self, message: discord.Message):
        content = message.content.strip()
        
        # Check if message starts with command prefix
        if not content.startswith(config.COMMAND_PREFIX):
            return
        
        # Add typing indicator for better UX
        async with message.channel.typing():
            try:
                await self.command_handler.handle_command(message)
            except Exception as e:
                logger.error(f"Error handling command: {e}")
                embed = discord.Embed(
                    title="❌ Something went wrong",
                    description="An unexpected error occurred. Please try again later.",
                    color=config.EMBED_ERROR_COLOR
                )
                await message.channel.send(embed=embed)
    
    def run(self):
        if not config.DISCORD_TOKEN:
            logger.error("❌ Discord token not found! Please set the DISCORD_TOKEN environment variable.")
            return
        
        try:
            self.bot.run(config.DISCORD_TOKEN)
        except discord.LoginFailure:
            logger.error("❌ Invalid Discord token!")
        except Exception as e:
            logger.error(f"❌ Bot startup failed: {e}")

if __name__ == "__main__":
    bot = MiniWallsBot()
    bot.run()