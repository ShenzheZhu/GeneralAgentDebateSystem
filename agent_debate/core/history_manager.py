from typing import List, Dict, Optional, Set, Any
from .message import Message
from collections import defaultdict

class HistoryManager:
    """History manager responsible for managing the conversation history"""
    
    def __init__(self):
        self.messages: List[Message] = []
        self.round_history: Dict[int, List[Message]] = {}
        self.agent_history: Dict[str, List[Message]] = defaultdict(list)
        
    def add_message(self, message: Message) -> None:
        """Add a new message to the history"""
        # Add to messages list
        self.messages.append(message)
        
        # Add to round history
        if message.round_number not in self.round_history:
            self.round_history[message.round_number] = []
        self.round_history[message.round_number].append(message)
        
        # Add to agent history
        self.agent_history[message.sender].append(message)
        if message.receiver != "all":  # If not a broadcast message
            self.agent_history[message.receiver].append(message)
            
    def get_round_history(self, round_number: int) -> List[Message]:
        """Get the history for a specific round"""
        return self.round_history.get(round_number, [])
        
    def get_agent_history(self, agent_id: str) -> List[Message]:
        """Get the history for a specific agent"""
        return self.agent_history[agent_id].copy()
        
    def get_context(self, round_number: int, window_size: int = 3) -> List[Message]:
        """Get the context for the current round (including previous rounds)"""
        context = []
        for r in range(max(1, round_number - window_size), round_number + 1):
            if r in self.round_history:
                context.extend(self.round_history[r])
        return context
        
    def get_round_summary(self, round_number: int) -> Dict[str, List[Message]]:
        """Get the summary for a specific round (grouped by agent)"""
        summary = defaultdict(list)
        if round_number in self.round_history:
            for msg in self.round_history[round_number]:
                summary[msg.sender].append(msg)
        return dict(summary)
        
    def clear(self) -> None:
        """Clear all history"""
        self.messages.clear()
        self.round_history.clear()
        self.agent_history.clear()
        
    def get_all_messages(self) -> List[Message]:
        """Get all history messages"""
        return self.messages.copy()
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get debate statistics"""
        stats = {
            "total_messages": len(self.messages),
            "messages_per_round": {
                round_num: [msg.to_dict() for msg in messages]
                for round_num, messages in self.round_history.items()
            },
            "messages_per_agent": {
                agent_id: len(messages)
                for agent_id, messages in self.agent_history.items()
            }
        }
        return stats 