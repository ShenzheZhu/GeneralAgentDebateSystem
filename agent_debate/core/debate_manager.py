from typing import Dict, List, Any, Optional, Type
from .message import Message, MessageType
from .agent_base import AgentBase
from .history_manager import HistoryManager
from .round_controller import RoundController
from .judge_system import JudgeSystem, JudgeMode
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DebateManager:
    """Debate manager responsible for coordinating the entire debate process"""
    
    def __init__(self, topic: str, total_rounds: int, judge_system: JudgeSystem):
        self.topic = topic
        self.agents: Dict[str, AgentBase] = {}
        self.history_manager = HistoryManager()
        self.round_controller = RoundController(total_rounds)
        self.judge_system = judge_system
        
    def register_agent(self, agent: AgentBase) -> None:
        """Register an agent"""
        self.agents[agent.agent_id] = agent
        logger.info(f"Agent {agent.agent_id} registered to debate")
        
    def start_debate(self) -> Dict[str, Any]:
        """Start the debate"""
        logger.info(f"Starting debate on topic: {self.topic}")
        
        while self.round_controller.start_round():
            current_round = self.round_controller.get_current_round()
            logger.info(f"Starting round {current_round}")
            
            # Execute current round
            self._execute_round()
            
            # End current round
            self.round_controller.end_round()
            logger.info(f"Round {current_round} completed")
            
        # Make final judgment for multi-agent debates
        if len(self.agents) > 2:
            final_round = self.round_controller.get_current_round()
            final_messages = self.history_manager.get_round_history(final_round)
            final_judgment = self.judge_system.make_final_judgment(final_messages)
            logger.info(f"Final judgment made: {final_judgment}")
            
        # Generate debate summary
        return self._generate_final_summary()
        
    def _execute_round(self) -> None:
        """Execute a round"""
        current_round = self.round_controller.get_current_round()
        
        # If single agent mode
        if len(self.agents) == 1:
            self._execute_single_agent_round()
        # If dual agent mode
        elif len(self.agents) == 2:
            self._execute_dual_agent_round()
        # If multi agent mode
        else:
            self._execute_multi_agent_round()
            
    def _execute_single_agent_round(self) -> None:
        """Execute single agent round (self-debate)"""
        agent = list(self.agents.values())[0]
        current_round = self.round_controller.get_current_round()
        
        # Generate response
        response = agent.generate_response(current_round, agent.agent_id)
        
        # Process message
        self._process_message(response)
        
    def _execute_dual_agent_round(self) -> None:
        """Execute dual agent round"""
        agents = list(self.agents.values())
        current_round = self.round_controller.get_current_round()
        
        # Take turns speaking
        for agent in agents:
            # Determine receiver (the other agent)
            receiver = [a for a in agents if a != agent][0]
            
            # Generate response
            response = agent.generate_response(current_round, receiver.agent_id)
            
            # Process message
            self._process_message(response)
            
    def _execute_multi_agent_round(self) -> None:
        """Execute multi agent round"""
        current_round = self.round_controller.get_current_round()
        
        # Take turns speaking
        for agent in self.agents.values():
            # Generate broadcast message
            response = agent.generate_response(current_round, "all")
            
            # Process message
            self._process_message(response)
            
    def _process_message(self, message: Message) -> None:
        """Process message"""
        # Record message
        self.history_manager.add_message(message)
        self.round_controller.record_message(message.sender)
        
        # If not broadcast message, send to receiver
        if message.receiver != "all":
            receiver = self.agents.get(message.receiver)
            if receiver:
                receiver.process_message(message)
        # If broadcast message, send to all other agents
        else:
            for agent in self.agents.values():
                if agent.agent_id != message.sender:
                    agent.process_message(message)
                    
    def _generate_final_summary(self) -> Dict[str, Any]:
        """Generate debate summary"""
        final_round = self.round_controller.get_current_round()
        final_messages = self.history_manager.get_round_history(final_round)
        
        # Get final answer from each agent
        final_answers = {}
        for agent_id, agent in self.agents.items():
            final_answers[agent_id] = agent.get_final_answer()
        
        summary = {
            "topic": self.topic,
            "total_rounds": self.round_controller.total_rounds,
            "participants": list(self.agents.keys()),
            "statistics": self.history_manager.get_statistics(),
            "final_judgment": self.judge_system.get_final_answer() if len(self.agents) > 2 else None,
            "final_answers": final_answers,
            "final_round": {
                "round_number": final_round,
                "messages": [msg.to_dict() for msg in final_messages]
            }
        }
        
        logger.info("Debate completed. Generating final summary.")
        return summary
        
    def get_debate_state(self) -> Dict[str, Any]:
        """Get current debate state"""
        return {
            "topic": self.topic,
            "progress": self.round_controller.get_progress(),
            "statistics": self.history_manager.get_statistics()
        }
        
    def get_agent_states(self) -> Dict[str, Dict[str, Any]]:
        """Get states of all agents"""
        return {
            agent_id: agent.get_state()
            for agent_id, agent in self.agents.items()
        } 