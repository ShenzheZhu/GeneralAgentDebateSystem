from typing import Dict, Any, Optional
from ..core.agent_base import AgentBase
from ..core.message import Message
from ..models.language_model import LanguageModel
from ..config.prompt_loader import PromptLoader

class SingleAgent(AgentBase):
    """Single Agent that performs self-debate through analysis and verification"""
    
    def __init__(self, agent_id: str, question: str, model_name: str = "gpt-3.5-turbo", prompts: Optional[Dict[str, str]] = None, prompt_config_path: Optional[str] = None, background_config: Optional[Dict[str, str]] = None):
        """
        Initialize single Agent
        :param agent_id: Agent ID
        :param question: Question to solve (with ground truth)
        :param model_name: Language model name
        :param prompts: Custom prompts to override defaults
        :param prompt_config_path: Path to custom prompt config file
        :param background_config: Background configuration with category and role
            Example: {"category": "academic", "role": "professor"}
        """
        super().__init__(agent_id, question)
        self.llm = LanguageModel(model_name)
        self.current_analysis: Optional[str] = None
        
        # Initialize prompt loader
        self.prompt_loader = PromptLoader(prompt_config_path, background_config)
        self.prompts = prompts or self.prompt_loader.get_single_agent_prompts()
        
        # Set system prompt
        if "system" in self.prompts:
            self.llm.get_response(self.prompts["system"])
        
    def process_message(self, message: Message) -> None:
        """Simply record the message in history"""
        self.add_to_history(message)
        
    def generate_response(self, round_number: int, receiver: str) -> Message:
        """Generate response based on round number"""
        if round_number == 1:
            return self._initial_analysis(round_number, receiver)
        return self._verify_analysis(round_number, receiver)
        
    def _initial_analysis(self, round_number: int, receiver: str) -> Message:
        """First round: Initial analysis of the question"""
        prompt = self.prompt_loader.format_prompt(
            self.prompts["initial_analysis"],
            question=self.debate_topic
        )
            
        response = self.llm.get_response(prompt)
        self.current_analysis = response
        
        return self.create_message(
            content=response,
            receiver=receiver,
            round_number=round_number
        )
        
    def _verify_analysis(self, round_number: int, receiver: str) -> Message:
        """Second round: Verify and improve the analysis"""
        if not self.current_analysis:
            return self._initial_analysis(round_number, receiver)
            
        prompt = self.prompt_loader.format_prompt(
            self.prompts["verify_analysis"],
            question=self.debate_topic,
            previous_analysis=self.current_analysis
        )
            
        response = self.llm.get_response(prompt)
        self.current_analysis = response
        
        return self.create_message(
            content=response,
            receiver=receiver,
            round_number=round_number
        )
        
    def get_final_answer(self) -> str:
        """Get the final answer from the last message"""
        return self.history[-1].content if self.history else "No answer generated yet" 