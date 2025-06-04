from dataclasses import dataclass, field
from typing import Dict, Any
from datetime import datetime
from enum import Enum

class MessageType(Enum):
    """Message type enumeration"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    BROADCAST = "broadcast"

@dataclass
class Message:
    """Base message class for encapsulating all communication content"""
    content: str
    sender: str
    receiver: str
    round_number: int
    message_type: MessageType = field(default=MessageType.ASSISTANT)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format"""
        return {
            "content": self.content,
            "sender": self.sender,
            "receiver": self.receiver,
            "round_number": self.round_number,
            "message_type": self.message_type.value,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message object from dictionary"""
        data = data.copy()
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if 'message_type' in data:
            data['message_type'] = MessageType(data['message_type'])
        return cls(**data)

    def __str__(self) -> str:
        """Return string representation of the message"""
        return f"[Round {self.round_number}] {self.sender} -> {self.receiver}: {self.content}" 