## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Frontend ["Next.js Frontend (TypeScript)"]
        UI["Student Dashboard<br/>(Upload, Quiz, Chat)"]
        Auth["Supabase Auth<br/>(JWT Login)"]
    end

    subgraph Backend ["FastAPI Backend (Python)"]
        API["API Endpoints"]
        Parser["PDF Parser & Chunker"]
        Embedder["OpenAI Embedding Engine"]
        RAG["RAG Retrieval Engine"]
        Evaluator["Answer Evaluator"]
    end

    subgraph Database ["Supabase (PostgreSQL)"]
        Relational[("Relational Tables<br/>(Users, Materials, Quizzes)")]
        VectorDB[("pgvector<br/>(Document Chunks & Embeddings)")]
    end

    subgraph External ["External AI"]
        OpenAI["OpenAI API<br/>(text-embedding-3-small & gpt-4o-mini)"]
    end

    %% Flows
    UI -->|1. Login| Auth
    UI -->|2. Upload PDF / Take Quiz| API
    
    API -->|3. Extract Text| Parser
    Parser -->|4. Generate Vectors| Embedder
    Embedder -->|5. Store Vectors| VectorDB
    Embedder -->|API Call| OpenAI
    
    API -->|6. Request Quiz Question| RAG
    RAG -->|7. Search Relevant Context| VectorDB
    RAG -->|8. Generate Grounded Question| OpenAI
    
    API -->|9. Submit Answer| Evaluator
    Evaluator -->|10. Evaluate & Explain| OpenAI
    Evaluator -->|11. Save Results| Relational
    
    API -->|12. Save Metadata| Relational

    classDef frontend fill:#3498db,color:#fff,stroke:#2980b9,stroke-width:2px;
    classDef backend fill:#e67e22,color:#fff,stroke:#d35400,stroke-width:2px;
    classDef db fill:#2ecc71,color:#fff,stroke:#27ae60,stroke-width:2px;
    classDef external fill:#9b59b6,color:#fff,stroke:#8e44ad,stroke-width:2px;

    class UI,Auth frontend;
    class API,Parser,Embedder,RAG,Evaluator backend;
    class Relational,VectorDB db;
    class OpenAI external;
