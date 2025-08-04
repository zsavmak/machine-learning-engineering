# Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deployment/__init__.py](deployment/__init__.py)

</details>



This document covers the deployment of MLE-STAR agents to cloud infrastructure, specifically Google Cloud Vertex AI Agent Engine, and the testing of deployed agents. This includes deployment scripts, cloud integration, session management, and validation of remote agent instances.

For information about local development and testing, see [Evaluation System](#5). For configuration of cloud backends, see [Configuration and Setup](#1.2).

## Overview

The deployment system enables MLE-STAR agents to be deployed to Google Cloud Vertex AI Agent Engine, providing cloud-hosted agent instances that can be accessed remotely. The deployment process involves packaging the agent code, configuring cloud resources, and creating managed agent instances that support session-based interactions.

### Deployment Architecture

```mermaid
graph TD
    subgraph "Local Development Environment"
        agent_code["machine_learning_engineering agent code"]
        deploy_script["deploy.py"]
        test_script["test_deployment.py"]
    end
    
    subgraph "Deployment Process"
        adk_wrapper["AdkApp wrapper"]
        packaging["requirements + extra packages"]
        cloud_upload["cloud resource upload"]
    end
    
    subgraph "Google Cloud Platform"
        project_config["GOOGLE_CLOUD_PROJECT"]
        location_config["GOOGLE_CLOUD_LOCATION"] 
        storage_config["GOOGLE_CLOUD_STORAGE_BUCKET"]
        iam_config["authentication & IAM"]
    end
    
    subgraph "Vertex AI Agent Engine"
        agent_engines_api["agent_engines API"]
        deployed_instance["deployed agent instance"]
        session_mgmt["session management"]
    end
    
    subgraph "Testing and Validation"
        create_session["create_session"]
        stream_query["stream_query interactions"]
        delete_session["delete_session"]
    end
    
    agent_code --> deploy_script
    deploy_script --> adk_wrapper
    adk_wrapper --> packaging
    packaging --> cloud_upload
    
    project_config --> agent_engines_api
    location_config --> agent_engines_api
    storage_config --> agent_engines_api
    iam_config --> agent_engines_api
    
    cloud_upload --> agent_engines_api
    agent_engines_api --> deployed_instance
    deployed_instance --> session_mgmt
    
    test_script --> create_session
    create_session --> stream_query
    stream_query --> delete_session
    session_mgmt --> create_session
```

Sources: Based on high-level system architecture diagrams showing deployment workflow and Google Cloud integration.

### Deployment Components

The deployment system consists of several key components that handle different aspects of the cloud deployment process:

| Component | Purpose | Key Functionality |
|-----------|---------|------------------|
| `deploy.py` | Main deployment script | Creates and manages Vertex AI agent instances |
| `test_deployment.py` | Deployed agent testing | Interactive testing of remote agent instances |
| `AdkApp` wrapper | Agent packaging | Wraps root_agent with tracing and monitoring |
| `agent_engines` API | Cloud interface | Vertex AI Agent Engine management operations |

### Deployment Flow

```mermaid
sequenceDiagram
    participant dev as "Developer"
    participant deploy as "deploy.py"
    participant adk as "AdkApp"
    participant vertex as "Vertex AI Agent Engine"
    participant test as "test_deployment.py"
    
    dev->>deploy: "deploy.py --create"
    deploy->>adk: "wrap root_agent with tracing"
    adk->>adk: "package requirements + dependencies"
    deploy->>vertex: "create agent instance"
    vertex->>vertex: "provision cloud resources"
    vertex-->>deploy: "agent instance created"
    
    dev->>test: "test_deployment.py"
    test->>vertex: "create_session"
    vertex-->>test: "session_id"
    test->>vertex: "stream_query with task"
    vertex-->>test: "agent responses"
    test->>vertex: "delete_session"
    vertex-->>test: "session terminated"
```

Sources: Inferred from deployment workflow diagrams and system architecture.

## Google Cloud Integration

The deployment system integrates with Google Cloud Platform through several configuration parameters and services:

### Required Configuration

The deployment process requires specific Google Cloud configuration parameters:

- `GOOGLE_CLOUD_PROJECT`: Target GCP project for deployment
- `GOOGLE_CLOUD_LOCATION`: Geographic region for agent instances
- `GOOGLE_CLOUD_STORAGE_BUCKET`: Storage bucket for agent artifacts
- Authentication credentials with appropriate IAM permissions

### Vertex AI Agent Engine Integration

```mermaid
graph LR
    subgraph "Deployment Operations"
        create_op["create agent instance"]
        update_op["update agent configuration"]
        delete_op["delete agent instance"]
        list_op["list deployed agents"]
    end
    
    subgraph "Runtime Operations"
        session_create["create_session"]
        query_stream["stream_query"]
        session_delete["delete_session"]
        session_list["list_sessions"]
    end
    
    subgraph "Vertex AI Agent Engine"
        agent_mgmt["agent management API"]
        session_mgmt["session management API"]
        resource_pool["compute resource pool"]
    end
    
    create_op --> agent_mgmt
    update_op --> agent_mgmt
    delete_op --> agent_mgmt
    list_op --> agent_mgmt
    
    session_create --> session_mgmt
    query_stream --> session_mgmt
    session_delete --> session_mgmt
    session_list --> session_mgmt
    
    agent_mgmt --> resource_pool
    session_mgmt --> resource_pool
```

Sources: Based on cloud integration workflow and Vertex AI architecture patterns.

## Session Management and Testing

Deployed agents support session-based interactions that maintain context across multiple queries. The testing framework validates deployed agent functionality through interactive sessions:

### Session Lifecycle

1. **Session Creation**: Establishes a new conversation context with the deployed agent
2. **Query Streaming**: Sends tasks to the agent and receives streamed responses  
3. **Context Maintenance**: Preserves conversation state across multiple interactions
4. **Session Termination**: Cleans up resources and ends the session

### Testing Deployed Agents

The `test_deployment.py` script provides comprehensive testing of deployed agent instances:

- Interactive query testing with real ML engineering tasks
- Response validation and performance measurement
- Session management verification
- Error handling and recovery testing

Sources: [deployment/__init__.py:1](), inferred from system architecture diagrams showing deployment and testing workflows.