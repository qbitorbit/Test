graph TD
    QA["QA Department"]
    
    %% Shared Level
    SHARED["SHARED Resources<br/>(All QA)"]
    QA --> SHARED
    
    SHARED_FILES["mcp/ | agents/ | skills/ | opencode.json | rules/"]
    SHARED --> SHARED_FILES
    
    %% Departments
    D1["Department 1<br/>QA Automation"]
    D2["Department 2<br/>QA Manual"]
    D3["Department 3<br/>QA Manual"]
    
    QA --> D1
    QA --> D2
    QA --> D3
    
    %% Dept 1 Shared
    D1_SHARED["Dept Shared Resources"]
    D1 --> D1_SHARED
    D1_SHARED_FILES["mcp/ | agents/ | skills/ | opencode.json | rules/"]
    D1_SHARED --> D1_SHARED_FILES
    
    %% Dept 1 Teams
    T1_1["Team: AI Quality Tech Lead<br/>├── mcp/<br/>├── agents/<br/>├── skills/<br/>├── opencode.json<br/>└── AGENTS.md"]
    T1_2["Team: Platform Mock UI+API<br/>├── mcp/<br/>├── agents/<br/>├── skills/<br/>├── opencode.json<br/>└── AGENTS.md"]
    T1_3["Team: Real Devices iOS+Android<br/>├── mcp/<br/>├── agents/<br/>├── skills/<br/>├── opencode.json<br/>└── AGENTS.md"]
    T1_4["Team: QA Operations<br/>├── mcp/<br/>├── agents/<br/>├── skills/<br/>├── opencode.json<br/>└── AGENTS.md"]
    
    D1 --> T1_1
    D1 --> T1_2
    D1 --> T1_3
    D1 --> T1_4
    
    %% Dept 2 Shared
    D2_SHARED["Dept Shared Resources"]
    D2 --> D2_SHARED
    D2_SHARED_FILES["mcp/ | agents/ | skills/ | opencode.json | rules/"]
    D2_SHARED --> D2_SHARED_FILES
    
    %% Dept 2 Teams
    T2_1["Team: Platform + Android<br/>├── mcp/<br/>├── agents/<br/>├── skills/<br/>├── opencode.json<br/>└── AGENTS.md"]
    T2_2["Team: Access 1<br/>├── mcp/<br/>├── agents/<br/>├── skills/<br/>├── opencode.json<br/>└── AGENTS.md"]
    T2_3["Team: Access 2<br/>├── mcp/<br/>├── agents/<br/>├── skills/<br/>├── opencode.json<br/>└── AGENTS.md"]
    T2_4["Team: Other Product<br/>├── mcp/<br/>├── agents/<br/>├── skills/<br/>├── opencode.json<br/>└── AGENTS.md"]
    
    D2 --> T2_1
    D2 --> T2_2
    D2 --> T2_3
    D2 --> T2_4
    
    %% Dept 3 Shared
    D3_SHARED["Dept Shared Resources"]
    D3 --> D3_SHARED
    D3_SHARED_FILES["mcp/ | agents/ | skills/ | opencode.json | rules/"]
    D3_SHARED --> D3_SHARED_FILES
    
    %% Dept 3 Teams
    T3_1["Team: Platform + iOS<br/>├── mcp/<br/>├── agents/<br/>├── skills/<br/>├── opencode.json<br/>└── AGENTS.md"]
    T3_2["Team: Forensic<br/>├── mcp/<br/>├── agents/<br/>├── skills/<br/>├── opencode.json<br/>└── AGENTS.md"]
    T3_3["Team: Access 3<br/>├── mcp/<br/>├── agents/<br/>├── skills/<br/>├── opencode.json<br/>└── AGENTS.md"]
    
    D3 --> T3_1
    D3 --> T3_2
    D3 --> T3_3
    
    %% Styling
    classDef qaStyle fill:#e1f5ff,stroke:#333,stroke-width:2px
    classDef sharedStyle fill:#fff9c4,stroke:#333,stroke-width:2px
    classDef deptStyle fill:#c8e6c9,stroke:#333,stroke-width:2px
    classDef deptSharedStyle fill:#ffe0b2,stroke:#333,stroke-width:2px
    classDef teamStyle fill:#dae8fc,stroke:#333,stroke-width:1px
    classDef filesStyle fill:#f5f5f5,stroke:#666,stroke-width:1px
    
    class QA qaStyle
    class SHARED sharedStyle
    class D1,D2,D3 deptStyle
    class D1_SHARED,D2_SHARED,D3_SHARED deptSharedStyle
    class T1_1,T1_2,T1_3,T1_4,T2_1,T2_2,T2_3,T2_4,T3_1,T3_2,T3_3 teamStyle
    class SHARED_FILES,D1_SHARED_FILES,D2_SHARED_FILES,D3_SHARED_FILES filesStyle
