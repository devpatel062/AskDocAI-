# Application Architecture & Interaction Flow

This document details the interaction flow within the AskDocAI application.

## 📄 Application Flow Diagram

Since AskDocAI is a Single Page Application (SPA), all interactions happen within the main Chat Interface. The diagram below illustrates the user journey and state transitions.

```mermaid
graph TD
    Start([User Opens App]) --> Init{Initial State}
    Init -->|Empty History| Welcome[Display Welcome Message]
    
    Welcome --> UserInput[/User Types Query/]
    ChatHist --> UserInput
    
    UserInput -->|Click Send / Enter| Validate{Input Valid?}
    Validate -->|No| UserInput
    Validate -->|Yes| Loading[Set Loading State & Show User Message]
    
    Loading -->|POST /api/ask| API[Backend API]
    
    API -->|Success| UpdateState[Update Messages & History]
    API -->|Error| ShowErr[Display Error Message]
    
    UpdateState --> DisplayAns[Display AI Response]
    DisplayAns --> ChatHist[Chat Interface]
    ShowErr --> ChatHist
```

## 🧩 Component Hierarchy

The frontend is built as a lightweight React application with the following component structure:

```mermaid
graph TD
    Root[main.jsx] --> App[App.jsx]
    
    subgraph "App Component"
        Header[Header Section]
        ChatArea[Chat Message List]
        InputArea[Input Form]
    end
    
    App --> Header
    App --> ChatArea
    App --> InputArea
```
