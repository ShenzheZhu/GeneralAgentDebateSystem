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

```bash
# Clone the repository
git clone https://github.com/ShenzheZhu/GeneralAgentDebateSystem.git
cd GeneralAgentDebateSystem

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

### Running Tests

```bash
# Run all debate modes
python run_test.py

# Run specific test
python tests/test_gsm8k.py
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
agent = AgentFactory.create_agent(
    mode="single",
    agent_id="agent_1",
    question="your_question",
    background_config={
        "category": "academic",
        "role": "professor"
    }
)
```

### 2. Dual Agent Mode
```python
solver = AgentFactory.create_agent(
    mode="dual",
    agent_id="solver",
    role="solver",
    question="your_question",
    background_config={
        "solver": {"category": "professional", "role": "engineer"},
        "critic": {"category": "academic", "role": "researcher"}
    }
)
```

### 3. Multi Agent Mode
```python
agents = [
    {"agent_id": "academic_expert", "category": "academic", "role": "professor"},
    {"agent_id": "professional_expert", "category": "professional", "role": "engineer"},
    {"agent_id": "creative_expert", "category": "creative", "role": "philosopher"}
]
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

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Contact

Shenzhe Zhu - [GitHub](https://github.com/ShenzheZhu) 