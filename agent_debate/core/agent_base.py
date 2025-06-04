from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .debate_manager import DebateManager

from .message import Message

class AgentBase(ABC):
    """Agent base class. All specific Agents must inherit from this class."""
    
    def __init__(self, agent_id: str, debate_topic: str):
        self.agent_id = agent_id
        self.debate_topic = debate_topic
        self.history: List[Message] = []
        self.debate_manager: Optional['DebateManager'] = None
        
    def add_to_history(self, message: Message) -> None:
        """Add a message to the history"""
        self.history.append(message)
        
    def get_history(self, round_number: Optional[int] = None) -> List[Message]:
        """Get the history, optionally specifying a round number"""
        if round_number is None:
            return self.history
        return [msg for msg in self.history if msg.round_number == round_number]
        
    @abstractmethod
    def process_message(self, message: Message) -> None:
        """Process the received message"""
        pass
        
    @abstractmethod
    def generate_response(self, round_number: int, receiver: str) -> Message:
        """Generate a response message"""
        pass
        
    def register_to_debate(self, debate_manager: 'DebateManager') -> None:
        """Register to the debate manager"""
        self.debate_manager = debate_manager
        debate_manager.register_agent(self)
        
    def create_message(self, content: str, receiver: str, round_number: int) -> Message:
        """Create a new message"""
        return Message(
            content=content,
            sender=self.agent_id,
            receiver=receiver,
            round_number=round_number
        )
        
    def clear_history(self) -> None:
        """Clear the history"""
        self.history = []
        
    def __str__(self) -> str:
        return f"Agent({self.agent_id})"

    def get_final_answer(self) -> Optional[str]:
        """Get the final answer"""
        if not self.history:
            return None
        # Return the content of the last message as the final answer
        return self.history[-1].content

    def get_debate_summary(self) -> Dict[str, Any]:
        """Get the debate summary"""
        return {
            "agent_id": self.agent_id,
            "debate_topic": self.debate_topic,
            "total_messages": len(self.history),
            "final_answer": self.get_final_answer()
        } 