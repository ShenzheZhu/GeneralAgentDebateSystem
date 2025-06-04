import json
import unittest
from pathlib import Path
from typing import List, Dict

from agent_debate.agents.agent_factory import AgentFactory, AgentManager, AgentUtils
from agent_debate.core.debate_manager import DebateManager
from agent_debate.judges.llm_judge import LLMJudge
from agent_debate.models.language_model import LanguageModel

class TestGSM8KDebate(unittest.TestCase):
    def setUp(self):
        self.model_name = "deepseek-chat"
        self.dataset_path = Path("dataset/gsm8k_mini.jsonl")
        self.rounds = 2
        self.judge = LLMJudge(model_name=self.model_name)
        
        # Load dataset
        self.questions = []
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                self.questions.append({
                    'question': data['question'],
                    'answer': data['answer']
                })
                
    def test_single_agent(self):
        print("\nTesting Single Agent Debate...")
        results = []
        
        for q in self.questions:
            # Create debate manager
            debate_manager = DebateManager(
                topic=q['question'],
                total_rounds=self.rounds,
                judge_system=self.judge
            )
            
            # Create single agent
            agent = AgentFactory.create_agent(
                mode="single",
                agent_id="agent_1",
                question=q['question'],
                model_name=self.model_name
            )
            
            # Add agent to manager
            debate_manager.register_agent(agent)
            
            # Run debate
            debate_result = debate_manager.start_debate()
            
            # Record results
            results.append({
                'question': q['question'],
                'expected': q['answer'],
                'result': debate_result
            })
            
            print(f"Question: {q['question']}")
            print(f"Expected: {q['answer']}")
            print(f"Final hypothesis: {debate_result['final_hypothesis']}\n")
            
        return results
        
    def test_dual_agent(self):
        print("\nTesting Dual Agent Debate...")
        results = []
        
        for q in self.questions:
            # Create debate manager
            debate_manager = DebateManager(
                topic=q['question'],
                total_rounds=self.rounds,
                judge_system=self.judge
            )
            
            # Create solver and critic agents
            solver = AgentFactory.create_agent(
                mode="dual",
                agent_id="solver",
                question=q['question'],
                role="solver",
                model_name=self.model_name
            )
            
            critic = AgentFactory.create_agent(
                mode="dual",
                agent_id="critic",
                question=q['question'],
                role="critic",
                model_name=self.model_name
            )
            
            # Add agents to manager
            debate_manager.register_agent(solver)
            debate_manager.register_agent(critic)
            
            # Run debate
            debate_result = debate_manager.start_debate()
            
            # Record results
            results.append({
                'question': q['question'],
                'expected': q['answer'],
                'result': debate_result
            })
            
            print(f"Question: {q['question']}")
            print(f"Expected: {q['answer']}")
            print(f"Final solution: {debate_result['final_solution']}\n")
            
        return results
        
    def test_multi_agent(self):
        print("\nTesting Multi Agent Debate...")
        results = []
        
        # Define expertise areas for math problem solving
        expertises = [
            "mathematical_reasoning",
            "numerical_computation",
            "problem_decomposition",
            "solution_verification"
        ]
        
        for q in self.questions:
            # Create debate manager
            debate_manager = DebateManager(
                topic=q['question'],
                total_rounds=self.rounds,
                judge_system=self.judge
            )
            
            # Create multiple expert agents
            for i, expertise in enumerate(expertises, 1):
                agent = AgentFactory.create_agent(
                    mode="multi",
                    agent_id=f"expert_{i}",
                    question=q['question'],
                    expertise=expertise,
                    model_name=self.model_name
                )
                debate_manager.register_agent(agent)
                
            # Run debate
            debate_result = debate_manager.start_debate()
            
            # Record results
            results.append({
                'question': q['question'],
                'expected': q['answer'],
                'result': debate_result
            })
            
            print(f"Question: {q['question']}")
            print(f"Expected: {q['answer']}")
            print(f"Final consensus: {debate_result['final_consensus']}\n")
            
        return results
        
    def test_all_modes(self):
        """Run all test modes and compare results"""
        single_results = self.test_single_agent()
        dual_results = self.test_dual_agent()
        multi_results = self.test_multi_agent()
        
        # Compare results
        print("\nResults Summary:")
        print("=" * 50)
        for i, q in enumerate(self.questions):
            print(f"\nQuestion {i+1}: {q['question']}")
            print(f"Expected Answer: {q['answer']}")
            print(f"Single Agent: {single_results[i]['result']['final_hypothesis']}")
            print(f"Dual Agent: {dual_results[i]['result']['final_solution']}")
            print(f"Multi Agent: {multi_results[i]['result']['final_consensus']}")
            print("-" * 50)
            
if __name__ == '__main__':
    unittest.main() 