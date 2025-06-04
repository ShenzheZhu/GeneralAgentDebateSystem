from typing import Dict, Any, List, Type, Optional
from ..core.judge_system import JudgeSystem, JudgeMode
from .llm_judge import LLMJudge
from .voting_judge import VotingJudge
from collections import defaultdict

class JudgeFactory:
    """Judge system factory class"""
    
    @staticmethod
    def create_judge(mode: str, **kwargs) -> JudgeSystem:
        """
        Create a judge system instance
        :param mode: Judge mode ("llm" or "voting")
        :param kwargs: Other parameters including:
            - model_name: Language model name
            - prompts: Custom prompts to override defaults
        :return: Judge system instance
        """
        model_name = kwargs.get("model_name", "gpt-3.5-turbo")
        prompts = kwargs.get("prompts")
        
        if mode.lower() == "llm":
            return LLMJudge(model_name=model_name, prompts=prompts)
        elif mode.lower() == "voting":
            return VotingJudge(model_name=model_name, prompts=prompts)
        else:
            raise ValueError(f"Unsupported judge mode: {mode}")

class JudgeUtils:
    """Judge system utility class"""
    
    @staticmethod
    def normalize_scores(scores: Dict[str, float], min_score: float = 0, max_score: float = 10) -> Dict[str, float]:
        """
        Normalize scores
        :param scores: Original scores
        :param min_score: Minimum score
        :param max_score: Maximum score
        :return: Normalized scores
        """
        if not scores:
            return {}
            
        # Get the current maximum and minimum values
        current_min = min(scores.values())
        current_max = max(scores.values())
        
        # If the maximum value equals the minimum value, return the average score
        if current_max == current_min:
            return {k: (max_score + min_score) / 2 for k in scores}
            
        # Normalization calculation
        normalized = {}
        for agent_id, score in scores.items():
            normalized_score = (score - current_min) / (current_max - current_min)
            normalized_score = normalized_score * (max_score - min_score) + min_score
            normalized[agent_id] = normalized_score
            
        return normalized
        
    @staticmethod
    def calculate_ranking_changes(
        previous_scores: Dict[str, float],
        current_scores: Dict[str, float]
    ) -> Dict[str, int]:
        """
        Calculate ranking changes
        :param previous_scores: Previous round scores
        :param current_scores: Current round scores
        :return: Ranking changes {agent_id: position_change}
        """
        def get_ranking(scores: Dict[str, float]) -> Dict[str, int]:
            sorted_agents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            return {agent: rank for rank, (agent, _) in enumerate(sorted_agents, 1)}
            
        if not previous_scores or not current_scores:
            return {}
            
        prev_ranking = get_ranking(previous_scores)
        curr_ranking = get_ranking(current_scores)
        
        changes = {}
        for agent in curr_ranking:
            if agent in prev_ranking:
                # Positive value indicates an upward ranking, negative value indicates a downward ranking
                changes[agent] = prev_ranking[agent] - curr_ranking[agent]
            else:
                changes[agent] = 0
                
        return changes
        
    @staticmethod
    def merge_judge_decisions(decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge multiple judge decisions
        :param decisions: Decision list
        :return: Merged decisions
        """
        if not decisions:
            return {}
            
        # Merge scores
        all_scores = defaultdict(list)
        for decision in decisions:
            scores = decision.get("scores", {})
            for agent_id, score in scores.items():
                all_scores[agent_id].append(score)
                
        # Calculate average scores
        merged_scores = {
            agent_id: sum(scores) / len(scores)
            for agent_id, scores in all_scores.items()
        }
        
        # Find the agent with the highest score
        best_agent = max(merged_scores.items(), key=lambda x: x[1])
        
        return {
            "decision": f"Agent {best_agent[0]} performed best overall",
            "scores": merged_scores,
            "best_agent": best_agent[0],
            "best_score": best_agent[1],
            "individual_decisions": decisions
        } 