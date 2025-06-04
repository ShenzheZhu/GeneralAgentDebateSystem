from pathlib import Path
import json
import os
import shutil
from datetime import datetime
from agent_debate.models.language_model import LanguageModel
from agent_debate.judges.llm_judge import LLMJudge
from agent_debate.core.debate_manager import DebateManager
from agent_debate.agents.agent_factory import AgentFactory
from agent_debate.config.prompt_loader import PromptLoader

def clean_reports_dir(output_dir: str = "debate_reports"):
    """Clean the reports directory"""
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

def save_debate_report(question_id: int, question: str, answer: str, debate_result: dict, output_dir: str = "debate_reports"):
    """Save debate report"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Build report
    report = {
        "question_id": question_id,
        "question": question,
        "ground_truth": answer,
        "timestamp": datetime.now().isoformat(),
        "debate_config": {
            "model": "deepseek-chat",
            "rounds": 2,
            "mode": debate_result.get("mode", "single_agent"),
            "participants": debate_result.get("participants", [])
        },
        "debate_history": {
            "messages": debate_result.get("messages", []),
            "rounds": debate_result.get("statistics", {}).get("messages_per_round", {}),
            "agent_summaries": debate_result.get("final_answers", {})
        },
        "final_result": {
            "final_judgment": debate_result.get("final_judgment"),
            "final_answers": debate_result.get("final_answers", {})
        }
    }
    
    # Save report
    filename = f"debate_report_q{question_id}.json"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\nDebate report saved to: {filepath}")
    return report

def run_single_agent_test(question: dict, model_name: str = "deepseek-chat", rounds: int = 2):
    """Run single agent debate test"""
    print("\n=== Testing Single Agent Debate ===")
    
    judge = LLMJudge(model_name=model_name)
    
    print(f"\nQuestion: {question['question']}")
    print(f"Expected Answer: {question['answer']}")
    
    # Create debate manager
    debate_manager = DebateManager(
        topic=question['question'],
        total_rounds=rounds,
        judge_system=judge
    )
    
    # Create single agent with academic background
    agent = AgentFactory.create_agent(
        mode="single",
        agent_id="agent_1",
        question=question['question'],
        model_name=model_name,
        background_config={
            "category": "academic",
            "role": "professor"
        }
    )
    
    # Add agent to manager
    debate_manager.register_agent(agent)
    
    # Run debate
    debate_result = debate_manager.start_debate()
    
    # Generate and save debate report
    report = save_debate_report(
        question_id=0,
        question=question['question'],
        answer=question['answer'],
        debate_result=debate_result,
        output_dir="debate_reports/single_agent"
    )
    
    print("\nDebate Summary:")
    print(f"Question: {report['question']}")
    print(f"Ground Truth: {report['ground_truth']}")
    print(f"Agent Answer: {report['final_result']['final_answers'].get('agent_1', 'No answer')}")
    print("\nAgent Messages:")
    for round_num, messages in report['debate_history']['rounds'].items():
        print(f"\nRound {round_num}:")
        for msg in messages:
            print(f"[{msg['sender']}]: {msg['content']}")
    
    return question

def run_dual_agent_test(question: dict, model_name: str = "deepseek-chat", rounds: int = 2):
    """Run dual agent debate test"""
    print("\n=== Testing Dual Agent Debate ===")
    
    # Create judge
    judge = LLMJudge(model_name=model_name)
    
    # Create debate manager
    debate_manager = DebateManager(
        topic=question['question'],
        total_rounds=rounds,
        judge_system=judge
    )
    
    # Define background configurations for both roles
    background_config = {
        "solver": {"category": "professional", "role": "engineer"},
        "critic": {"category": "academic", "role": "researcher"}
    }
    
    # Create two agents with different backgrounds
    solver = AgentFactory.create_agent(
        mode="dual",
        agent_id="solver",
        question=question['question'],
        model_name=model_name,
        role="solver",
        background_config=background_config
    )
    
    critic = AgentFactory.create_agent(
        mode="dual",
        agent_id="critic",
        question=question['question'],
        model_name=model_name,
        role="critic",
        background_config=background_config
    )
    
    # Add agents to manager
    debate_manager.register_agent(solver)
    debate_manager.register_agent(critic)
    
    # Run debate
    debate_result = debate_manager.start_debate()
    
    # Generate and save report
    report = save_debate_report(
        question_id=0,
        question=question['question'],
        answer=question['answer'],
        debate_result=debate_result,
        output_dir="debate_reports/dual_agent"
    )
    
    print("\nDebate Summary:")
    print(f"Question: {report['question']}")
    print(f"Ground Truth: {report['ground_truth']}")
    print("\nFinal Answers:")
    for agent_id, answer in report['final_result']['final_answers'].items():
        print(f"{agent_id}: {answer}")
    print("\nAgent Messages:")
    for round_num, messages in report['debate_history']['rounds'].items():
        print(f"\nRound {round_num}:")
        for msg in messages:
            print(f"[{msg['sender']}]: {msg['content']}")

def run_multi_agent_test(question: dict, model_name: str = "deepseek-chat", rounds: int = 2):
    """Run multi-agent debate test"""
    print("\n=== Testing Multi Agent Debate ===")
    
    # Create judge
    judge = LLMJudge(model_name=model_name)
    
    # Create debate manager
    debate_manager = DebateManager(
        topic=question['question'],
        total_rounds=rounds,
        judge_system=judge
    )
    
    # Create background configurations for all agents
    backgrounds = [
        {
            "agent_id": "academic_expert",
            "category": "academic",
            "role": "professor"
        },
        {
            "agent_id": "professional_expert",
            "category": "professional",
            "role": "engineer"
        },
        {
            "agent_id": "creative_expert",
            "category": "creative",
            "role": "philosopher"
        },
        {
            "agent_id": "research_expert",
            "category": "academic",
            "role": "researcher"
        }
    ]
    
    # Create agents with their backgrounds
    for i, bg in enumerate(backgrounds):
        agent = AgentFactory.create_agent(
            mode="multi",
            agent_id=bg["agent_id"],
            question=question['question'],
            model_name=model_name,
            agent_index=i,
            background_config=backgrounds
        )
        debate_manager.register_agent(agent)
    
    # Run debate
    debate_result = debate_manager.start_debate()
    
    # Generate and save report
    report = save_debate_report(
        question_id=0,
        question=question['question'],
        answer=question['answer'],
        debate_result=debate_result,
        output_dir="debate_reports/multi_agent"
    )
    
    print("\nDebate Summary:")
    print(f"Question: {report['question']}")
    print(f"Ground Truth: {report['ground_truth']}")
    print(f"\nFinal Judgment: {report['final_result']['final_judgment']}")
    print("\nFinal Answers:")
    for agent_id, answer in report['final_result']['final_answers'].items():
        print(f"{agent_id}: {answer}")
    print("\nAgent Messages:")
    for round_num, messages in report['debate_history']['rounds'].items():
        print(f"\nRound {round_num}:")
        for msg in messages:
            print(f"[{msg['sender']}]: {msg['content']}")

def run_all_tests():
    """Run all debate tests"""
    print("Starting all tests...")
    
    # Clean report directories
    clean_reports_dir("debate_reports/single_agent")
    clean_reports_dir("debate_reports/dual_agent")
    clean_reports_dir("debate_reports/multi_agent")
    
    # Load dataset
    dataset_path = Path("dataset/gsm8k_mini.jsonl")
    questions = []
    with open(dataset_path, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            questions.append({
                'question': data['question'],
                'answer': data['answer']
            })
    
    # Run first question through all test types
    q = questions[0]
    
    # Run single agent test
    print("\nRunning single agent test...")
    run_single_agent_test(q)
    
    # Run dual agent test
    print("\nRunning dual agent test...")
    run_dual_agent_test(q)
    
    # Run multi agent test
    print("\nRunning multi agent test...")
    run_multi_agent_test(q)

if __name__ == "__main__":
    run_all_tests() 