from typing import Dict, Any

class JudgePromptTemplates:
    """Prompt templates for different judge types"""
    
    # LLM judge prompts
    LLM_JUDGE = {
        "system": """You are a fair and objective judge who carefully analyzes and evaluates solutions.
Your role is to:
1. Understand each perspective thoroughly
2. Compare different approaches objectively
3. Identify strengths and weaknesses
4. Make well-reasoned decisions
5. Provide clear explanations for your judgments""",
        
        "final_judgment": """Please analyze the following solutions from different perspectives and determine which solution or combination of solutions is most appropriate.

Solutions:
{answers_text}

Please:
1. Analyze each agent's unique perspective and reasoning
2. Compare the different approaches and insights
3. Determine which solution(s) have the strongest reasoning and evidence
4. If multiple solutions have merit, synthesize them into a comprehensive solution
5. Explain why the chosen solution is the most appropriate

Focus on the logical strength, completeness, and unique value of each perspective."""
    }
    
    # Voting judge prompts
    VOTING_JUDGE = {
        "system": """You are a fair and objective evaluator who analyzes solutions and votes on their effectiveness.
Your role is to:
1. Understand each perspective thoroughly
2. Evaluate solutions objectively
3. Consider diverse viewpoints
4. Make well-reasoned decisions
5. Explain your voting rationale""",
        
        "final_judgment": """Please analyze the following solutions from different perspectives and determine which solution or combination of solutions is most appropriate.

Solutions:
{answers_text}

Please:
1. Identify the unique insights in each solution
2. Compare the different approaches and perspectives
3. Determine which solution(s) have the strongest reasoning and evidence
4. If multiple solutions have merit, synthesize them into a comprehensive solution
5. Explain why the chosen solution is the most appropriate

Focus on the logical strength, completeness, and unique value of each perspective."""
    }
    
    @classmethod
    def get_llm_judge_prompts(cls) -> Dict[str, str]:
        """Get LLM judge prompts"""
        return cls.LLM_JUDGE.copy()
        
    @classmethod
    def get_voting_judge_prompts(cls) -> Dict[str, str]:
        """Get voting judge prompts"""
        return cls.VOTING_JUDGE.copy()
        
    @classmethod
    def format_prompt(cls, prompt: str, **kwargs) -> str:
        """Format prompt with provided arguments"""
        return prompt.format(**kwargs) 