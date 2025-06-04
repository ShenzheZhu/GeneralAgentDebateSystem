# Agent Debate System Architecture

## Overview

The Agent Debate System is designed to facilitate structured debates between AI agents on questions that have definitive ground truth answers, rather than open-ended discussion topics. This is a crucial distinction that affects how agents approach the debate and how the system evaluates their performance.

## Key Characteristics

1. **Ground Truth Focus**:
   - The system is designed for debating questions with verifiable answers
   - Examples: mathematical proofs, scientific facts, historical events, logical puzzles
   - Agents must provide evidence and reasoning that can be verified against established facts
   - The goal is to arrive at the correct answer through collaborative or competitive reasoning

2. **Debate Modes**:
   - **Single Agent Mode**: Self-debate where an agent explores different aspects of a question to find the correct answer
   - **Dual Agent Mode**: Two agents debate opposing views, with the goal of identifying and proving the ground truth
   - **Multi Agent Mode**: Multiple agents contribute different perspectives to collectively solve the problem

## System Architecture

### Core Components

1. **Message System**
   - Message class for all communication
   - Attributes:
     * content: message content
     * sender: sender ID
     * receiver: receiver ID
     * timestamp: time of message
     * message_type: type (debate/system/judge)
     * round_number: current round
     * metadata: additional data

2. **Agent Base**
   - Abstract base class for all agents
   - Core functionality:
     * Message processing
     * State maintenance
     * History tracking
   - Main methods:
     * process_message(): handle incoming messages
     * generate_response(): create responses
     * update_state(): maintain internal state

3. **Debate Manager**
   - Central coordinator
   - Features:
     * Agent registration and management
     * Message routing
     * Round control:
       - Round configuration
       - Progress tracking
       - Round type management (debate/summary)
     * State synchronization

4. **History Manager**
   - History management system
   - Features:
     * Storage:
       - Global history
       - Round-specific history
       - Agent-specific history
     * Context management:
       - Current round context
       - Historical summaries
     * Retrieval:
       - By round
       - By topic
       - By agent

5. **Judge System**
   Two types of judges:
   - **LLM Judge**: 
     * Evaluates logical validity
     * Verifies evidence
     * Checks reasoning steps
     * Identifies fallacies
   
   - **Voting Judge**:
     * Aggregates validator assessments
     * Weights votes by credibility
     * Evaluates proof consensus
     * Tracks claim verification

### Communication Mechanisms

1. **Single Agent Mode**
   - Self-dialogue system
   - State self-maintenance
   - Independent decision making
   - Systematic exploration
   - Proof refinement

2. **Dual Agent Mode**
   - Direct communication
   - Turn-based interaction
   - Solver-critic dynamics
   - Solution verification

3. **Multi Agent Mode**
   - Broadcast communication
   - Expert contribution system
   - Collaborative problem-solving
   - Solution synthesis

### History Sharing System

1. **Layered Storage**
   - Global shared history
   - Agent-private history
   - Context-specific history

2. **Access Control**
   - Role-based access
   - Round-based access
   - Topic-based access

## Implementation Structure

### Code Organization
```
/agent_debate
    /core
        - message.py
        - agent_base.py
        - debate_manager.py
        - history_manager.py
        - judge_system.py
        - round_controller.py
    /agents
        - single_agent.py
        - dual_agent.py
        - multi_agent.py
    /judges
        - llm_judge.py
        - voting_judge.py
        - judge_base.py
    /utils
        - message_router.py
        - state_tracker.py
        - config.py
        - round_utils.py
    /models
        - language_model.py
```

### Key Interfaces

1. **Agent Interface**
   - register_to_debate()
   - process_message()
   - generate_response()
   - update_state()

2. **Debate Manager Interface**
   - register_agent()
   - start_debate()
   - route_message()
   - end_debate()
   - manage_rounds()

3. **Judge Interface**
   - evaluate_round()
   - check_rules()
   - make_decision()
   - get_judgment_explanation()

4. **Round Controller Interface**
   - init_rounds()
   - next_round()
   - get_current_round()
   - get_round_summary()

## Evaluation System

1. **Correctness Assessment**
   - Accuracy verification
   - Logical validity
   - Evidence quality
   - Proof completeness

2. **Reasoning Evaluation**
   - Logic consistency
   - Deduction clarity
   - Assumption identification
   - Conclusion validity

3. **Evidence Verification**
   - Source validation
   - Reference accuracy
   - Context preservation
   - Fact checking

4. **Solution Progress**
   - Answer convergence
   - Reasoning clarity
   - Counter-argument handling
   - Conflict resolution

## Architecture Features

1. **Modularity**: Clear component responsibilities
2. **Flexibility**: Support for multiple debate modes
3. **Extensibility**: Plugin system and observer interfaces
4. **Encapsulation**: Clean interface design
5. **Configurability**: Customizable settings 