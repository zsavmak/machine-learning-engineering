# Test Framework

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [eval/full_eval/test_eval.py](eval/full_eval/test_eval.py)
- [eval/simple_eval/test_eval.py](eval/simple_eval/test_eval.py)

</details>



The Test Framework provides automated evaluation capabilities for the MLE-STAR machine learning engineering agent system. It integrates with Google's Agent Development Kit (ADK) evaluation framework to run comprehensive tests that validate agent performance across different task complexity levels.

For information about test scenarios and evaluation criteria, see [Test Cases and Configuration](#5.2). For deployment testing of live agents, see [Testing Deployed Agents](#6.2).

## Framework Architecture

The test framework is built around the `AgentEvaluator` class from Google ADK and uses pytest as the test runner. The system supports two evaluation modes: simple evaluation for basic functionality and full evaluation for comprehensive testing.

### Test Framework Components

```mermaid
graph TD
    subgraph "Test Execution Framework"
        PYTEST["pytest Framework"] --> FIXTURES["Session Fixtures"]
        FIXTURES --> ENV_LOAD["load_env fixture"]
        FIXTURES --> MONKEYPATCH["monkeypatch fixture"]
    end
    
    subgraph "Google ADK Integration"
        AGENT_EVAL["AgentEvaluator.evaluate()"] --> TARGET_AGENT["machine_learning_engineering"]
        AGENT_EVAL --> TEST_JSON["Test JSON Files"]
        AGENT_EVAL --> NUM_RUNS["num_runs=1"]
    end
    
    subgraph "Test Suites"
        SIMPLE_TEST["test_basic_interaction()"] --> SIMPLE_JSON["simple.test.json"]
        FULL_TEST["test_full_interaction()"] --> FULL_JSON["full.test.json"]
        FULL_TEST --> TIMEOUT_CONFIG["exec_timeout=30"]
    end
    
    subgraph "Configuration System"
        DOTENV["dotenv.load_dotenv()"] --> CONFIG_MODULE["config.CONFIG"]
        CONFIG_MODULE --> TIMEOUT_OVERRIDE["monkeypatch.setattr()"]
    end
    
    PYTEST --> SIMPLE_TEST
    PYTEST --> FULL_TEST
    ENV_LOAD --> DOTENV
    MONKEYPATCH --> TIMEOUT_OVERRIDE
    SIMPLE_TEST --> AGENT_EVAL
    FULL_TEST --> AGENT_EVAL
    TIMEOUT_OVERRIDE --> FULL_TEST
```

**Sources:** [eval/full_eval/test_eval.py:1-29](), [eval/simple_eval/test_eval.py:1-28]()

### Test Execution Flow

The test framework follows a consistent execution pattern across both simple and full evaluation modes:

```mermaid
sequenceDiagram
    participant PYTEST as "pytest Runner"
    participant FIXTURE as "Session Fixtures"
    participant TEST as "Test Function"
    participant EVAL as "AgentEvaluator"
    participant AGENT as "machine_learning_engineering"
    participant JSON as "Test Definition"
    
    PYTEST->>FIXTURE: "Execute load_env fixture"
    FIXTURE->>FIXTURE: "dotenv.load_dotenv()"
    
    PYTEST->>TEST: "Execute test_*_interaction()"
    TEST->>EVAL: "AgentEvaluator.evaluate()"
    EVAL->>JSON: "Load test scenarios"
    EVAL->>AGENT: "Execute agent with test inputs"
    AGENT->>AGENT: "Process ML tasks"
    AGENT->>EVAL: "Return results"
    EVAL->>TEST: "Evaluation complete"
    TEST->>PYTEST: "Test result"
```

**Sources:** [eval/full_eval/test_eval.py:15-28](), [eval/simple_eval/test_eval.py:15-27]()

## Test Implementation Details

### Session-Level Fixtures

Both test suites use identical session-level fixtures for environment setup:

| Fixture | Purpose | Scope | Auto-use |
|---------|---------|-------|----------|
| `load_env` | Loads environment variables via `dotenv.load_dotenv()` | session | Yes |

The `load_env` fixture [eval/full_eval/test_eval.py:15-17]() ensures that environment configuration is available before any tests execute.

### Test Functions

#### Simple Evaluation Test

The `test_basic_interaction` function [eval/simple_eval/test_eval.py:20-27]() executes basic agent functionality tests:

- **Target Agent**: `"machine_learning_engineering"`
- **Test Definition**: `"./simple.test.json"`
- **Execution Count**: `num_runs=1`
- **Timeout**: Uses default configuration

#### Full Evaluation Test

The `test_full_interaction` function [eval/full_eval/test_eval.py:20-28]() executes comprehensive agent testing:

- **Target Agent**: `"machine_learning_engineering"`
- **Test Definition**: `"./full.test.json"`
- **Execution Count**: `num_runs=1`
- **Timeout Override**: `exec_timeout=30` via `monkeypatch.setattr(config.CONFIG, "exec_timeout", 30)`

### Configuration Management

The test framework integrates with the shared configuration system:

```mermaid
graph LR
    subgraph "Configuration Flow"
        DOTENV_FILE[".env File"] --> LOAD_DOTENV["dotenv.load_dotenv()"]
        LOAD_DOTENV --> CONFIG_MODULE["config.CONFIG"]
        CONFIG_MODULE --> DEFAULT_TIMEOUT["Default exec_timeout"]
        
        MONKEYPATCH["monkeypatch.setattr()"] --> TIMEOUT_OVERRIDE["exec_timeout=30"]
        TIMEOUT_OVERRIDE --> FULL_TEST_CONFIG["Full Test Configuration"]
        DEFAULT_TIMEOUT --> SIMPLE_TEST_CONFIG["Simple Test Configuration"]
    end
    
    subgraph "Test Execution"
        SIMPLE_TEST_CONFIG --> SIMPLE_EVAL["Simple Evaluation"]
        FULL_TEST_CONFIG --> FULL_EVAL["Full Evaluation"]
    end
```

**Sources:** [eval/full_eval/test_eval.py:9,16-17,23](), [eval/simple_eval/test_eval.py:9,16-17]()

## AgentEvaluator Integration

The framework leverages Google ADK's `AgentEvaluator` class for agent execution and evaluation:

### Evaluation Parameters

| Parameter | Type | Purpose |
|-----------|------|---------|
| `agent_name` | `str` | Target agent identifier (`"machine_learning_engineering"`) |
| `test_file` | `str` | Path to JSON test definition file |
| `num_runs` | `int` | Number of evaluation runs (set to `1`) |

### Path Resolution

Test definition files are resolved using `pathlib.Path(__file__).parent` to locate JSON files relative to the test script:

- Simple tests: [eval/simple_eval/test_eval.py:25]()
- Full tests: [eval/full_eval/test_eval.py:26]()

## Async Test Support

Both test suites are configured for asynchronous execution:

- **pytest Plugin**: `pytest_plugins = ("pytest_asyncio",)` [eval/full_eval/test_eval.py:12]()
- **Test Decorators**: `@pytest.mark.asyncio` [eval/full_eval/test_eval.py:20]()
- **Async Functions**: `async def test_*_interaction()` pattern

This enables proper handling of the asynchronous `AgentEvaluator.evaluate()` method calls.

**Sources:** [eval/full_eval/test_eval.py:12,20-21](), [eval/simple_eval/test_eval.py:12,20-21]()