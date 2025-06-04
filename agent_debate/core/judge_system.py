from abc import ABC, abstractmethod
from typing import Dict, Any, List
from .message import Message
from enum import Enum

class JudgeMode(Enum):
    LLM = "llm"
    VOTING = "voting"

class JudgeSystem(ABC):
    """Base class for judge system, only used in multi-agent setting"""
    
    def __init__(self, mode: JudgeMode):
        self.mode = mode
        self.final_judgment: str = ""
        
    @abstractmethod
    def make_final_judgment(self, all_messages: List[Message]) -> str:
        """Make final judgment based on all debate messages"""
        pass
        
    def get_final_answer(self) -> str:
        """Get the final answer"""
        return self.final_judgment or "No judgment made yet" 