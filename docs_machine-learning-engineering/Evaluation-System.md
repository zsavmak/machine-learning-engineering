# Evaluation System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [eval/__init__.py](eval/__init__.py)
- [eval/full_eval/__init__.py](eval/full_eval/__init__.py)
- [eval/simple_eval/__init__.py](eval/simple_eval/__init__.py)

</details>



## Purpose and Scope

The Evaluation System provides a comprehensive testing framework for validating the capabilities and performance of the MLE-STAR machine learning engineering agent. It implements a two-tier testing approach with basic and comprehensive evaluation scenarios, integrated with Google's Agent Development Kit (ADK) evaluation framework.

This document covers the overall evaluation architecture, test execution flow, and scoring mechanisms. For detailed test implementation and pytest integration, see [Test Framework](#5.1). For specific test scenarios and configuration details, see [Test Cases and Configuration](#5.2).

## Evaluation Architecture

The evaluation system is structured around two primary evaluation tiers, each designed to test different aspects of agent functionality:

```mermaid
graph TB
    subgraph eval_system["eval/ Directory Structure"]
        eval_init["__init__.py"]
        
        subgraph full_eval_dir["full_eval/"]
            full_init["__init__.py"]
            full_test_json["full.test.json"]
            full_config["test_config.json"]
        end
        
        subgraph simple_eval_dir["simple_eval/"]
            simple_init["__init__.py"] 
            simple_test_json["simple.test.json"]
            simple_config["test_config.json"]
        end
    end
    
    subgraph external_frameworks["External Testing Frameworks"]
        adk_evaluator["AgentEvaluator"]
        pytest_runner["pytest"]
    end
    
    subgraph target_agent["Target System"]
        mle_agent["machine_learning_engineering Agent"]
        ml_tasks["California Housing Task<br/>Tabular Regression"]
    end
    
    full_test_json --> adk_evaluator
    simple_test_json --> adk_evaluator
    full_config --> adk_evaluator
    simple_config --> adk_evaluator
    
    pytest_runner --> adk_evaluator
    adk_evaluator --> mle_agent
    mle_agent --> ml_tasks
```

Sources: [eval/__init__.py:1](), [eval/full_eval/__init__.py:1](), [eval/simple_eval/__init__.py:1]()

## Two-Tier Evaluation Approach

The system implements distinct evaluation tiers optimized for different testing scenarios:

| Evaluation Tier | Purpose | Test Complexity | Target Use Case |
|-----------------|---------|-----------------|-----------------|
| `simple_eval` | Basic functionality validation | Low complexity interactions | Smoke testing, quick validation |
| `full_eval` | Comprehensive capability testing | Complex multi-step scenarios | Thorough performance assessment |

### Simple Evaluation Configuration

The `simple_eval` tier focuses on basic agent interactions with weighted scoring:

```mermaid
graph LR
    simple_config["simple_eval/test_config.json"]
    simple_tests["simple.test.json"]
    
    subgraph scoring_weights["Scoring Configuration"]
        tool_trajectory_60["tool_trajectory: 0.6"]
        response_match_40["response_match: 0.4"]
    end
    
    simple_config --> scoring_weights
    simple_tests --> test_execution["Basic Interaction Tests"]
    scoring_weights --> test_execution
```

### Full Evaluation Configuration  

The `full_eval` tier emphasizes comprehensive testing with different scoring priorities:

```mermaid
graph LR
    full_config["full_eval/test_config.json"]
    full_tests["full.test.json"]
    
    subgraph scoring_weights["Scoring Configuration"]
        tool_trajectory_0["tool_trajectory: 0.0"]
        response_match_0["response_match: 0.0"]
    end
    
    full_config --> scoring_weights
    full_tests --> test_execution["Complex Scenario Tests"]
    scoring_weights --> test_execution
```

Sources: Based on diagram analysis of evaluation system architecture

## Test Execution Flow

The evaluation system integrates with both pytest and Google ADK to provide comprehensive test execution:

```mermaid
sequenceDiagram
    participant pytest as "pytest Framework"
    participant test_full as "test_full_interaction"
    participant test_simple as "test_basic_interaction" 
    participant evaluator as "AgentEvaluator.evaluate"
    participant agent as "machine_learning_engineering"
    participant tasks as "ML Tasks"
    participant validation as "Response Validation"
    participant scoring as "Score Calculation"
    
    pytest->>test_full: Execute full evaluation
    pytest->>test_simple: Execute simple evaluation
    
    test_full->>evaluator: Load full.test.json + config
    test_simple->>evaluator: Load simple.test.json + config
    
    evaluator->>agent: Initialize agent instance
    agent->>tasks: Execute California Housing Task
    tasks-->>agent: Return results
    agent-->>evaluator: Provide responses
    
    evaluator->>validation: Validate responses
    validation->>scoring: Calculate weighted scores
    scoring-->>evaluator: Return final scores
    evaluator-->>pytest: Test results
```

Sources: Based on diagram analysis of evaluation pipeline

## Integration with Google ADK

The evaluation system leverages Google's Agent Development Kit (ADK) `AgentEvaluator` class for standardized agent testing:

```mermaid
graph TB
    subgraph adk_integration["ADK Integration Layer"]
        agent_evaluator["AgentEvaluator"]
        evaluation_engine["ADK Evaluation Engine"]
    end
    
    subgraph test_definitions["Test Definitions"]
        test_scenarios["Test Scenarios<br/>(JSON format)"]
        test_configs["Test Configurations<br/>(Scoring weights)"]
    end
    
    subgraph agent_target["Target Agent"]
        mle_star["MLE-STAR Agent"]
        agent_capabilities["Agent Capabilities<br/>- Task initialization<br/>- Code generation<br/>- Model training<br/>- Result submission"]
    end
    
    subgraph evaluation_metrics["Evaluation Metrics"]
        tool_trajectory["tool_trajectory<br/>Execution path validation"]
        response_match["response_match<br/>Output correctness"]
        composite_score["Composite Score<br/>Weighted combination"]
    end
    
    test_scenarios --> agent_evaluator
    test_configs --> agent_evaluator
    agent_evaluator --> evaluation_engine
    evaluation_engine --> mle_star
    mle_star --> agent_capabilities
    
    evaluation_engine --> tool_trajectory
    evaluation_engine --> response_match
    tool_trajectory --> composite_score
    response_match --> composite_score
```

Sources: Based on diagram analysis of evaluation system integration

## Scoring Configuration

The evaluation system uses weighted scoring mechanisms that differ between evaluation tiers:

| Metric | Simple Eval Weight | Full Eval Weight | Description |
|--------|-------------------|------------------|-------------|
| `tool_trajectory` | 0.6 | 0.0 | Validates the sequence of tools/actions used |
| `response_match` | 0.4 | 0.0 | Measures correctness of final responses |

### Simple Evaluation Scoring

The `simple_eval` configuration emphasizes tool usage patterns and response accuracy, making it suitable for validating basic agent functionality and interaction flows.

### Full Evaluation Scoring  

The `full_eval` configuration uses zero weights for standard metrics, suggesting it may employ custom evaluation criteria or focus on qualitative assessment of complex scenarios.

Sources: Based on diagram analysis of test configuration systems