graph TD
    %% --- Styles ---
    classDef py fill:#3776ab,stroke:#fff,stroke-width:2px,color:#fff;
    classDef data fill:#f9f2af,stroke:#d4a017,stroke-width:2px,color:#333;
    classDef hardware fill:#e1e1e1,stroke:#333,stroke-width:2px,color:#333;
    classDef llm fill:#10a37f,stroke:#fff,stroke-width:2px,color:#fff;
    classDef ui fill:#4CAF50,stroke:#388E3C,stroke-width:2px,color:#fff;

    %% --- 1. User Interaction Layer ---
    User((User)):::ui -- "Input Command" --> Main[main.py<br/>Entry Point]:::py

    %% --- 2. Core Logic & Orchestration ---
    subgraph "Orchestration Layer"
        Main --> Orch[orchestrator.py<br/>Routing Logic]:::py
        Orch <-->|Read/Write Context| Memory[memory_manager.py<br/>Chat History/Context]:::py
        Orch -->|Selects Agent| AgentMgr[agent_factory.py]:::py
    end

    %% --- 3. Intelligence Layer ---
    subgraph "Intelligence (Local LLM)"
        Orch <-->|Prompt/Response| LLMConn[llm_client.py<br/>LangChain Interface]:::py
        LLMConn <-->|HTTP Req| LocalLLM[Local Server<br/>gpt-oss-120b]:::llm
    end

    %% --- 4. Agent Layer ---
    subgraph "Agents Layer"
        AgentMgr -->|Spawns| GenAgent[generic_agent.py]:::py
        AgentMgr -->|Spawns| SamAgent[samsung_agent.py]:::py
        AgentMgr -->|Spawns| TaskAgent[playstore_agent.py]:::py
        GenAgent & SamAgent & TaskAgent -- "Reasoning/Action" --> LLMConn
    end

    %% --- 5. Tools & MCP Layer ---
    subgraph "Tools / Skills Layer"
        GenAgent & SamAgent & TaskAgent -->|Calls| ADBTool[adb_tools.py<br/>Shell/Push/Pull]:::py
        SamAgent -->|Calls| SettingsTool[samsung_tools.py<br/>Vendor Settings]:::py
        TaskAgent -->|Calls| DBTool[sqlite_reader.py<br/>App DB Analysis]:::py
        TaskAgent -->|Calls| FileTool[file_system_tools.py<br/>Local File Ops]:::py
    end

    %% --- 6. Data & File System ---
    subgraph "Data Persistence"
        DBTool <-->|Read/Query| AppDB[(fetched_app.sqlite)]:::data
        SettingsTool <-->|Read Config| Profiles[device_profiles.json]:::data
        Orch <-->|Load Config/Workflow| Workflows[workflows.yaml]:::data
        FileTool <-->|Read/Write Local| LocalStorage[data/local_storage/]:::data
    end

    %% --- 7. Hardware Layer ---
    subgraph "Hardware Interface"
        ADBTool -->|Commands| Bridge[ADB Server]:::hardware
        Bridge -->|Control via USB/WiFi| S24[Samsung S24+]:::hardware
        Bridge -->|Control via USB/WiFi| Pixel[Pixel 8]:::hardware
    end
