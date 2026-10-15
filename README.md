# ResiliRoute (v3.3)
## BCP 모빌리티 오케스트레이터 & FinOps 여비 거버넌스 엔진

> **기업 평시 여비 거버넌스(FinOps), 지진·재해 BCP 모빌리티 오케스트레이터 및 시계열 군중 분산(Crowd-Balancing) 엔진**

### 🌐 Google Cloud Run 공식 배포 URL
* **실시간 웹 관제 대시보드 (Live Web URL)**: **[https://resiliroute-1048978192076.asia-northeast1.run.app/](https://resiliroute-1048978192076.asia-northeast1.run.app/)**
* **인터랙티브 API 명세서 (Swagger Docs)**: **[https://resiliroute-1048978192076.asia-northeast1.run.app/docs](https://resiliroute-1048978192076.asia-northeast1.run.app/docs)**

---

## 1. 프로젝트 개요 (Executive Summary)

* **프로젝트명**: ResiliRoute (Adaptive Mobility Governance & BCP Crowd-Balancing Engine)
* **핵심 미션**:
  - **평시**: 일본 대중교통 공식 API인 **Ekispert API MCP 서버**와 사내 여비 규정 RAG를 결합하여 임직원의 신칸센·전철 출장비를 자율 심의하고 최적 비용을 승인(FinOps).
  - **재해 시**: 기상청 **J-Alert 지진 속보 웹훅 인입 시 0.1초 만에 비상 BCP 붉은색 관제 모드로 즉시 전환**하여, 철도 마비로 인한 거점 역(신주쿠역 등)의 군중 압사 병목(Bottleneck Integral $\ge 0.70$)을 사전에 차단하고 임직원 120명을 3대 안전 회랑으로 지능형 군중 분산(Crowd Balancing).

---

## 2. 6계층 엔드투엔드 시스템 아키텍처 (Layer 0 ~ Layer 5)

```
 [사내 발화 / 모바일 품의 / 기상청 J-Alert 지진 웹훅]
                         │
                         ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ Layer 0: Mobility Ingress Perimeter & Confidential Trip DLP  │
 │  - 극비 M&A 출장지, 신사업 코드명, 임직원 실명, 법인카드 인라인 마스킹│
 │  - 지진 J-Alert 웹훅 인입 시 0.1초 만에 전사 BCP 모드 전환    │
 └───────────────────────┬──────────────────────────────────────┘
                         │ (Sanitized Context)
                         ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ Layer 0.5: Mobility Dynamics & Crowd Balancing Engine        │
 │  - [평시] 최근 10일간의 누적 출장 이동 부채(Transit Debt) 적분 연산│
 │  - [재해] 거점 역(신주쿠역) 군중 밀집도 시간 적분(Bottleneck Integral)│
 │  - 3대 대피 회랑 쿼터 산출 (그룹 A 녹지, 그룹 B 버스, 그룹 C 사내)│
 └───────────────────────┬──────────────────────────────────────┘
                         │ (Mobility State Vector)
                         ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ Layer 1: Travel & Crisis Orchestrator & Pluggable Cache      │
 │  - Gemini 3.8 Flash 자연어 출장 의도 분해 (출발/도착/좌석/일정) │
 │  - Pluggable Cache: 로컬 메모리($0) ↔ Vertex AI 캐시(10만토큰)│
 └───────────────────────┬──────────────────────────────────────┘
                         │ (MCP Directives)
                         ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ Layer 2: Mobility Native Core (Ekispert API MCP Server)      │
 │  - 스폰서 공식 Ekispert API 직결 (신칸센 그린샤 vs 보통차 지정석) │
 │  - 사규 제14조 대조: 대리 직급 그린샤 위반 판정 및 일반석 전결 │
 └───────────────────────┬──────────────────────────────────────┘
                         │ (Ekispert Transit Results)
                         ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ Layer 3: Chief Mobility Arbiter & BCP Governor               │
 │  - [평시] 4,470엔 절감 일반석 자동 품의서 작성 및 슬랙 발송  │
 │  - [재해] 120명 사원 1:1 맞춤형 피난 티켓 & QR 발급        │
 │  - [고립자] 롯폰기 외근 고립자(강 과장) 300m 제휴 빌딩 턴바이턴 안내│
 └───────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ Layer 4: Tri-Line Mobility Trajectory & Visualizer           │
 │  - [평시] 3중 여비 궤적: [예산선 vs 신청 원안선 vs 사규 절감선]  │
 │    ──▶ 에메랄드(Emerald) 절감 면적 실시간 셰이딩             │
 │  - [재해] 3중 안전 궤적: [기준선 vs 압사 위험선 vs 군중 분산선] │
 │    ──▶ 사이언(Cyan-Blue) 안전 면적 실시간 셰이딩            │
 └───────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ Layer 5: Live Voice Dispatcher & Three.js 3D Commander       │
 │  - WebGL 3D 홀로그램 관제사 아바타 및 음성 립싱크 애니메이션 │
 │  - Web Speech API 실시간 비상 대피 및 절감 브리핑 음성 방송  │
 └──────────────────────────────────────────────────────────────┘
```

---

## 3. 핵심 수학적 모델링 수식

### 1) 평시: 누적 이동 피로 부채 (Cumulative Transit Debt Integral)
$$
\text{TransitDebt}(t) = \sum_{i=1}^N \Delta \text{TravelHours}_i \cdot \omega_{\text{late\_night}} \cdot \exp\left(-\frac{t - t_i}{\tau_{\text{recovery}}}\right)
$$
* $\Delta \text{TravelHours}_i$: 편도 이동 소요 시간 (시간).
* $\omega_{\text{late\_night}}$: 22시 이후 심야 환승 시 피로 가중치 ($1.50$).
* $\tau_{\text{recovery}}$: 자연 회복 시상수 ($3.5\text{일}$).
* $\text{TransitDebt}(t) \ge 15.0\text{시간}$ 도달 시: 당일치기 출장 불허 및 강제 숙박/화상회의 권고.

### 2) 재해 시: 거점 역 군중 병목 지수 (Station Bottleneck Index)
$$
\text{BottleneckIndex}(s, t) = \frac{\int_{t_0}^t \left( \text{InflowRate}(s, \tau) - \text{EvacuationCapacity}(s, \tau) \right) d\tau}{\text{MaxStationSafetyCapacity}(s)}
$$
* $\text{InflowRate}(s, \tau)$: 시점 $\tau$의 역 유입 인원수.
* $\text{EvacuationCapacity}(s, \tau)$: 유효 배출 용량 (열차 운행 중단 시 $0$으로 급락).
* $\text{MaxStationSafetyCapacity}(s)$: 해당 역 최대 안전 한계 수용력.
* $\text{BottleneckIndex} \ge 0.70$ 도달 시: **해당 역 진입 즉시 전면 차단 및 3개 분산 대피로 강제 우회**.

---

## 4. 합성 재해·출장 시뮬레이터 (3대 핵심 시나리오)

| 시나리오 | 대상 및 상황 | ResiliRoute 시스템 개입 및 결과 |
|---|---|---|
| **시나리오 1: 평시 신칸센 출장 FinOps** | 도쿄 본사 최 대리<br>도쿄 $\to$ 신오사카 노조미 그린샤 신청 | Ekispert MCP 호출 후 사규 제14조 대조<br>보통차 지정석으로 자동 조정되어 **4,470엔(23.1%) 절감** 품의 기안 & 슬랙 전송 |
| **시나리오 2: 지진 J-Alert 군중 분산** | 신주쿠 본사 사원 120명<br>수도권 규모 6.2 강진 발생 | **0.1초 만에 전사 붉은색 BCP 모드 전환**<br>신주쿠역 병목 0.92 폭발 감지 $\to$ 역사 셧다운<br>사원 120명을 **3개 대피 그룹(녹지/버스/사내)으로 분산 티켓 발송** |
| **시나리오 3: 외근 고립자 제휴 대피소 구호** | 롯폰기 외근 강 과장<br>지하철 전면 마비로 도로 고립 | Ekispert + BCP DB 조회 $\to$ **300m 거리 제휴 내진 빌딩(모리 타워 3F 방재센터) 매칭**<br>골목 단위 **턴바이턴 도보 내비 & 모바일 출입 QR 패스 발급** |

---

## 5. 실행 방법 (Quick Start Guide)

### 1) 환경 설정 (`.env`)
```bash
# .env 파일에 환경변수를 설정합니다 (템플릿: .env.example):
GEMINI_API_KEY="your-gemini-api-key"
EKISPERT_API_KEY="your-ekispert-api-key"
GEMINI_MODEL="gemini-3.8-flash"
GEMINI_MODEL_FALLBACK="gemini-flash-latest"
CACHE_BACKEND="local"
HOST="127.0.0.1"
PORT=8000
```

### 2) 테스트 슈트 실행 (16개 전체 테스트 검증)
```bash
pytest -v
```
*(모든 16개 테스트 통과 완료)*

### 3) 관제 서버 및 프론트엔드 실행
```bash
python run_server.py
```
* **웹 대시보드 (관제 콘솔)**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* **Swagger API 문서**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 6. 관제 UI 기능 구성

1. **상단 시뮬레이션 데크**:
   - `[버튼 1: 평시 신칸센 출장 기안]`
   - `[버튼 2: 지진 J-Alert 발생]`
   - `[버튼 3: 외근 고립자 구호]`
   - `[🔄 리셋]`
2. **3중 모빌리티 궤적 그래프 (`trajectoryCanvas`)**:
   - Canvas 기반 실시간 인터랙티브 차트
   - 평시 에메랄드(Emerald) 절감 면적 vs 재해 사이언(Cyan-Blue) 안전 면적 셰이딩
3. **실시간 게이트웨이 로그 인스펙터 (`DevLogInspector`)**:
   - 밀리초 단위 HTTP 패킷 및 Ekispert 연동 실시간 로그 스트림
4. **Three.js WebGL 3D 비상 관제사 아바타**:
   - 미래형 홀로그램 관제사 3D 모델
   - 음성 발화 시 입모양 립싱크(Lip-Sync) 애니메이션 및 Web Speech API 음성 브리핑 연동
5. **신주쿠역 군중 병목 지수 게이지**:
   - 0.70 안전 한계선 초과 시 실시간 붉은색 점멸 알림
6. **실시간 모바일 티켓 & 전자결재 카드**:
   - 120명 사원 분산 티켓, 고립자 턴바이턴 보행로, 출입 QR 코드 미리보기
