# ResiliRoute v3.3 - System Architecture Specification

## 1. High-Level Architecture Overview

ResiliRoute is an Enterprise Mobility FinOps Governance & Earthquake BCP Crowd-Balancing Engine deployed on **Google Cloud Run**. It seamlessly bridges daily corporate travel cost optimization with sub-100ms emergency crisis response.

```mermaid
flowchart TB
    subgraph Users["End Users & Crisis Dispatch"]
        EMP["Corporate Employees<br/>(Business Travelers / Evacuees)"]
        BCP_ADMIN["Crisis Response Commander<br/>(Admin & General Affairs)"]
    end

    subgraph ClientLayer["Frontend Client (Edge Browser)"]
        UI["Real-time Control Dashboard<br/>(Glassmorphism Web UI)"]
        AVATAR["Gemini Live 3D Commander<br/>(Three.js WebGL & Lip-sync)"]
        STT_MIC["Dual-mode Voice & Natural Language Bar<br/>(Web Speech & Gemini Multimodal STT)"]
        GIS["Tokyo Metro Real-time GIS Map<br/>(Leaflet Interactive GIS)"]
        TRI["Tri-Line Mobility Trajectory Canvas<br/>(Dynamic Graph Visualizer)"]
    end

    subgraph CloudRun["Google Cloud Run (Serverless Microservices)"]
        direction TB
        L0["Layer 0: Mobility Ingress Perimeter<br/>• Confidential Trip DLP<br/>• J-Alert Sub-100ms Transition"]
        L05["Layer 0.5: Dynamics & Calculus Engine<br/>• Cumulative Transit Debt Integral<br/>• Hub Station Bottleneck Integral<br/>• 3-Corridor Crowd Balancing"]
        L1["Layer 1: Travel & Crisis Orchestrator<br/>• Gemini 3.8 Flash Intent Parser<br/>• Pluggable Policy Cache Adapter"]
        L2["Layer 2: Mobility Native Core<br/>• Ekispert API MCP Client<br/>• Corporate Travel Policy Engine"]
        L3["Layer 3: Chief Mobility Arbiter<br/>• FinOps Auto-Arbitration<br/>• 1:1 Disaster Mobile Ticket Generator<br/>• Stranded Roppongi Shelter Matcher"]
        L4["Layer 4: Trajectory Visualizer<br/>• Tri-Line Curve Math Generator"]
        L5["Layer 5: Voice Dispatcher<br/>• Google Gemini Dedicated Audio TTS<br/>• Google Cloud Text-to-Speech Client"]
    end

    subgraph GCP_AI["Google Cloud Platform AI & Sponsor Services"]
        GEMINI_LLM["Google Gemini 3.8 Flash<br/>(LLM Decomposition & Multi-intent Routing)"]
        GEMINI_TTS["Gemini Native Audio TTS<br/>(gemini-3.8-flash-tts / 240KB WAV)"]
        GEMINI_STT["Gemini Multimodal Audio STT<br/>(inlineData Speech Recognition)"]
        VERTEX_CACHE["Vertex AI Context Caching<br/>(asia-northeast1 Enterprise Cache)"]
        CLOUD_TTS["Google Cloud Text-to-Speech API<br/>(ja-JP-Neural2-B)"]
        EKISPERT["Ekispert API MCP Server<br/>(Shinkansen & Tokyo Metro Routing)"]
        SLACK["Slack Live Webhook API<br/>(Instant Incident & Approval Notifications)"]
    end

    EMP <--> UI
    BCP_ADMIN <--> UI
    UI --- AVATAR
    UI --- STT_MIC
    UI --- GIS
    UI --- TRI

    STT_MIC -->|Voice / Text / J-Alert| L0
    L0 --> L05
    L05 --> L1
    L1 <--> GEMINI_LLM
    L1 <--> VERTEX_CACHE
    L1 --> L2
    L2 <--> EKISPERT
    L2 --> L3
    L3 --> SLACK
    L3 --> L4
    L3 --> L5
    L5 <--> GEMINI_TTS
    L5 <--> CLOUD_TTS
    STT_MIC <--> GEMINI_STT
    L4 -->|JSON Trajectory| TRI
    L5 -->|Base64 WAV Audio| AVATAR
    L3 -->|GeoJSON Guidance & Pins| GIS
```

---

## 2. Mathematical Models & Core Algorithms

### 2.1 Layer 0.5: Cumulative Transit Debt Integral
Measures employee business travel fatigue debt over a rolling 10-day window:
$$D_{\text{transit}}(t) = \int_{t-10}^{t} \left[ \sum_{i} H_i \cdot w_{\text{late}} \cdot e^{-\lambda(t - \tau_i)} \right] d\tau$$
* If $D_{\text{transit}} > 15.0$ hours, automated policy exception elevates seat upgrade rights.

### 2.2 Layer 0.5: Station Bottleneck Integral & Shutdown Criterion
Calculates crowd congestion pressure at critical transport hubs (e.g. Shinjuku Station):
$$B(t) = \frac{\int_{0}^{t} \left( \Phi_{\text{in}}(\tau) - C_{\text{evac}}(\tau) \right) d\tau}{S_{\text{max}}}$$
* If $B(t) \ge 0.70$: Instant automatic perimeter shutdown issued to prevent station crush disasters.

### 2.3 Layer 0.5: 3-Corridor Crowd-Balancing Optimization
Allocates $N = 120$ headquarters personnel into 3 safe evacuation corridors:
* **Group A (40 pax)**: Meiji Jingu Green Path (Avoids rail concourse)
* **Group B (40 pax)**: Shinjuku Gyoen National Garden
* **Group C (40 pax)**: Hatsudai Secondary Highway & Bus Hub
Each employee receives an individualized 1:1 mobile guidance ticket with QR verification token.

---

## 3. Technology Stack & Hackathon Requirements Mapping

| Layer / Component | Technology Used | Hackathon Criteria Met |
| :--- | :--- | :--- |
| **Execution Environment** | Google Cloud Run (asia-northeast1) | **Requirement 1**: Google Cloud Serverless Container |
| **Generative AI** | Google Gemini 3.8 Flash | **Requirement 2**: Gemini API / Vertex AI |
| **Voice AI (TTS)** | Gemini 3.8 Flash Native TTS + Cloud TTS | **Requirement 2**: Text-to-Speech AI |
| **Voice AI (STT)** | Gemini Multimodal Audio STT | **Requirement 2**: Speech-to-Text AI |
| **Context Memory** | Vertex AI Context Caching ($0.00 zero-cost) | **Requirement 2**: Vertex AI Enterprise Agent Platform |
| **Data Privacy** | Cloud DLP (Confidential Trip Sanitizer) | **Requirement 2**: Natural Language / Security AI |
| **Mobility Sponsor API** | **Ekispert API MCP Server** | **Requirement 3**: Sponsor Specialized Tech (Top Priority) |
| **Frontend Framework** | Three.js (WebGL 3D), Leaflet GIS, Canvas 2D | Interactive Visual UI & Real-time Telemetry |
