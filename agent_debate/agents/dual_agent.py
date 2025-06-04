from typing import Dict, Any, Optional
from ..core.agent_base import AgentBase
from ..core.message import Message
from ..models.language_model import LanguageModel
from ..config.prompt_loader import PromptLoader

class DualAgent(AgentBase):
    """Dual Agent that performs debate through solver-critic interaction"""
    
    def __init__(self, agent_id: str, question: str, role: str, model_name: str = "gpt-3.5-turbo", prompts: Optional[Dict[str, str]] = None, prompt_config_path: Optional[str] = None, background_config: Optional[Dict[str, Dict[str, str]]] = None):
        """
        Initialize dual agent
        :param agent_id: Agent ID
        :param question: Question to solve (with ground truth)
        :param role: Role ("solver" or "critic")
        :param model_name: Language model name
        :param prompts: Custom prompts to override defaults
        :param prompt_config_path: Path to custom prompt config file
        :param background_config: Background configuration for both roles
            Example: {
                "solver": {"category": "professional", "role": "engineer"},
                "critic": {"category": "academic", "role": "professor"}
            }
        """
        super().__init__(agent_id, question)
        self.llm = LanguageModel(model_name)
        self.role = role
        self.opponent_id: Optional[str] = None
        self.last_opponent_message: Optional[Message] = None
        
        # Initialize prompt loader
        self.prompt_loader = PromptLoader(prompt_config_path, background_config)
        self.prompts = prompts or self.prompt_loader.get_dual_agent_prompts(role)
        
        # Set system prompt
        if "system" in self.prompts:
            self.llm.get_response(self.prompts["system"])
        
    def process_message(self, message: Message) -> None:
        """Record message and update opponent info"""
        self.add_to_history(message)
        
        # Record opponent ID and message
        if message.sender != self.agent_id:
            self.opponent_id = message.sender
            self.last_opponent_message = message
        
    def generate_response(self, round_number: int, receiver: str) -> Message:
        """Generate response based on round number and role"""
        if round_number == 1:
            return self._initial_response(round_number, receiver)
        return self._debate_response(round_number, receiver)
        
    def _initial_response(self, round_number: int, receiver: str) -> Message:
        """First round: Initial solution proposal or preparation for critique"""
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
        
    def _debate_response(self, round_number: int, receiver: str) -> Message:
        """Subsequent rounds: Respond to opponent's message"""
        if not self.last_opponent_message:
            return self._initial_response(round_number, receiver)
            
        prompt = self.prompt_loader.format_prompt(
            self.prompts["response"],
            question=self.debate_topic,
            previous_message=self.last_opponent_message.content
        )
            
        response = self.llm.get_response(prompt)
        
        return self.create_message(
            content=response,
            receiver=receiver,
            round_number=round_number
        )
        
    def get_final_answer(self) -> str:
        """Get the final answer"""
        # If the role is solver, return the last message
        if self.role == "solver":
            return self.history[-1].content if self.history else "No answer generated yet"
            
        # If the role is critic, return the last message from the solver
        if self.opponent_id:
            solver_messages = [msg for msg in self.history if msg.sender == self.opponent_id]
            return solver_messages[-1].content if solver_messages else "No solver answer available"
            
        return "No answer available" 