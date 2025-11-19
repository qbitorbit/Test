graph TD
    %% --- Styles ---
    classDef py fill:#3776ab,stroke:#fff,stroke-width:2px,color:#fff;
    classDef data fill:#f9f2af,stroke:#d4a017,stroke-width:2px,color:#333;
    classDef hardware fill:#e1e1e1,stroke:#333,stroke-width:2px,color:#333;

    %% --- Flow ---
    User((User)) -->|Command| Main[main.py]:::py

    subgraph Orchestration
        Main --> Orch[orchestrator.py]:::py
        Orch <-->|Memory| Context[memory_manager.py]:::py
        Orch <-->|LLM Query| LLM[Local LLM (gpt-oss-120b)]:::py
    end

    subgraph Agents
        Orch -->|Selects| Agent[Specific Agent]:::py
        Agent -->|Decides| Logic[Reasoning Loop]:::py
    end

    subgraph MCP_Tools
        Logic -->|Calls| ADB[adb_tools.py]:::py
        Logic -->|Calls| Files[file_tools.py]:::py
        Logic -->|Calls| SQL[sqlite_reader.py]:::py
    end

    subgraph Hardware
        ADB -->|USB/WiFi| Device[Android Device]:::hardware
    end
