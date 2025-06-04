from typing import Dict, Any, List, Type, Optional, Union
from ..core.agent_base import AgentBase
from .single_agent import SingleAgent
from .dual_agent import DualAgent
from .multi_agent import MultiAgent
from ..core.message import Message

class AgentFactory:
    """Agent factory class"""
    
    @staticmethod
    def create_agent(
        mode: str,
        agent_id: str,
        question: str,
        background_config: Optional[Union[Dict[str, str], Dict[str, Dict[str, str]], List[Dict[str, str]]]] = None,
        **kwargs
    ) -> AgentBase:
        """
        Create Agent instance
        :param mode: Agent mode ("single", "dual", or "multi")
        :param agent_id: Agent ID
        :param question: Question to solve (with ground truth)
        :param background_config: Background configuration(s)
            For single agent: Dict with {"category": "academic", "role": "professor"}
            For dual agent: Dict with role assignments
                Example: {
                    "solver": {"category": "professional", "role": "engineer"},
                    "critic": {"category": "academic", "role": "professor"}
                }
            For multi agent: List of background configs for each agent
                Example: [
                    {"category": "academic", "role": "professor"},
                    {"category": "creative", "role": "philosopher"},
                    {"category": "professional", "role": "engineer"}
                ]
        :param kwargs: Other parameters including:
            - model_name: Language model name
            - role: Role for dual agent ("solver" or "critic")
            - agent_index: Index for multi agent
            - prompts: Custom prompts to override defaults
            - prompt_config_path: Path to custom prompt config file
        :return: Agent instance
        """
        model_name = kwargs.get("model_name", "gpt-3.5-turbo")
        prompts = kwargs.get("prompts")
        prompt_config_path = kwargs.get("prompt_config_path")
        
        if mode.lower() == "single":
            return SingleAgent(
                agent_id=agent_id,
                question=question,
                model_name=model_name,
                prompts=prompts,
                prompt_config_path=prompt_config_path,
                background_config=background_config
            )
            
        elif mode.lower() == "dual":
            role = kwargs.get("role")
            if not role:
                raise ValueError("Role (solver/critic) must be specified for dual agent mode")
            if role not in ["solver", "critic"]:
                raise ValueError("Role must be either 'solver' or 'critic'")
                
            # Validate background config for dual agent
            if background_config and not isinstance(background_config, dict):
                raise ValueError("Background config for dual agent must be a dictionary with 'solver' and 'critic' keys")
            if background_config and not all(k in background_config for k in ["solver", "critic"]):
                raise ValueError("Background config for dual agent must contain both 'solver' and 'critic' configurations")
                
            return DualAgent(
                agent_id=agent_id,
                question=question,
                role=role,
                model_name=model_name,
                prompts=prompts,
                prompt_config_path=prompt_config_path,
                background_config=background_config
            )
            
        elif mode.lower() == "multi":
            agent_index = kwargs.get("agent_index")
            if agent_index is None:
                raise ValueError("Agent index must be specified for multi agent mode")
                
            # Validate background config for multi agent
            if background_config and not isinstance(background_config, list):
                raise ValueError("Background config for multi agent must be a list of configurations")
            if background_config and not (0 <= agent_index < len(background_config)):
                raise ValueError(f"Agent index {agent_index} is out of range for the provided background configurations")
                
            return MultiAgent(
                agent_id=agent_id,
                question=question,
                agent_index=agent_index,
                model_name=model_name,
                prompts=prompts,
                prompt_config_path=prompt_config_path,
                background_config=background_config
            )
            
        else:
            raise ValueError(f"Unsupported agent mode: {mode}")
            
class AgentManager:
    """Agent manager class"""
    
    def __init__(self):
        self.agents: Dict[str, AgentBase] = {}
        
    def add_agent(self, agent: AgentBase) -> None:
        """Add Agent"""
        self.agents[agent.agent_id] = agent
        
    def remove_agent(self, agent_id: str) -> None:
        """Remove Agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            
    def get_agent(self, agent_id: str) -> Optional[AgentBase]:
        """Get Agent"""
        return self.agents.get(agent_id)
        
    def get_all_agents(self) -> List[AgentBase]:
        """Get all Agents"""
        return list(self.agents.values())
        
    def get_agent_states(self) -> Dict[str, Dict[str, Any]]:
        """Get all Agent states"""
        return {
            agent_id: agent.get_state()
            for agent_id, agent in self.agents.items()
        }
        
    def get_solution_summaries(self) -> Dict[str, Dict[str, Any]]:
        """Get all Agent solution summaries"""
        return {
            agent_id: agent.get_debate_summary()
            for agent_id, agent in self.agents.items()
        }
        
    def broadcast_message(self, message: Message) -> None:
        """Broadcast message to all Agents"""
        for agent in self.agents.values():
            if agent.agent_id != message.sender:
                agent.process_message(message)
                
    def clear_all_history(self) -> None:
        """Clear all Agent history"""
        for agent in self.agents.values():
            agent.clear_history()
            
class AgentUtils:
    """Agent utility class"""
    
    @staticmethod
    def create_solution_group(
        mode: str,
        question: str,
        config: Dict[str, Any]
    ) -> AgentManager:
        """
        Create solution group
        :param mode: Solution mode
        :param question: Question to solve
        :param config: Configuration information including:
            - model_name: Language model name
            - expertises: List of expertises for multi agent mode
            - prompts: Custom prompts for each agent
        :return: AgentManager instance
        """
        manager = AgentManager()
        
        if mode == "single":
            # Create a single Agent
            agent = AgentFactory.create_agent(
                mode="single",
                agent_id="agent_1",
                question=question,
                **config
            )
            manager.add_agent(agent)
            
        elif mode == "dual":
            # Create solver and critic
            solver = AgentFactory.create_agent(
                mode="dual",
                agent_id="solver",
                question=question,
                role="solver",
                **config
            )
            critic = AgentFactory.create_agent(
                mode="dual",
                agent_id="critic",
                question=question,
                role="critic",
                **config
            )
            manager.add_agent(solver)
            manager.add_agent(critic)
            
        elif mode == "multi":
            # Create multiple expert Agents
            expertises = config.get("expertises", [])
            if not expertises:
                raise ValueError("Expertises must be specified for multi agent mode")
                
            for i, expertise in enumerate(expertises, 1):
                agent = AgentFactory.create_agent(
                    mode="multi",
                    agent_id=f"expert_{i}",
                    question=question,
                    expertise=expertise,
                    **config
                )
                manager.add_agent(agent)
                
        else:
            raise ValueError(f"Unsupported solution mode: {mode}")
            
        return manager 