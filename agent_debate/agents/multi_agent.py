from typing import Dict, Any, Set, Optional, List
from ..core.agent_base import AgentBase
from ..core.message import Message
from ..models.language_model import LanguageModel
from ..config.prompt_loader import PromptLoader

class MultiAgent(AgentBase):
    """Multi Agent that participates in collaborative problem-solving"""
    
    def __init__(self, agent_id: str, question: str, agent_index: int, model_name: str = "gpt-3.5-turbo", prompts: Optional[Dict[str, str]] = None, prompt_config_path: Optional[str] = None, background_config: Optional[List[Dict[str, str]]] = None):
        """
        Initialize multi agent
        :param agent_id: Agent ID
        :param question: Question to solve (with ground truth)
        :param agent_index: Index of this agent in the multi-agent setup
        :param model_name: Language model name
        :param prompts: Custom prompts to override defaults
        :param prompt_config_path: Path to custom prompt config file
        :param background_config: List of background configurations for all agents
        """
        super().__init__(agent_id, question)
        self.llm = LanguageModel(model_name)
        self.agent_index = agent_index
        self.other_agents: Set[str] = set()
        self.last_round_messages: List[Message] = []
        
        # Initialize prompt loader
        self.prompt_loader = PromptLoader(prompt_config_path, background_config)
        self.prompts = prompts or self.prompt_loader.get_multi_agent_prompts(agent_index)
        
        # Set system prompt
        if "system" in self.prompts:
            self.llm.get_response(self.prompts["system"])
        
    def process_message(self, message: Message) -> None:
        """Record message from other agents"""
        self.add_to_history(message)
        
        # Track other agents and their messages
        if message.sender != self.agent_id:
            self.other_agents.add(message.sender)
            self.last_round_messages.append(message)
        
    def generate_response(self, round_number: int, receiver: str) -> Message:
        """Generate response based on round number"""
        if round_number == 1:
            return self._initial_response(round_number, receiver)
        return self._collaborative_response(round_number, receiver)
        
    def _initial_response(self, round_number: int, receiver: str) -> Message:
        """First round: Share initial thoughts and approach"""
        prompt = self.prompt_loader.format_prompt(
            self.prompts["initial"],
            question=self.debate_topic
        )
            
        response = self.llm.get_response(prompt)
        
        return self.create_message(
            content=response,
            receiver=receiver,
            round_number=round_number
        )
        
    def _collaborative_response(self, round_number: int, receiver: str) -> Message:
        """Subsequent rounds: Build on others' contributions"""
        # Format previous contributions
        other_contributions = "\n\n".join([
            f"Agent {msg.sender}:\n{msg.content}"
            for msg in self.last_round_messages
        ])
        
        prompt = self.prompt_loader.format_prompt(
            self.prompts["collaborative"],
            question=self.debate_topic,
            other_contributions=other_contributions
        )
            
        response = self.llm.get_response(prompt)
        
        # Clear last round messages for next round
        self.last_round_messages = []
        
        return self.create_message(
            content=response,
            receiver=receiver,
            round_number=round_number
        )
        
    def get_final_answer(self) -> str:
        """Get the final answer from the last message"""
        return self.history[-1].content if self.history else "No answer generated yet" 