# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [machine-learning-engineering-architecture.svg](machine-learning-engineering-architecture.svg)
- [machine_learning_engineering/__init__.py](machine_learning_engineering/__init__.py)

</details>



This document provides a technical overview of the MLE-STAR (Machine Learning Engineering with Multiple Agents) system, a sophisticated multi-agent framework designed to automate the implementation of state-of-the-art machine learning models. The system leverages web search, targeted code refinement, and ensemble strategies to achieve competitive performance on machine learning tasks, demonstrating medal-winning results on 63.6% of Kaggle competitions in the MLE-bench-Lite benchmark.

For detailed information about individual agents and their implementations, see [Sub-Agents](#3). For configuration management and deployment procedures, see [Configuration and Setup](#1.2) and [Deployment](#6).

## System Purpose and Architecture

MLE-STAR is a conversational, multi-agent system that automates the end-to-end machine learning engineering process. The system follows a sequential agent architecture where specialized agents handle different phases of ML model development, from initial solution generation through final submission.

### High-Level Agent Architecture

```mermaid
graph TB
    subgraph "MLE-STAR Core System"
        subgraph "Entry Point"
            root_agent["root_agent<br/>(mle_frontdoor_agent)"]
        end
        
        subgraph "Sequential Pipeline"
            pipeline["mle_pipeline_agent<br/>(SequentialAgent)"]
            init["initialization_agent"]
            refine["refinement_agent"] 
            ensemble["ensemble_agent"]
            submit["submission_agent"]
        end
        
        subgraph "Supporting Systems"
            config["DefaultConfig"]
            workspace["workspace_dir"]
            tasks["tasks/california-housing-prices"]
        end
    end
    
    subgraph "External Integration"
        vertex["Vertex AI Agent Engine"]
        genai["Google GenAI Models"]
        search["Web Search & Retrieval"]
    end
    
    root_agent --> pipeline
    pipeline --> init
    init --> refine
    refine --> ensemble
    ensemble --> submit
    
    config --> pipeline
    workspace --> pipeline
    tasks --> init
    
    pipeline --> vertex
    pipeline --> genai
    init --> search
```

Sources: [README.md:1-317](), [machine_learning_engineering/__init__.py:1-4]()

### Core Agent Execution Flow

The system implements a sophisticated state management approach where each agent in the pipeline builds upon the previous agent's results through a shared `CallbackContext.state`.

```mermaid
sequenceDiagram
    participant User
    participant root_agent
    participant mle_pipeline_agent
    participant initialization_agent
    participant refinement_agent
    participant ensemble_agent
    participant submission_agent
    participant State as "CallbackContext.state"
    
    User->>root_agent: "execute the task"
    root_agent->>mle_pipeline_agent: FRONTDOOR_INSTRUCTION
    
    mle_pipeline_agent->>initialization_agent: "Phase 1: Initialize"
    initialization_agent->>State: "Set workspace, task data"
    initialization_agent->>State: "Store initial solutions"
    
    mle_pipeline_agent->>refinement_agent: "Phase 2: Refine"
    refinement_agent->>State: "Store refined code blocks"
    refinement_agent->>State: "Apply targeted improvements"
    
    mle_pipeline_agent->>ensemble_agent: "Phase 3: Ensemble"
    ensemble_agent->>State: "Store ensemble strategies"
    ensemble_agent->>State: "Combine solutions"
    
    mle_pipeline_agent->>submission_agent: "Phase 4: Submit"
    submission_agent->>State: "Generate final submission"
    submission_agent->>State: "Save results to CSV"
    
    State->>State: "save_state callback"
    State->>User: "final_state.json + submission.csv"
```

Sources: [README.md:17-44](), [README.md:167-190]()

## Key System Capabilities

### Initial Solution Generation
The system retrieves state-of-the-art models and example code through web search, then merges the best-performing candidates into a consolidated initial solution. This approach leverages existing ML knowledge and best practices from the broader community.

### Targeted Code Block Refinement
MLE-STAR implements an iterative improvement process that identifies specific code blocks (ML pipeline components) with the most significant performance impact through ablation studies. An inner refinement loop applies various optimization strategies to these targeted components.

### Ensemble Strategies
The system introduces novel ensembling methods where agents propose and refine ensemble strategies to combine multiple solutions, aiming for superior performance compared to individual best solutions.

### Robustness Modules
Three key robustness components ensure system reliability:
- **Debugging Agent**: Automated error correction and code refinement
- **Data Leakage Checker**: Prevents improper data access during preprocessing
- **Data Usage Checker**: Ensures all provided data sources are utilized effectively

Sources: [README.md:35-43]()

## Configuration and Backend Support

The system supports dual backend configurations for flexible deployment scenarios:

| Backend Type | Environment Variable | Authentication | Use Case |
|--------------|---------------------|----------------|----------|
| Vertex AI | `GOOGLE_GENAI_USE_VERTEXAI=true` | GCloud CLI | Production deployment |
| ML Dev API | `GOOGLE_GENAI_USE_VERTEXAI=false` | API Key | Development/testing |

### Configuration Parameters

```mermaid
graph LR
    subgraph "Configuration Sources"
        env[".env file"]
        cli["CLI Arguments"]
        defaults["DefaultConfig"]
    end
    
    subgraph "Core Parameters"
        model["ROOT_AGENT_MODEL<br/>gemini-2.0-flash-001"]
        workspace["workspace_dir<br/>./workspace/"]
        data["data_dir<br/>./tasks/"]
        task["task_name<br/>california-housing-prices"]
        type_param["task_type<br/>Tabular Regression"]
    end
    
    subgraph "Runtime Settings"
        timeout["exec_timeout: 1800s"]
        solutions["num_solutions: 2"] 
        retry["max_retry: 3"]
        lower["lower: true"]
    end
    
    env --> model
    env --> workspace
    defaults --> data
    defaults --> task
    defaults --> type_param
    defaults --> timeout
    defaults --> solutions
    defaults --> retry
    defaults --> lower
```

Sources: [README.md:120-127](), [README.md:272-317]()

## Task Structure and Execution

The system expects a specific task structure for ML problems:

```mermaid
graph TB
    subgraph "Task Directory Structure"
        tasks["tasks/"]
        housing["california-housing-prices/"]
        desc["task_description.txt"]
        data_files["*.csv data files"]
    end
    
    subgraph "Execution Workflow"
        adk_run["adk run machine_learning_engineering"]
        agent_init["Agent Initialization"]
        task_load["Task Loading"]
        pipeline_exec["Pipeline Execution"]
        results["submission.csv + final_state.json"]
    end
    
    tasks --> housing
    housing --> desc
    housing --> data_files
    
    adk_run --> agent_init
    agent_init --> task_load
    task_load --> pipeline_exec
    pipeline_exec --> results
    
    housing --> task_load
```

Sources: [README.md:137-190](), [README.md:278-296]()

The system demonstrates strong performance on tabular regression tasks, achieving competitive results through its multi-agent approach and sophisticated refinement strategies. The architecture enables both local development and cloud deployment, making it suitable for various ML engineering scenarios.