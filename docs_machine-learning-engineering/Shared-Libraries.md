# Shared Libraries

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [machine_learning_engineering/shared_libraries/__init__.py](machine_learning_engineering/shared_libraries/__init__.py)
- [machine_learning_engineering/shared_libraries/common_util.py](machine_learning_engineering/shared_libraries/common_util.py)

</details>



## Purpose and Scope

The shared libraries provide common utilities and helper functions used across the MLE-STAR agent system. These libraries abstract away low-level operations for code execution, debugging, data validation, and general utility functions, enabling the agents to focus on high-level machine learning engineering tasks.

For configuration management details, see [Configuration Management](#4.1). For code execution capabilities, see [Code Execution System](#4.2). For debugging functionality, see [Debugging System](#4.3). For data validation utilities, see [Data Validation](#4.4).

## Library Structure and Organization

The shared libraries are organized in the `machine_learning_engineering/shared_libraries/` directory and provide specialized utility modules that support different aspects of the agent pipeline execution.

### Core Utility Modules

```mermaid
graph TD
    subgraph "shared_libraries Package"
        COMMON["common_util.py<br/>General utilities"]
        CODE["code_util.py<br/>Python execution"]
        DEBUG["debug_util.py<br/>Error handling"]
        LEAKAGE["check_leakage_util.py<br/>Data validation"]
    end
    
    subgraph "Agent Integration Points"
        PIPELINE["mle_pipeline_agent<br/>SequentialAgent"]
        INIT["initialization_agent"]
        REFINE["refinement_agent"] 
        ENSEMBLE["ensemble_agent"]
        SUBMIT["submission_agent"]
    end
    
    subgraph "Core Operations"
        EXEC["Python Code Execution"]
        SEED["Random Seed Management"]
        FILE["File Operations"]
        RESP["LLM Response Processing"]
        VAL["Data Leakage Detection"]
        ERR["Error Diagnosis"]
    end
    
    PIPELINE --> COMMON
    PIPELINE --> CODE
    PIPELINE --> DEBUG
    PIPELINE --> LEAKAGE
    
    INIT --> COMMON
    REFINE --> DEBUG
    ENSEMBLE --> CODE
    
    COMMON --> SEED
    COMMON --> FILE
    COMMON --> RESP
    CODE --> EXEC
    DEBUG --> ERR
    LEAKAGE --> VAL
```

Sources: [machine_learning_engineering/shared_libraries/common_util.py:1-41]()

### Utility Function Categories

The shared libraries provide four main categories of functionality:

| Category | Module | Primary Functions | Agent Usage |
|----------|--------|------------------|-------------|
| General Utilities | `common_util.py` | Response processing, random seeding, file operations | All agents |
| Code Execution | `code_util.py` | Python script execution, performance extraction | Refinement, ensemble agents |
| Debug Support | `debug_util.py` | Error analysis, code refinement | Refinement agent |
| Data Validation | `check_leakage_util.py` | Data leakage detection, prevention | Initialization, refinement agents |

## Common Utility Functions

The `common_util` module provides fundamental utility functions used throughout the agent system.

### LLM Response Processing

The `get_text_from_response` function extracts text content from Google ADK LLM responses:

```mermaid
flowchart LR
    subgraph "LLM Response Processing"
        INPUT["llm_response.LlmResponse"]
        PARTS["response.content.parts[]"]
        TEXT["Extracted text string"]
    end
    
    subgraph "Implementation Flow"
        CHECK["Check content exists"]
        ITERATE["Iterate through parts"]
        EXTRACT["Extract text attributes"]
        CONCAT["Concatenate final_text"]
    end
    
    INPUT --> CHECK
    CHECK --> PARTS
    PARTS --> ITERATE
    ITERATE --> EXTRACT
    EXTRACT --> CONCAT
    CONCAT --> TEXT
```

Sources: [machine_learning_engineering/shared_libraries/common_util.py:12-22]()

### Random Seed Management

The `set_random_seed` function ensures reproducible results across different libraries:

```mermaid
graph TD
    subgraph "Reproducibility Setup"
        SEED_INPUT["seed: int"]
        RANDOM["random.seed()"]
        NUMPY["np.random.seed()"]
        TORCH_CPU["torch.manual_seed()"]
        TORCH_GPU["torch.cuda.manual_seed()"]
        TORCH_ALL["torch.cuda.manual_seed_all()"]
        CUDNN_DET["cudnn.deterministic = True"]
        CUDNN_BENCH["cudnn.benchmark = False"]
    end
    
    SEED_INPUT --> RANDOM
    SEED_INPUT --> NUMPY
    SEED_INPUT --> TORCH_CPU
    SEED_INPUT --> TORCH_GPU
    SEED_INPUT --> TORCH_ALL
    SEED_INPUT --> CUDNN_DET
    SEED_INPUT --> CUDNN_BENCH
```

Sources: [machine_learning_engineering/shared_libraries/common_util.py:25-33]()

### File Operations

The `copy_file` function provides safe file copying with directory creation:

- Creates destination directories if they don't exist using `os.makedirs(exist_ok=True)`
- Uses `shutil.copy2` to preserve file metadata
- Supports copying files across different directory structures

Sources: [machine_learning_engineering/shared_libraries/common_util.py:36-40]()

## Integration with Agent System

The shared libraries are imported and used throughout the agent pipeline to provide consistent behavior and reduce code duplication:

```mermaid
sequenceDiagram
    participant Agent as "Any Agent"
    participant Common as "common_util"
    participant Code as "code_util"
    participant Debug as "debug_util"
    participant Leakage as "check_leakage_util"
    
    Agent->>Common: "get_text_from_response(llm_response)"
    Common-->>Agent: "Extracted text"
    
    Agent->>Common: "set_random_seed(42)"
    Common-->>Agent: "Reproducible state"
    
    Agent->>Code: "execute_python_code(script)"
    Code-->>Agent: "Execution results"
    
    Agent->>Debug: "analyze_error(traceback)"
    Debug-->>Agent: "Suggested fixes"
    
    Agent->>Leakage: "check_data_leakage(code)"
    Leakage-->>Agent: "Validation results"
```

Sources: [machine_learning_engineering/shared_libraries/common_util.py:1-41]()

The shared libraries form the foundation layer that enables the MLE-STAR agent system to perform complex machine learning engineering tasks while maintaining code quality, reproducibility, and robust error handling.