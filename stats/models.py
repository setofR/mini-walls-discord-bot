from dataclasses import dataclass
from typing import Optional
import time

@dataclass
class PlayerStats:
    displayname: str
    rank: str
    wins: int
    finals: int
    kills: int
    kills_overall: int
    deaths: int
    wither_damage: int
    wither_kills: int
    arrows_hit: int
    arrows_shot: int
    first_login: Optional[int] = None
    last_login: Optional[int] = None
    
    @property
    def kd_ratio(self) -> float:
        return round(self.kills_overall / max(self.deaths, 1), 2)
    
    @property
    def kd_no_finals_ratio(self) -> float:
        return round(self.kills / max(self.deaths, 1), 2)
    
    @property
    def fd_ratio(self) -> float:
        return round(self.finals / max(self.deaths, 1), 2)
    
    @property
    def wd_ratio(self) -> float:
        return round(self.wither_damage / max(self.deaths, 1), 0)
    
    @property
    def wk_ratio(self) -> float:
        return round(self.wither_kills / max(self.deaths, 1), 2)
    
    @property
    def arrow_accuracy(self) -> float:
        return round((self.arrows_hit / max(self.arrows_shot, 1)) * 100, 1)
    
    @property
    def wins_per_death(self) -> float:
        return round(self.wins / max(self.deaths, 1), 2)
    
    @property
    def average_wither_damage(self) -> float:
        return round(self.wither_damage / max(self.wins, 1), 0)
