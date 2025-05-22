import discord
from typing import Optional, List
from datetime import datetime
from models import PlayerStats
from config import config
from api_client import APIClient

class EmbedCreator:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
    
    async def create_stats_embed(self, username: str) -> Optional[discord.Embed]:
        try:
            stats = await self.api_client.get_player_stats(username)
            if not stats:
                return self._create_error_embed(f"Player '{username}' not found or has no Mini Walls stats")
            
            rank_info = config.RANK_MAPPING.get(stats.rank, config.RANK_MAPPING['DEFAULT'])
            
            # Embed with only clean stat list
            embed = discord.Embed(
                title=f"{rank_info['name']} {stats.displayname}",
                description="Mini Walls Stats",
                color=self._get_rank_color(stats.rank),
                timestamp=datetime.utcnow()
            )

            # Head icon
            uuid = await self.api_client.get_uuid(username)
            if uuid:
                embed.set_thumbnail(url=f"https://mc-heads.net/avatar/{uuid}/128")
            
            # Simple stat list
            stat_lines = [
                f"🏆 Wins: `{stats.wins:,}`",
                f"⚔️ Kills: `{stats.kills:,}`",
                f"💀 Finals: `{stats.finals:,}`",
                f"📈 K/D Ratio: `{stats.kd_ratio}`",
                f"🔪 Final K/D: `{stats.fd_ratio}`",
                f"🎯 Arrow Accuracy: `{stats.arrow_accuracy}%`",
                f"🐉 Wither Kills: `{stats.wither_kills:,}`",
                f"💥 Wither Damage: `{stats.wither_damage:,}`",
                f"📊 Wins per Death: `{stats.wins_per_death}`"
            ]
            embed.add_field(name="📋 Stats", value="\n".join(stat_lines), inline=False)
            
            embed.set_footer(
                text="Mini Walls • Powered by Hypixel API",
                icon_url="https://hypixel.net/styles/hypixel-v2/images/favicon.ico"
            )
            
            return embed

        except Exception as e:
            return self._create_error_embed(f"Error fetching stats: {str(e)}")
    
    def _add_extended_stats(self, embed: discord.Embed, stats: PlayerStats):
        # Advanced ratios
        advanced_ratios = (
            f"Wither K/D: {stats.wk_ratio}  "
            f"Wither Dmg/Death: {stats.wd_ratio:,.0f}  "
            f"No-Final K/D: {stats.kd_no_finals_ratio}  "
            f"Kills per Win: {(stats.kills / max(stats.wins, 1)):.2f}  "
            f"Finals per Win: {(stats.finals / max(stats.wins, 1)):.2f}"
        )
        
        # Detailed combat analysis
        hit_rate = (stats.arrows_hit / max(stats.arrows_shot, 1)) * 100
        combat_analysis = (
            f"Projectile Efficiency - Hit Rate: {hit_rate:.1f}%  "
            f"Shots per Kill: {(stats.arrows_shot / max(stats.kills, 1)):.1f}  "
            f"Hits per Kill: {(stats.arrows_hit / max(stats.kills, 1)):.1f}  "
            f"Wither Performance - Damage per Kill: {(stats.wither_damage / max(stats.wither_kills, 1)):,.0f}  "
            f"Kill Efficiency: {(stats.wither_kills / max(stats.kills, 1) * 100):.1f}%"
        )
        
        # Game impact metrics
        impact_score = self._calculate_impact_score(stats)
        consistency = self._calculate_consistency_score(stats)
        
        game_impact = (
            f"Impact Score: {impact_score}/100 {self._get_impact_emoji(impact_score)}  "
            f"Consistency: {consistency}/100 {self._get_consistency_emoji(consistency)}  "
            f"Versatility: {self._get_versatility_rating(stats)}  "
            f"Playstyle: {self._determine_playstyle(stats)}"
        )
        
        embed.add_field(name="📊 Advanced Ratios", value=advanced_ratios, inline=True)
        embed.add_field(name="🔬 Combat Analysis", value=combat_analysis, inline=True)
        embed.add_field(name="🎮 Game Impact", value=game_impact, inline=False)
    
    async def create_comparison_embed(self, username1: str, username2: str) -> Optional[discord.Embed]:
        try:
            stats1 = await self.api_client.get_player_stats(username1)
            stats2 = await self.api_client.get_player_stats(username2)
            
            if not stats1:
                return self._create_error_embed(f"Player '{username1}' not found")
            if not stats2:
                return self._create_error_embed(f"Player '{username2}' not found")
            
            # Determine overall winner
            comparison_results = self._calculate_comparison_winner(stats1, stats2)
            winner_name = stats1.displayname if comparison_results['p1_wins'] > comparison_results['p2_wins'] else stats2.displayname
            
            embed = discord.Embed(
                title=f"⚔️ Battle Analysis",
                description=f"**{stats1.displayname}** vs **{stats2.displayname}**",
                color=config.EMBED_PRIMARY_COLOR,
                timestamp=datetime.utcnow()
            )
            
            # Head-to-head overview
            overview = (
                f"🏆 Winner: {winner_name}  "
                f"({comparison_results['p1_wins']}-{comparison_results['p2_wins']}-{comparison_results['ties']})  "
                f"📊 Categories: {comparison_results['p1_wins'] + comparison_results['p2_wins'] + comparison_results['ties']}"
            )
            embed.add_field(name="🥊 Battle Results", value=overview, inline=False)
            
            # Core stats comparison with visual indicators
            core_stats = self._create_visual_comparison([
                ("Wins", stats1.wins, stats2.wins, "🏆"),
                ("Finals", stats1.finals, stats2.finals, "⚔️"),
                ("K/D Ratio", stats1.kd_ratio, stats2.kd_ratio, "📊"),
                ("Final K/D", stats1.fd_ratio, stats2.fd_ratio, "💀"),
            ], stats1.displayname[:8], stats2.displayname[:8])
            
            performance_stats = self._create_visual_comparison([
                ("Arrow Acc", stats1.arrow_accuracy, stats2.arrow_accuracy, "🎯", "%"),
                ("Win Rate", stats1.wins_per_death, stats2.wins_per_death, "📈"),
                ("Wither Dmg/G", stats1.average_wither_damage, stats2.average_wither_damage, "🐉"),
                ("Impact", self._calculate_impact_score(stats1), self._calculate_impact_score(stats2), "⚡"),
            ], stats1.displayname[:8], stats2.displayname[:8])
            
            embed.add_field(name="📊 Core Performance", value=core_stats, inline=True)
            embed.add_field(name="🎯 Advanced Metrics", value=performance_stats, inline=True)
            
            # Strengths and weaknesses analysis
            analysis = self._create_player_analysis(stats1, stats2)
            embed.add_field(name="🔍 Tactical Analysis", value=analysis, inline=False)
            
            embed.set_footer(text="Mini Walls • Head-to-Head Comparison")
            return embed
            
        except Exception as e:
            return self._create_error_embed(f"Error creating comparison: {str(e)}")
    
    async def create_player_count_embed(self) -> Optional[discord.Embed]:
        try:
            player_count = await self.api_client.get_mini_walls_player_count()
            if player_count is None:
                return self._create_error_embed("Failed to retrieve player count")
            
            # Enhanced status determination
            if player_count >= 150:
                status = "🟢 Peak Hours"
                color = config.EMBED_SUCCESS_COLOR
                description = "Perfect time to play! Lots of active players."
            elif player_count >= 100:
                status = "🟡 High Activity"
                color = config.EMBED_SUCCESS_COLOR
                description = "Great activity level with quick matchmaking."
            elif player_count >= 50:
                status = "🟠 Moderate Activity"
                color = config.EMBED_WARNING_COLOR
                description = "Somewhat active, might experience longer queues."
            else:
                status = "🔴 Low Activity"
                color = config.EMBED_ERROR_COLOR
                description = "Low player activity, matchmaking may be slow."
            
            embed = discord.Embed(
                title="📈 Mini Walls Player Count",
                description=f"Current players: **{player_count:,}**\nStatus: {status}\n{description}",
                color=color,
                timestamp=datetime.utcnow()
            )
            
            embed.set_footer(text="Powered by Hypixel API", icon_url="https://hypixel.net/styles/hypixel-v2/images/favicon.ico")
            
            return embed
        
        except Exception as e:
            return self._create_error_embed(f"Error fetching player count: {str(e)}")
    
    # Helper and utility methods
    
    def _create_error_embed(self, message: str) -> discord.Embed:
        return discord.Embed(title="Error", description=message, color=config.EMBED_ERROR_COLOR)
    
    def _get_rank_color(self, rank: str) -> int:
        # Map rank string to discord.Color
        rank_colors = {
            "DEFAULT": discord.Color.light_grey(),
            "VIP": discord.Color.green(),
            "VIP_PLUS": discord.Color.green(),
            "MVP": discord.Color.blue(),
            "MVP_PLUS": discord.Color.purple(),
            "ADMIN": discord.Color.red(),
            # Add other ranks as necessary
        }
        return rank_colors.get(rank, discord.Color.light_grey())
    
    def _calculate_performance_tier(self, stats: PlayerStats) -> str:
        # Simple tier calculation based on K/D ratio
        kd = stats.kd_ratio
        if kd >= 3.0:
            return "Diamond 🏆"
        elif kd >= 2.0:
            return "Gold 🥇"
        elif kd >= 1.0:
            return "Silver 🥈"
        else:
            return "Bronze 🥉"
    
    def _calculate_impact_score(self, stats: PlayerStats) -> int:
        # Placeholder calculation
        score = int(stats.kd_ratio * 20 + stats.wins_per_death * 10)
        return min(score, 100)
    
    def _get_impact_emoji(self, score: int) -> str:
        if score > 80:
            return "🔥"
        elif score > 50:
            return "⚡"
        else:
            return "💤"
    
    def _calculate_consistency_score(self, stats: PlayerStats) -> int:
        # Placeholder: consistency based on games played and win rate
        return min(int(stats.wins / max(stats.games_played, 1) * 100), 100)
    
    def _get_consistency_emoji(self, score: int) -> str:
        if score > 75:
            return "👍"
        elif score > 50:
            return "👌"
        else:
            return "🤷"
    
    def _get_versatility_rating(self, stats: PlayerStats) -> str:
        # Placeholder versatility rating
        if stats.kd_ratio > 2 and stats.arrow_accuracy > 50:
            return "High 🎯"
        elif stats.kd_ratio > 1:
            return "Moderate ⚔️"
        else:
            return "Low 🐢"
    
    def _determine_playstyle(self, stats: PlayerStats) -> str:
        # Based on ratios, determine playstyle
        if stats.kd_ratio > 2:
            return "Aggressive"
        elif stats.wins_per_death > 0.5:
            return "Balanced"
        else:
            return "Defensive"
    
    def _calculate_comparison_winner(self, stats1: PlayerStats, stats2: PlayerStats) -> dict:
        categories = ['wins', 'finals', 'kd_ratio', 'fd_ratio']
        p1_wins = 0
        p2_wins = 0
        ties = 0
        
        for cat in categories:
            val1 = getattr(stats1, cat, 0)
            val2 = getattr(stats2, cat, 0)
            if val1 > val2:
                p1_wins += 1
            elif val2 > val1:
                p2_wins += 1
            else:
                ties += 1
        return {'p1_wins': p1_wins, 'p2_wins': p2_wins, 'ties': ties}
    
    def _create_visual_comparison(self, stats: List[tuple], label1: str, label2: str) -> str:
        lines = []
        for name, val1, val2, icon, suffix in [(s[0], s[1], s[2], s[3], s[4] if len(s) > 4 else '') for s in stats]:
            if val1 > val2:
                line = f"{icon} **{label1}** {name}: {val1}{suffix} | {val2}{suffix} {label2}"
            elif val2 > val1:
                line = f"{icon} {label1} {name}: {val1}{suffix} | **{val2}{suffix} {label2}**"
            else:
                line = f"{icon} {label1} {name}: {val1}{suffix} | {val2}{suffix} {label2}"
            lines.append(line)
        return "\n".join(lines)
    
    def _create_player_analysis(self, stats1: PlayerStats, stats2: PlayerStats) -> str:
        # Example analysis, can be customized
        analysis = []
        if stats1.kd_ratio > stats2.kd_ratio:
            analysis.append(f"{stats1.displayname} has superior combat skills.")
        elif stats2.kd_ratio > stats1.kd_ratio:
            analysis.append(f"{stats2.displayname} has superior combat skills.")
        else:
            analysis.append("Both players have similar combat skills.")
        
        if stats1.wins > stats2.wins:
            analysis.append(f"{stats1.displayname} has more wins.")
        elif stats2.wins > stats1.wins:
            analysis.append(f"{stats2.displayname} has more wins.")
        else:
            analysis.append("Both players have equal wins.")
        
        return " ".join(analysis)