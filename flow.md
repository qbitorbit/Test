graph TD
    %% User Layer
    User[User / Terminal] -- "Commands (Text)" --> Main[Orchestrator (main.py)]

    %% The Brain (Local)
    Main -- "Prompts" --> LLM[Local LLM Server]
    LLM -- "Responses" --> Main

    %% The App Core (LangChain)
    subgraph "Python App (VS Code)"
        Main -- "Selects" --> AgentManager[Agent Manager]
        AgentManager -- "Spawns" --> GenericAgent[Generic Agent]
        AgentManager -- "Spawns" --> SpecificAgent[Samsung/Pixel Agent]
        
        %% Memory
        Context[Context / Memory] -.-> AgentManager
    end

    %% The Hands (MCP/Tools)
    subgraph "Tools & MCP Layer"
        GenericAgent -- "Uses" --> ADBTool[ADB Wrapper Tool]
        GenericAgent -- "Uses" --> FileTool[File/DB Reader]
        SpecificAgent -- "Uses" --> VendorTool[Vendor Settings Tool]
    end

    %% The Hardware
    ADBTool --> Bridge[ADB Server]
    VendorTool --> Bridge
    Bridge -- "USB / WiFi" --> Device1[Android Device 1]
    Bridge -- "USB / WiFi" --> Device2[Android Device 2]
