# Ensemble Agent

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [machine_learning_engineering/sub_agents/ensemble/agent.py](machine_learning_engineering/sub_agents/ensemble/agent.py)
- [machine_learning_engineering/sub_agents/ensemble/prompt.py](machine_learning_engineering/sub_agents/ensemble/prompt.py)

</details>



## Purpose and Scope

The Ensemble Agent is a specialized sub-agent within the MLE-STAR system responsible for combining multiple machine learning solutions to achieve better performance through ensemble techniques. This agent operates on refined solutions from the refinement phase and creates ensembled predictions by implementing various combination strategies.

For information about the overall agent pipeline workflow, see [Agent Pipeline](#2.1). For details about other specialized agents, see [Sub-Agents](#3).

## Agent Architecture

The `ensemble_agent` is implemented as a `SequentialAgent` that orchestrates multiple sub-agents in a specific order to plan, implement, and iteratively refine ensemble strategies.

### Core Agent Structure

```mermaid
graph TD
    subgraph "ensemble_agent (SequentialAgent)"
        IPA["init_ensemble_plan_agent<br/>(Planning)"]
        IPIA["init_ensemble_plan_implement_agent<br/>(Initial Implementation)"]
        LOOP["ensemble_plan_refine_and_implement_loop_agent<br/>(Iterative Refinement)"]
        
        IPA --> IPIA
        IPIA --> LOOP
    end
    
    subgraph "Loop Agent Components"
        LOOP --> RPR["ensemble_plan_refine_agent<br/>(Plan Refinement)"]
        RPR --> RPI["ensemble_plan_implement_agent<br/>(Plan Implementation)"]
        RPI --> RPR
    end
    
    subgraph "State Management"
        STATE["callback_context.state"]
        STATE --> PLANS["ensemble_plans[]"]
        STATE --> ITER["ensemble_iter"]
        STATE --> RESULTS["ensemble_code_exec_result_{iter}"]
    end
    
    IPA --> STATE
    IPIA --> STATE
    LOOP --> STATE
```

Sources: [machine_learning_engineering/sub_agents/ensemble/agent.py:189-252]()

### Agent Configuration and Dependencies

| Agent Component | Type | Model | Temperature | Description |
|----------------|------|-------|-------------|-------------|
| `init_ensemble_plan_agent` | `Agent` | `config.CONFIG.agent_model` | 1.0 | Generates initial ensemble strategy |
| `init_ensemble_plan_implement_agent` | Debug Agent | Variable | Variable | Implements initial ensemble plan |
| `ensemble_plan_refine_agent` | `Agent` | `config.CONFIG.agent_model` | 1.0 | Refines ensemble strategy based on scores |
| `ensemble_plan_implement_agent` | Debug Agent | Variable | Variable | Implements refined ensemble plans |

Sources: [machine_learning_engineering/sub_agents/ensemble/agent.py:189-225]()

## State Management and Data Flow

The Ensemble Agent manages state through the `callback_context.state` dictionary to coordinate between planning and implementation phases.

### State Variables

```mermaid
graph LR
    subgraph "Input State"
        NS["num_solutions"]
        OLR["outer_loop_round"]
        TC["train_code_{round}_{task_id}"]
        WD["workspace_dir"]
        DD["data_dir"]
        TN["task_name"]
    end
    
    subgraph "Ensemble State"
        EI["ensemble_iter"]
        EP["ensemble_plans[]"]
        ECR["ensemble_code_exec_result_{iter}"]
        SLC["skip_data_leakage_check_{iter}"]
    end
    
    subgraph "Configuration State"
        NTP["num_top_plans"]
        LOWER["lower"]
        ELR["ensemble_loop_round"]
    end
    
    NS --> EP
    OLR --> EP
    TC --> EP
    EI --> ECR
    EP --> ECR
```

Sources: [machine_learning_engineering/sub_agents/ensemble/agent.py:20-33](), [machine_learning_engineering/sub_agents/ensemble/agent.py:76-93]()

### State Lifecycle Functions

| Function | Purpose | State Variables Modified |
|----------|---------|-------------------------|
| `init_ensemble_loop_states` | Initialize loop iteration counter | `ensemble_iter = 0` |
| `update_ensemble_loop_states` | Increment loop iteration counter | `ensemble_iter += 1` |
| `get_init_ensemble_plan` | Store initial ensemble plan | `ensemble_plans = [response_text]` |
| `get_refined_ensemble_plan` | Append refined plan | `ensemble_plans.append(response_text)` |
| `check_ensemble_plan_implement_finish` | Check if implementation completed | `skip_data_leakage_check_{iter}` |

Sources: [machine_learning_engineering/sub_agents/ensemble/agent.py:20-73]()

## Workspace Management

The Ensemble Agent creates a dedicated workspace structure for ensemble operations, separating input data from final outputs.

### Workspace Creation Process

```mermaid
graph TD
    subgraph "create_workspace Function"
        START["create_workspace()"] --> CHECK["Check if ensemble dir exists"]
        CHECK --> REMOVE["shutil.rmtree() if exists"]
        REMOVE --> MKDIRS["Create directory structure"]
        
        MKDIRS --> ENSDIR["workspace/task/ensemble/"]
        MKDIRS --> INPUTDIR["workspace/task/ensemble/input/"]
        MKDIRS --> FINALDIR["workspace/task/ensemble/final/"]
        
        ENSDIR --> COPY["Copy data files"]
        COPY --> EXCLUDE["Exclude 'answer' files"]
        EXCLUDE --> RESULT["Workspace ready"]
    end
    
    subgraph "Data Sources"
        DATADIR["data_dir/task_name/"] --> COPY
    end
```

Sources: [machine_learning_engineering/sub_agents/ensemble/agent.py:158-186]()

## Instruction Generation

The Ensemble Agent uses dynamic instruction generation to provide context-specific prompts based on current state and available solutions.

### Instruction Functions

```mermaid
graph TD
    subgraph "Instruction Generation"
        INIT_INSTR["get_init_ensemble_plan_agent_instruction()"]
        REFINE_INSTR["get_ensemble_plan_refinement_instruction()"]
        IMPLEMENT_INSTR["get_ensemble_plan_implement_agent_instruction()"]
    end
    
    subgraph "Prompt Templates"
        INIT_PROMPT["INIT_ENSEMBLE_PLAN_INSTR"]
        REFINE_PROMPT["ENSEMBLE_PLAN_REFINE_INSTR"] 
        IMPLEMENT_PROMPT["ENSEMBLE_PLAN_IMPLEMENT_INSTR"]
    end
    
    subgraph "State Data"
        SOLUTIONS["python_solutions[]"]
        PLANS["prev_plans_and_scores"]
        SCORES["exec_result.score"]
    end
    
    INIT_INSTR --> INIT_PROMPT
    REFINE_INSTR --> REFINE_PROMPT
    IMPLEMENT_INSTR --> IMPLEMENT_PROMPT
    
    SOLUTIONS --> INIT_INSTR
    SOLUTIONS --> REFINE_INSTR
    SOLUTIONS --> IMPLEMENT_INSTR
    
    PLANS --> REFINE_INSTR
    SCORES --> REFINE_INSTR
```

Sources: [machine_learning_engineering/sub_agents/ensemble/agent.py:76-155](), [machine_learning_engineering/sub_agents/ensemble/prompt.py:1-66]()

### Score-Based Plan Refinement

The `get_ensemble_plan_refinement_instruction` function implements a sophisticated scoring system to guide plan improvement:

| Parameter | Purpose | Default Value |
|-----------|---------|---------------|
| `num_top_plans` | Number of top performing plans to analyze | 3 |
| `lower` | Whether lower scores are better | `True` |
| `criteria` | Scoring criteria ("lower" or "higher") | Based on `lower` flag |

The function uses `numpy.argsort()` to rank previous plans by performance and selects the best performers for analysis.

Sources: [machine_learning_engineering/sub_agents/ensemble/agent.py:96-134]()

## Integration with Debugging System

The Ensemble Agent leverages the shared debugging system for robust code execution and error handling during plan implementation.

### Debug Agent Integration

```mermaid
graph TD
    subgraph "Debug Integration"
        INIT_IMPL["init_ensemble_plan_implement_agent"]
        REFINE_IMPL["ensemble_plan_implement_agent"]
        
        INIT_IMPL --> DEBUG_UTIL["debug_util.get_run_and_debug_agent()"]
        REFINE_IMPL --> DEBUG_UTIL
    end
    
    subgraph "Debug Agent Parameters"
        PREFIX["prefix: 'ensemble_plan_implement'"]
        SUFFIX["suffix: ''"]
        DESC["agent_description"]
        INSTR_FUNC["instruction_func"]
        CALLBACK["before_model_callback"]
    end
    
    DEBUG_UTIL --> PREFIX
    DEBUG_UTIL --> SUFFIX
    DEBUG_UTIL --> DESC
    DEBUG_UTIL --> INSTR_FUNC
    DEBUG_UTIL --> CALLBACK
    
    subgraph "Execution Flow"
        CALLBACK --> CHECK["check_ensemble_plan_implement_finish()"]
        CHECK --> SKIP["Skip if already executed"]
        CHECK --> EXECUTE["Execute if not completed"]
    end
```

Sources: [machine_learning_engineering/sub_agents/ensemble/agent.py:201-225]()

## Iterative Refinement Loop

The ensemble agent uses a `LoopAgent` to iteratively refine ensemble strategies based on performance feedback.

### Loop Configuration

| Component | Value | Purpose |
|-----------|--------|---------|
| `max_iterations` | `config.CONFIG.ensemble_loop_round` | Maximum refinement iterations |
| `before_agent_callback` | `update_ensemble_loop_states` | Increment iteration counter |
| `after_agent_callback` | `update_ensemble_loop_states` | Update state after each iteration |

### Loop Execution Flow

```mermaid
sequenceDiagram
    participant Loop as "ensemble_plan_refine_and_implement_loop_agent"
    participant Refine as "ensemble_plan_refine_agent"
    participant Implement as "ensemble_plan_implement_agent"
    participant State as "callback_context.state"
    
    Loop->>State: update_ensemble_loop_states()
    Loop->>Refine: Execute refinement
    Refine->>State: get_refined_ensemble_plan()
    Refine->>Implement: Pass to implementation
    Implement->>State: Store execution results
    Implement->>Loop: Complete iteration
    Loop->>State: update_ensemble_loop_states()
    
    Note over Loop: Repeat until max_iterations
```

Sources: [machine_learning_engineering/sub_agents/ensemble/agent.py:226-241]()