# Agent Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [machine_learning_engineering/agent.py](machine_learning_engineering/agent.py)

</details>



## Purpose and Scope

The Agent Pipeline is the core orchestration mechanism of the MLE-STAR system, responsible for executing a sequential chain of specialized agents to solve machine learning engineering tasks. This pipeline coordinates the execution flow from task initialization through final submission, managing state persistence and inter-agent communication.

This document covers the pipeline architecture, execution flow, and state management. For configuration of individual sub-agents, see [Sub-Agents](#3). For system-wide configuration and setup, see [Configuration and Setup](#1.2).

## Pipeline Architecture Overview

The Agent Pipeline consists of two main components: the `mle_pipeline_agent` which orchestrates the sequential execution, and the `root_agent` which serves as the user-facing frontdoor interface.

### Core Pipeline Components

```mermaid
graph TD
    subgraph "User Interface Layer"
        USER["`User Request`"] --> ROOT["root_agent<br/>(mle_frontdoor_agent)"]
    end
    
    subgraph "Pipeline Orchestration"
        ROOT --> PIPELINE["mle_pipeline_agent<br/>(SequentialAgent)"]
        PIPELINE --> CALLBACK["save_state<br/>(after_agent_callback)"]
    end
    
    subgraph "Sub-Agent Execution Chain"
        INIT["initialization_agent"]
        REFINE["refinement_agent"] 
        ENSEMBLE["ensemble_agent"]
        SUBMIT["submission_agent"]
        
        PIPELINE --> INIT
        INIT --> REFINE
        REFINE --> ENSEMBLE
        ENSEMBLE --> SUBMIT
    end
    
    subgraph "State Management"
        STATE["CallbackContext.state"]
        JSON_FILE["final_state.json"]
        
        CALLBACK --> STATE
        STATE --> JSON_FILE
    end
    
    subgraph "Configuration Sources"
        ENV_MODEL["ROOT_AGENT_MODEL"]
        FRONTDOOR["FRONTDOOR_INSTRUCTION"]
        SYSTEM["SYSTEM_INSTRUCTION"]
    end
    
    ENV_MODEL --> ROOT
    FRONTDOOR --> ROOT
    SYSTEM --> ROOT
```

*Sources: [machine_learning_engineering/agent.py:30-50]()*

### Agent Class Hierarchy

The pipeline leverages the Google ADK's agent framework with specific agent types for different roles:

| Component | Class Type | Purpose |
|-----------|------------|---------|
| `root_agent` | `agents.Agent` | User-facing interface with system instructions |
| `mle_pipeline_agent` | `agents.SequentialAgent` | Orchestrates sub-agent execution |
| Sub-agents | `agents.Agent` | Specialized task handlers |

*Sources: [machine_learning_engineering/agent.py:30-40](), [machine_learning_engineering/agent.py:43-50]()*

## Sequential Agent Execution Flow

The `mle_pipeline_agent` implements a strict sequential execution pattern where each sub-agent builds upon the work of its predecessors.

### Execution Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant root_agent
    participant mle_pipeline_agent
    participant initialization_agent
    participant refinement_agent  
    participant ensemble_agent
    participant submission_agent
    participant save_state
    participant State as "CallbackContext.state"
    
    User->>root_agent: "Task request with FRONTDOOR_INSTRUCTION"
    root_agent->>mle_pipeline_agent: "Execute pipeline"
    
    Note over mle_pipeline_agent: "Sequential execution begins"
    
    mle_pipeline_agent->>initialization_agent: "1. Initialize task"
    initialization_agent->>State: "Set workspace_dir, task_name, data"
    initialization_agent-->>mle_pipeline_agent: "Initialization complete"
    
    mle_pipeline_agent->>save_state: "after_agent_callback"
    save_state->>State: "Persist state snapshot"
    
    mle_pipeline_agent->>refinement_agent: "2. Refine solutions"
    refinement_agent->>State: "Update code blocks, metrics"
    refinement_agent-->>mle_pipeline_agent: "Refinement complete"
    
    mle_pipeline_agent->>save_state: "after_agent_callback"
    
    mle_pipeline_agent->>ensemble_agent: "3. Create ensembles"
    ensemble_agent->>State: "Store ensemble strategies"
    ensemble_agent-->>mle_pipeline_agent: "Ensemble complete"
    
    mle_pipeline_agent->>save_state: "after_agent_callback"
    
    mle_pipeline_agent->>submission_agent: "4. Generate submission"
    submission_agent->>State: "Final results and outputs"
    submission_agent-->>mle_pipeline_agent: "Submission complete"
    
    mle_pipeline_agent->>save_state: "after_agent_callback"
    save_state->>State: "Write final_state.json"
    
    mle_pipeline_agent-->>root_agent: "Pipeline complete"
    root_agent-->>User: "Task results"
```

*Sources: [machine_learning_engineering/agent.py:32-37](), [machine_learning_engineering/agent.py:39]()*

### Sub-Agent Import Structure

The pipeline imports and orchestrates four specialized sub-agents:

```mermaid
graph LR
    subgraph "Import Modules"
        INIT_MOD["initialization_agent_module"]
        REFINE_MOD["refinement_agent_module"] 
        ENSEMBLE_MOD["ensemble_agent_module"]
        SUBMIT_MOD["submission_agent_module"]
    end
    
    subgraph "Agent Instances"
        INIT_AGENT["initialization_agent"]
        REFINE_AGENT["refinement_agent"]
        ENSEMBLE_AGENT["ensemble_agent"] 
        SUBMIT_AGENT["submission_agent"]
    end
    
    subgraph "Pipeline Configuration"
        SUB_AGENTS["sub_agents=[]"]
        SEQUENTIAL["SequentialAgent"]
    end
    
    INIT_MOD --> INIT_AGENT
    REFINE_MOD --> REFINE_AGENT
    ENSEMBLE_MOD --> ENSEMBLE_AGENT
    SUBMIT_MOD --> SUBMIT_AGENT
    
    INIT_AGENT --> SUB_AGENTS
    REFINE_AGENT --> SUB_AGENTS
    ENSEMBLE_AGENT --> SUB_AGENTS
    SUBMIT_AGENT --> SUB_AGENTS
    
    SUB_AGENTS --> SEQUENTIAL
```

*Sources: [machine_learning_engineering/agent.py:10-13](), [machine_learning_engineering/agent.py:32-37]()*

## State Management and Persistence

The pipeline maintains execution state through the `CallbackContext.state` mechanism, with automatic persistence after each agent execution.

### State Persistence Mechanism

The `save_state` function implements the callback mechanism for persisting agent execution state:

```mermaid
graph TD
    subgraph "Callback Execution"
        AGENT_COMPLETE["Agent Completion"] --> CALLBACK_TRIGGER["after_agent_callback"]
        CALLBACK_TRIGGER --> SAVE_STATE_FUNC["save_state()"]
    end
    
    subgraph "State Extraction"
        SAVE_STATE_FUNC --> GET_WORKSPACE["callback_context.state.get('workspace_dir')"]
        SAVE_STATE_FUNC --> GET_TASK["callback_context.state.get('task_name')"]
    end
    
    subgraph "File Operations"
        GET_WORKSPACE --> BUILD_PATH["os.path.join(workspace_dir, task_name)"]
        GET_TASK --> BUILD_PATH
        BUILD_PATH --> JSON_PATH["os.path.join(run_cwd, 'final_state.json')"]
        JSON_PATH --> WRITE_FILE["json.dump(callback_context.state.to_dict())"]
    end
    
    subgraph "Output"
        WRITE_FILE --> FINAL_STATE_JSON["final_state.json"]
    end
```

*Sources: [machine_learning_engineering/agent.py:18-27]()*

### State Schema and Structure

The state persisted by the `save_state` callback includes:

| State Key | Purpose | Set By |
|-----------|---------|---------|
| `workspace_dir` | Working directory path | Initialization Agent |
| `task_name` | Current task identifier | Initialization Agent |
| Additional state | Agent-specific data | Each sub-agent |

The state is serialized as JSON with 2-space indentation for readability and debugging.

*Sources: [machine_learning_engineering/agent.py:22-26]()*

## Root Agent and Frontdoor Interface

The `root_agent` serves as the primary interface point for the entire MLE-STAR system, configured with system-level instructions and model parameters.

### Root Agent Configuration

```mermaid
graph TD
    subgraph "Environment Configuration"
        ENV_VAR["ROOT_AGENT_MODEL<br/>(environment variable)"]
        MODEL_CONFIG["model parameter"]
    end
    
    subgraph "Instruction System"
        FRONTDOOR["FRONTDOOR_INSTRUCTION<br/>(from prompt module)"]
        SYSTEM["SYSTEM_INSTRUCTION<br/>(from prompt module)"]
    end
    
    subgraph "Agent Parameters"
        NAME["name: 'mle_frontdoor_agent'"]
        TEMP["temperature: 0.01"]
        SUB_AGENT_LIST["sub_agents: [mle_pipeline_agent]"]
    end
    
    subgraph "Root Agent Instance"
        ROOT_AGENT["root_agent<br/>(agents.Agent)"]
    end
    
    ENV_VAR --> MODEL_CONFIG
    FRONTDOOR --> ROOT_AGENT
    SYSTEM --> ROOT_AGENT
    MODEL_CONFIG --> ROOT_AGENT
    NAME --> ROOT_AGENT
    TEMP --> ROOT_AGENT
    SUB_AGENT_LIST --> ROOT_AGENT
```

*Sources: [machine_learning_engineering/agent.py:43-50](), [machine_learning_engineering/agent.py:15]()*

### Agent Naming Convention

The system follows specific naming conventions required by the ADK framework:

- **`root_agent`**: Required name for ADK tools compatibility
- **`mle_frontdoor_agent`**: Descriptive name field for the root agent
- **`mle_pipeline_agent`**: Sequential orchestration agent name

This naming structure ensures proper integration with Google ADK's agent evaluation and deployment systems.

*Sources: [machine_learning_engineering/agent.py:42-45]()*