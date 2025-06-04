# General Agent Debate System

A flexible and extensible multi-agent debate framework that enables AI agents to engage in structured discussions and collaborative problem-solving.

## 🌟 Features

- **Multiple Debate Modes**:
  - Single Agent (Self-reflection)
  - Dual Agent (Solver-Critic)
  - Multi Agent (Group Discussion)

- **Customizable Agent Roles**:
  - Academic backgrounds (professors, researchers)
  - Professional backgrounds (engineers, experts)
  - Creative backgrounds (philosophers, innovators)

- **Flexible Architecture**:
  - Modular design for easy extension
  - Plugin system for different LLM backends
  - Customizable debate formats and rules

- **Built-in Evaluation**:
  - Automated judgment system
  - Performance metrics tracking
  - Detailed debate reports

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git
- Access to LLM APIs (DeepSeek, OpenAI)
- 8GB RAM minimum

```bash
# Clone the repository
git clone https://github.com/ShenzheZhu/GeneralAgentDebateSystem.git
cd GeneralAgentDebateSystem

# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Set up your API keys in `agent_debate/models/Config.py`:
```python
OPENAI_API_KEY = "your-openai-key"
DEEPSEEK_API_KEY = ["your-deepseek-key"]
```

2. Choose or customize agent backgrounds in `agent_debate/config/backgrounds/`

3. Prepare the dataset:
```bash
# Download the GSM8K mini dataset
mkdir -p dataset
wget https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/mini.jsonl -O dataset/gsm8k_mini.jsonl
```

### Running Tests

```bash
# Run all debate modes
python run_test.py

# Run specific test
python tests/test_gsm8k.py
```

### Example Output

After running the tests, you can find the debate reports in the `debate_reports` directory:
```
debate_reports/
├── single_agent/
│   └── debate_report_q0.json
├── dual_agent/
│   └── debate_report_q0.json
└── multi_agent/
    └── debate_report_q0.json
```

## 🏗️ System Architecture

### Core Components

1. **Debate Manager** (`agent_debate/core/debate_manager.py`)
   - Coordinates the entire debate process
   - Manages rounds and turn-taking
   - Handles message routing

2. **Agents** (`agent_debate/agents/`)
   - `single_agent.py`: Self-reflection and analysis
   - `dual_agent.py`: Solver-Critic interaction
   - `multi_agent.py`: Group discussion
   - `agent_factory.py`: Agent creation and configuration

3. **History Management** (`agent_debate/core/history_manager.py`)
   - Tracks debate progress
   - Maintains message history
   - Generates statistics

4. **Judge System** (`agent_debate/judges/`)
   - Evaluates debate quality
   - Makes final judgments
   - Provides feedback

### Message Flow

```
[Agent 1] ---> [Debate Manager] ---> [Agent 2]
     ^                                   |
     |                                   v
[History Manager] <--- [Judge System] <---
```

## 💡 Use Cases

### 1. Single Agent Mode
```python
from agent_debate.agents.agent_factory import AgentFactory
from agent_debate.core.debate_manager import DebateManager
from agent_debate.judges.llm_judge import LLMJudge

# Create debate manager and judge
judge = LLMJudge(model_name="deepseek-chat")
debate_manager = DebateManager(
    topic="What is the solution to climate change?",
    total_rounds=2,
    judge_system=judge
)

# Create and configure agent
agent = AgentFactory.create_agent(
    mode="single",
    agent_id="agent_1",
    question="What is the solution to climate change?",
    model_name="deepseek-chat",
    background_config={
        "category": "academic",
        "role": "professor"
    }
)

# Register agent and start debate
debate_manager.register_agent(agent)
result = debate_manager.start_debate()

# Process results
final_answer = result["final_answers"]["agent_1"]
debate_history = result["debate_history"]["messages"]
print(f"Final Answer: {final_answer}")
```

### 2. Dual Agent Mode
```python
# Create debate manager
debate_manager = DebateManager(
    topic="Is AI consciousness possible?",
    total_rounds=3,
    judge_system=LLMJudge(model_name="deepseek-chat")
)

# Define background configurations
background_config = {
    "solver": {"category": "professional", "role": "engineer"},
    "critic": {"category": "academic", "role": "researcher"}
}

# Create solver and critic agents
solver = AgentFactory.create_agent(
    mode="dual",
    agent_id="solver",
    question="Is AI consciousness possible?",
    model_name="deepseek-chat",
    role="solver",
    background_config=background_config
)

critic = AgentFactory.create_agent(
    mode="dual",
    agent_id="critic",
    question="Is AI consciousness possible?",
    model_name="deepseek-chat",
    role="critic",
    background_config=background_config
)

# Register agents and start debate
debate_manager.register_agent(solver)
debate_manager.register_agent(critic)
result = debate_manager.start_debate()

# Process results
solver_answer = result["final_answers"]["solver"]
critic_answer = result["final_answers"]["critic"]
debate_rounds = result["debate_history"]["rounds"]
```

### 3. Multi Agent Mode
```python
# Create debate manager
debate_manager = DebateManager(
    topic="How to improve education system?",
    total_rounds=2,
    judge_system=LLMJudge(model_name="deepseek-chat")
)

# Define agent backgrounds
backgrounds = [
    {"agent_id": "academic_expert", "category": "academic", "role": "professor"},
    {"agent_id": "professional_expert", "category": "professional", "role": "engineer"},
    {"agent_id": "creative_expert", "category": "creative", "role": "philosopher"}
]

# Create and register agents
for i, bg in enumerate(backgrounds):
    agent = AgentFactory.create_agent(
        mode="multi",
        agent_id=bg["agent_id"],
        question="How to improve education system?",
        model_name="deepseek-chat",
        agent_index=i,
        background_config=backgrounds
    )
    debate_manager.register_agent(agent)

# Start debate and get results
result = debate_manager.start_debate()

# Process results
final_judgment = result["final_judgment"]
individual_answers = result["final_answers"]
debate_statistics = result["statistics"]

# Save debate report
from datetime import datetime
import json

report_path = f"debate_reports/multi_agent/debate_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
```

## 📊 Output Format

The system generates detailed debate reports in JSON format:
```json
{
    "question_id": 0,
    "question": "...",
    "ground_truth": "...",
    "debate_config": {
        "model": "deepseek-chat",
        "rounds": 2,
        "mode": "single_agent"
    },
    "debate_history": {
        "messages": [],
        "rounds": {},
        "agent_summaries": {}
    },
    "final_result": {
        "final_judgment": "...",
        "final_answers": {}
    }
}
```

## 🔧 Customization

### Adding New Agent Types
1. Create a new agent class inheriting from `AgentBase`
2. Implement required methods (`process_message`, `generate_response`)
3. Register in `AgentFactory`

### Custom Backgrounds
Add new YAML files in `agent_debate/config/backgrounds/`:
```yaml
category: "your_category"
role: "your_role"
system_prompt: "Your custom prompt..."
```

### Custom Prompts
Modify or add YAML files in `agent_debate/config/prompts/`:
```yaml
system: "System prompt..."
initial_analysis: "Initial analysis prompt..."
verify_analysis: "Verification prompt..."
```

## 📞 Contact

Shenzhe Zhu
- GitHub: [@ShenzheZhu](https://github.com/ShenzheZhu)
- Email: [your-email@example.com]
- Project Link: [https://github.com/ShenzheZhu/GeneralAgentDebateSystem](https://github.com/ShenzheZhu/GeneralAgentDebateSystem)
