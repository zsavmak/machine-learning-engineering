# Core Agent System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [machine_learning_engineering/agent.py](machine_learning_engineering/agent.py)
- [machine_learning_engineering/prompt.py](machine_learning_engineering/prompt.py)

</details>



## Purpose and Scope

This document provides a deep dive into the main MLE-STAR agent pipeline and execution flow. The core agent system serves as the orchestration layer that coordinates machine learning engineering tasks through a sequential multi-agent architecture.

For detailed information about individual sub-agents and their specific functionalities, see [Sub-Agents](#3). For system configuration and environment setup, see [Configuration and Setup](#1.2). For detailed pipeline execution flow, see [Agent Pipeline](#2.1), and for instruction definitions, see [Instructions and Prompts](#2.2).

## System Architecture Overview

The core agent system implements a two-tier architecture with a root agent that delegates to a sequential pipeline agent, which in turn orchestrates specialized sub-agents.

### Core Agent Hierarchy

```mermaid
graph TD
    root_agent["root_agent<br/>(mle_frontdoor_agent)"]
    pipeline["mle_pipeline_agent<br/>(SequentialAgent)"]
    init["initialization_agent"]
    refine["refinement_agent"] 
    ensemble["ensemble_agent"]
    submit["submission_agent"]
    
    root_agent --> pipeline
    pipeline --> init
    pipeline --> refine
    pipeline --> ensemble
    pipeline --> submit
    
    subgraph "State Management"
        state["CallbackContext.state"]
        save_state_func["save_state()"]
    end
    
    pipeline --> save_state_func
    save_state_func --> state
```

**Sources:** [machine_learning_engineering/agent.py:30-50]()

## Root Agent Structure

The `root_agent` serves as the primary entry point and is configured with specific instructions and model parameters. It implements the frontdoor pattern where initial user interactions are handled before delegating to the pipeline.

### Root Agent Configuration

| Component | Value | Source |
|-----------|-------|---------|
| Agent Name | `mle_frontdoor_agent` | [agent.py:45]() |
| Model | `os.getenv("ROOT_AGENT_MODEL")` | [agent.py:44]() |
| Instruction | `prompt.FRONTDOOR_INSTRUCTION` | [agent.py:46]() |
| Global Instruction | `prompt.SYSTEM_INSTRUCTION` | [agent.py:47]() |
| Temperature | 0.01 | [agent.py:49]() |

The root agent uses the ADK naming convention where the main agent must be named `root_agent` for tool compatibility [machine_learning_engineering/agent.py:42-43]().

### Agent Instantiation Flow

```mermaid
sequenceDiagram
    participant ENV as "Environment Variables"
    participant root as "root_agent"
    participant prompt as "prompt module"
    participant pipeline as "mle_pipeline_agent"
    
    ENV->>root: "ROOT_AGENT_MODEL"
    prompt->>root: "FRONTDOOR_INSTRUCTION"
    prompt->>root: "SYSTEM_INSTRUCTION"
    root->>pipeline: "sub_agents=[mle_pipeline_agent]"
    
    Note over root: "GenerateContentConfig(temperature=0.01)"
    Note over root: "Name: mle_frontdoor_agent"
```

**Sources:** [machine_learning_engineering/agent.py:43-50](), [machine_learning_engineering/prompt.py:4-26]()

## Sequential Pipeline Architecture

The `mle_pipeline_agent` implements the core orchestration logic using the `SequentialAgent` pattern from the ADK framework. This agent executes four specialized sub-agents in sequence.

### Pipeline Configuration

```mermaid
graph LR
    subgraph "mle_pipeline_agent SequentialAgent"
        init_agent["initialization_agent_module.initialization_agent"]
        refine_agent["refinement_agent_module.refinement_agent"] 
        ensemble_agent["ensemble_agent_module.ensemble_agent"]
        submit_agent["submission_agent_module.submission_agent"]
    end
    
    init_agent --> refine_agent
    refine_agent --> ensemble_agent 
    ensemble_agent --> submit_agent
    
    subgraph "Callbacks"
        after_callback["after_agent_callback=save_state"]
    end
    
    submit_agent --> after_callback
```

The pipeline agent is configured with the following parameters:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `name` | `"mle_pipeline_agent"` | Agent identifier |
| `sub_agents` | List of 4 agents | Sequential execution order |
| `description` | Task execution description | Agent documentation |
| `after_agent_callback` | `save_state` function | State persistence |

**Sources:** [machine_learning_engineering/agent.py:30-40]()

## State Management System

The core agent system implements comprehensive state management through the `CallbackContext.state` mechanism, with automatic persistence after each agent execution.

### State Persistence Flow

```mermaid
sequenceDiagram
    participant pipeline as "mle_pipeline_agent"
    participant callback as "save_state function"
    participant context as "CallbackContext.state"
    participant fs as "File System"
    
    pipeline->>callback: "after_agent_callback"
    callback->>context: "get('workspace_dir')"
    callback->>context: "get('task_name')"
    callback->>context: "to_dict()"
    callback->>fs: "write final_state.json"
    
    Note over fs: "File: {workspace_dir}/{task_name}/final_state.json"
```

### State Save Implementation

The `save_state` function [machine_learning_engineering/agent.py:18-27]() implements the following logic:

1. Extracts `workspace_dir` and `task_name` from callback context state
2. Constructs output directory path: `{workspace_dir}/{task_name}`
3. Serializes entire state to `final_state.json` with 2-space indentation
4. Returns `None` to indicate no content response

**Sources:** [machine_learning_engineering/agent.py:18-27]()

## Agent Import Structure

The core agent system imports sub-agents through a modular structure that maintains clear separation of concerns:

```mermaid
graph TD
    subgraph "machine_learning_engineering.agent"
        agent_py["agent.py"]
    end
    
    subgraph "Sub-agent Modules"
        init_mod["sub_agents.initialization.agent"]
        refine_mod["sub_agents.refinement.agent"]
        ensemble_mod["sub_agents.ensemble.agent"] 
        submit_mod["sub_agents.submission.agent"]
    end
    
    subgraph "Prompt Module"
        prompt_mod["prompt.py"]
    end
    
    subgraph "External Dependencies"
        adk["google.adk.agents"]
        genai["google.genai.types"]
        callback["google.adk.agents.callback_context"]
    end
    
    agent_py --> init_mod
    agent_py --> refine_mod
    agent_py --> ensemble_mod
    agent_py --> submit_mod
    agent_py --> prompt_mod
    agent_py --> adk
    agent_py --> genai
    agent_py --> callback
```

Each sub-agent module exposes its agent instance through a standardized naming convention, allowing the pipeline to reference them as `{module_name}.{agent_name}` [machine_learning_engineering/agent.py:10-13]().

**Sources:** [machine_learning_engineering/agent.py:1-16]()