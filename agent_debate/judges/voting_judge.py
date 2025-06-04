from typing import Dict, Any, List, Optional
from ..core.judge_system import JudgeSystem, JudgeMode
from ..core.message import Message
from ..models.language_model import LanguageModel
from ..config.judge_prompts import JudgePromptTemplates

class VotingJudge(JudgeSystem):
    """Judge system that uses LLM to analyze and vote on expert answers"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", prompts: Optional[Dict[str, str]] = None):
        """
        Initialize voting judge
        :param model_name: Language model name
        :param prompts: Custom prompts to override defaults
        """
        super().__init__(JudgeMode.VOTING)
        self.llm = LanguageModel(model_name)
        self.prompts = prompts or JudgePromptTemplates.get_voting_judge_prompts()
        
        # Set system prompt
        if "system" in self.prompts:
            self.llm.get_response(self.prompts["system"])
        
    def make_final_judgment(self, final_messages: List[Message]) -> str:
        """Analyze final answers from all experts and select the most appropriate one"""
        # Format final answers by expert
        final_answers = {}
        for msg in final_messages:
            final_answers[msg.sender] = msg.content
            
        # Format the answers text
        answers_text = "\n\n".join([
            f"Agent {expert}:\n{answer}"
            for expert, answer in final_answers.items()
        ])
        
        # Format the prompt
        prompt = JudgePromptTemplates.format_prompt(
            self.prompts["final_judgment"],
            answers_text=answers_text
        )
        
        # Get analysis from LLM
        judgment = self.llm.get_response(prompt)
        self.final_judgment = judgment
        
        return judgment 