from typing import Dict, Any, Optional
from datetime import datetime

class RoundController:
    """Round controller responsible for managing debate rounds"""
    
    def __init__(self, total_rounds: int):
        self.total_rounds = total_rounds
        self.current_round = 0
        self.round_start_time: Optional[datetime] = None
        self.round_statistics: Dict[int, Dict[str, Any]] = {}
        
    def start_round(self) -> bool:
        """Start a new round"""
        if self.is_final_round():
            return False
            
        self.current_round += 1
        self.round_start_time = datetime.now()
        
        self.round_statistics[self.current_round] = {
            "start_time": self.round_start_time,
            "messages_count": 0,
            "participants": set()
        }
        
        return True
        
    def end_round(self) -> None:
        """End the current round"""
        if self.current_round in self.round_statistics:
            self.round_statistics[self.current_round]["end_time"] = datetime.now()
            
    def is_final_round(self) -> bool:
        """Check if it is the final round"""
        return self.current_round > self.total_rounds
        
    def get_current_round(self) -> int:
        """Get the current round number"""
        return self.current_round
        
    def record_message(self, agent_id: str) -> None:
        """Record message statistics"""
        if self.current_round in self.round_statistics:
            self.round_statistics[self.current_round]["messages_count"] += 1
            self.round_statistics[self.current_round]["participants"].add(agent_id)
            
    def get_round_summary(self, round_number: Optional[int] = None) -> Dict[str, Any]:
        """Get the round summary"""
        if round_number is None:
            round_number = self.current_round
            
        if round_number not in self.round_statistics:
            return {}
            
        stats = self.round_statistics[round_number].copy()
        if "participants" in stats:
            stats["participants"] = list(stats["participants"])
        return stats
        
    def get_progress(self) -> Dict[str, Any]:
        """Get the debate progress information"""
        return {
            "current_round": self.current_round,
            "total_rounds": self.total_rounds,
            "remaining_rounds": self.total_rounds - self.current_round,
            "progress_percentage": (self.current_round / self.total_rounds) * 100
        } 