"""
ResiliRoute FastAPI Gateway & Enterprise Control Center Server
Provides RESTful APIs for Travel FinOps, J-Alert BCP Webhook, Simulation Deck, and WebSocket/Polling for UI.
Localized purely in Japanese.
"""
from typing import Dict, Any, Optional, List
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import settings
from layer0_ingress import IngressPerimeter, JAlertPayload
from layer0_5_dynamics import MobilityDynamicsEngine, TripHistoryItem
from layer1_orchestrator import TravelCrisisOrchestrator
from layer2_mobility_core import EkispertMCPClient, CorporateTravelPolicyEngine
from layer3_arbiter import ChiefMobilityArbiter
from layer4_visualizer import TrajectoryVisualizer
from layer5_voice_dispatcher import VoiceDispatcher
from simulator import SyntheticSimulator
from cache_adapter import cache_instance

app = FastAPI(
    title="ResiliRoute BCP Mobility Orchestrator",
    version="3.3",
    description="Corporate Mobility FinOps & Earthquake BCP Crowd-Balancing Engine"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State Container
class SystemState:
    def __init__(self):
        self.is_bcp_mode: bool = False
        self.bcp_activated_at: Optional[str] = None
        self.last_jalert: Optional[Dict[str, Any]] = None
        self.shinjuku_bottleneck_index: float = 0.15
        self.logs: List[Dict[str, Any]] = []
        self.last_trajectory: Optional[Dict[str, Any]] = None
        self.last_approval: Optional[Dict[str, Any]] = None
        self.last_evacuation_plan: Optional[Dict[str, Any]] = None
        self.last_stranded_rescue: Optional[Dict[str, Any]] = None

    def add_log(self, method: str, path: str, status_code: int, duration_sec: float, message: str, tag: str = "GATEWAY"):
        log_entry = {
            "timestamp": time.strftime("%H:%M:%S"),
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_sec": round(duration_sec, 4),
            "duration_ms": round(duration_sec * 1000, 2),
            "message": message,
            "tag": tag
        }
        self.logs.insert(0, log_entry)
        if len(self.logs) > 100:
            self.logs = self.logs[:100]

state = SystemState()

# Instantiate core engines
ingress = IngressPerimeter()
dynamics = MobilityDynamicsEngine()
orchestrator = TravelCrisisOrchestrator()
ekispert = EkispertMCPClient()
policy = CorporateTravelPolicyEngine()
arbiter = ChiefMobilityArbiter()
visualizer = TrajectoryVisualizer()
voice = VoiceDispatcher()
simulator = SyntheticSimulator()

# Initial trajectory
state.last_trajectory = visualizer.generate_finops_trajectory().model_dump()

# Request Models
class TravelRequestPayload(BaseModel):
    message: str
    employee_name: Optional[str] = "田中 主任"
    employee_rank: Optional[str] = "主任"

class SimulationRunPayload(BaseModel):
    scenario_id: int # 1, 2, or 3

class TTSRequestPayload(BaseModel):
    text: str

class STTRequestPayload(BaseModel):
    audio_base64: str
    mime_type: Optional[str] = "audio/webm"

class StrandedDistressPayload(BaseModel):
    employee_name: str = "佐藤 課長"
    location: str = "六本木ヒルズ付近交差点 (Roppongi Hills)"
    message: str = "地下鉄全面運休のため道路で孤立"

# ----------------- API ENDPOINTS ----------------- #

@app.get("/v1/mobility/status")
def get_system_status():
    """Returns real-time gateway and BCP system state."""
    return {
        "is_bcp_mode": state.is_bcp_mode,
        "ui_theme": "EMERGENCY_RED_ALERT" if state.is_bcp_mode else "NORMAL_FINOPS_BLUE",
        "bcp_activated_at": state.bcp_activated_at,
        "shinjuku_bottleneck_index": state.shinjuku_bottleneck_index,
        "cache_stats": cache_instance.get_cache_stats(),
        "recent_logs": state.logs[:20],
        "active_alert": state.last_jalert,
        "last_approval": state.last_approval,
        "last_stranded_rescue": state.last_stranded_rescue
    }

@app.post("/v1/mobility/request")
def process_mobility_request(payload: TravelRequestPayload):
    """
    Handles natural language travel request with DLP, Ekispert query, policy check, and arbitration.
    """
    t0 = time.perf_counter()

    # 1. DLP Scan
    sanitized = ingress.process_travel_request(payload.message)

    # 2. Transit Debt
    history = [
        TripHistoryItem(trip_id="T1", date_offset_days=3.0, travel_hours=2.5, is_late_night=False, origin="東京", destination="名古屋"),
        TripHistoryItem(trip_id="T2", date_offset_days=7.0, travel_hours=3.0, is_late_night=True, origin="東京", destination="仙台")
    ]
    debt = dynamics.calculate_transit_debt("EMP-2041", payload.employee_name, payload.employee_rank, history)

    # 3. Orchestration
    directive = orchestrator.orchestrate_request(sanitized.sanitized_text, is_bcp_mode=state.is_bcp_mode)

    # 3-A. Stranded Rescue Intent Handling
    if directive.intent.intent_type == "STRANDED_RESCUE":
        emp_name = directive.intent.employee_name or payload.employee_name or "佐藤 課長"
        rescue_plan = arbiter.rescue_stranded_employee(
            employee_name=emp_name,
            location="六本木ヒルズ付近交差点 (Roppongi Hills)"
        )
        state.last_stranded_rescue = rescue_plan.model_dump()
        voice_payload = voice.dispatch_stranded_rescue(
            employee_name=emp_name,
            shelter_name=rescue_plan.matched_shelter_name
        )
        duration = time.perf_counter() - t0
        state.add_log(
            "POST", "/v1/mobility/request", 200, duration,
            f"[自然言語発話: 孤立救護] {emp_name} -> {rescue_plan.matched_shelter_name}",
            tag="RESCUE"
        )
        return {
            "status": "PROCESSED",
            "intent_type": "STRANDED_RESCUE",
            "sanitized_input": sanitized.sanitized_text,
            "masked_count": len(sanitized.masked_entities),
            "rescue_plan": rescue_plan.model_dump(),
            "voice_dispatch": voice_payload.model_dump()
        }

    # 3-B. Disaster Evacuation Intent Handling
    if directive.intent.intent_type == "DISASTER_EVACUATION":
        state.is_bcp_mode = True
        state.bcp_activated_at = time.strftime("%Y-%m-%d %H:%M:%S")
        inflow = [200, 500, 1000, 1600, 2400, 3200, 3800]
        evac_cap = [1200, 400, 50, 0, 0, 0, 0]
        bottleneck = dynamics.calculate_bottleneck_integral(
            station_name="新宿駅 (Shinjuku Station)",
            inflow_series=inflow,
            evacuation_capacity_series=evac_cap,
            max_station_safety_capacity=12000
        )
        state.shinjuku_bottleneck_index = bottleneck.bottleneck_index
        employee_ids = [f"EMP-HQ-{i:03d}" for i in range(1, 121)]
        crowd_plan = dynamics.allocate_crowd_balancing(
            employee_ids=employee_ids,
            hub_station="新宿駅",
            bottleneck_index=bottleneck.bottleneck_index
        )
        tickets = arbiter.generate_evacuation_tickets(crowd_plan)
        trajectory = visualizer.generate_disaster_trajectory(bottleneck_peak=bottleneck.bottleneck_index)
        state.last_trajectory = trajectory.model_dump()
        state.last_evacuation_plan = {
            "crowd_plan": crowd_plan.model_dump(),
            "total_tickets": len(tickets),
            "tickets_preview": [t.model_dump() for t in tickets[:5]]
        }
        voice_payload = voice.dispatch_earthquake_evacuation(
            bottleneck_index=bottleneck.bottleneck_index,
            total_employees=120
        )
        duration = time.perf_counter() - t0
        state.add_log(
            "POST", "/v1/mobility/request", 200, duration,
            f"[自然言語発話: 避難回廊編成] 新宿駅ボトルネック: {bottleneck.bottleneck_index}",
            tag="BCP_ALERT"
        )
        return {
            "status": "PROCESSED",
            "intent_type": "DISASTER_EVACUATION",
            "sanitized_input": sanitized.sanitized_text,
            "masked_count": len(sanitized.masked_entities),
            "bottleneck": bottleneck.model_dump(),
            "crowd_balancing_plan": crowd_plan.model_dump(),
            "total_tickets_issued": len(tickets),
            "tickets_preview": [t.model_dump() for t in tickets[:5]],
            "trajectory": trajectory.model_dump(),
            "voice_dispatch": voice_payload.model_dump()
        }

    # 4. Ekispert Query (Normal FinOps)
    courses = ekispert.search_shinkansen_courses(
        origin=directive.intent.origin,
        destination=directive.intent.destination,
        date=directive.intent.departure_date,
        time=directive.intent.departure_time
    )
    selected_course = courses[0]

    # 5. Policy Check
    compliance = policy.evaluate_request(
        employee_name=payload.employee_name,
        employee_rank=payload.employee_rank,
        requested_seat=directive.intent.requested_seat,
        green_fare=selected_course.total_green_jpy,
        reserved_fare=selected_course.total_reserved_jpy,
        transit_debt_hours=debt.transit_debt_hours
    )

    # 6. Arbiter
    approval = arbiter.arbitrate_travel_application(
        compliance=compliance,
        course=selected_course,
        origin=directive.intent.origin,
        destination=directive.intent.destination
    )
    state.last_approval = approval.model_dump()

    # 7. Trajectory
    trajectory = visualizer.generate_finops_trajectory(
        savings_jpy=compliance.cost_saving_jpy,
        original_fare=compliance.original_fare_jpy,
        approved_fare=compliance.approved_fare_jpy
    )
    state.last_trajectory = trajectory.model_dump()

    # 8. Voice
    voice_payload = voice.dispatch_finops_approval(
        employee_name=payload.employee_name,
        savings_jpy=compliance.cost_saving_jpy,
        approved_seat=compliance.recommended_seat_type
    )

    duration = time.perf_counter() - t0
    state.add_log(
        "POST", "/v1/mobility/request", 200, duration,
        f"[Ekispert: {compliance.cost_saving_jpy:,}円 削減] {payload.employee_name} ({payload.employee_rank})",
        tag="FINOPS"
    )

    return {
        "status": "PROCESSED",
        "intent_type": "TRAVEL_BOOKING",
        "sanitized_input": sanitized.sanitized_text,
        "masked_count": len(sanitized.masked_entities),
        "ekispert_course": selected_course.model_dump(),
        "policy_compliance": compliance.model_dump(),
        "approval_draft": approval.model_dump(),
        "trajectory": trajectory.model_dump(),
        "voice_dispatch": voice_payload.model_dump()
    }

@app.post("/v1/disaster/webhook")
def handle_disaster_webhook(payload: JAlertPayload):
    """
    J-Alert Earthquake Webhook endpoint. Activates BCP mode in < 0.1s and runs crowd balancing.
    """
    t0 = time.perf_counter()
    bcp_resp = ingress.trigger_jalert(payload)

    state.is_bcp_mode = True
    state.bcp_activated_at = time.strftime("%Y-%m-%d %H:%M:%S")
    state.last_jalert = payload.model_dump()

    # Layer 0.5 Bottleneck integral
    inflow = [200, 500, 1000, 1600, 2400, 3200, 3800]
    evac_cap = [1200, 400, 50, 0, 0, 0, 0]
    bottleneck = dynamics.calculate_bottleneck_integral(
        station_name="新宿駅 (Shinjuku Station)",
        inflow_series=inflow,
        evacuation_capacity_series=evac_cap,
        max_station_safety_capacity=12000
    )
    state.shinjuku_bottleneck_index = bottleneck.bottleneck_index

    # Crowd balancing 120 employees
    employee_ids = [f"EMP-HQ-{i:03d}" for i in range(1, 121)]
    crowd_plan = dynamics.allocate_crowd_balancing(
        employee_ids=employee_ids,
        hub_station="新宿駅",
        bottleneck_index=bottleneck.bottleneck_index
    )
    tickets = arbiter.generate_evacuation_tickets(crowd_plan)
    state.last_evacuation_plan = {
        "crowd_plan": crowd_plan.model_dump(),
        "total_tickets": len(tickets),
        "tickets_preview": [t.model_dump() for t in tickets[:5]]
    }

    trajectory = visualizer.generate_disaster_trajectory(bottleneck_peak=bottleneck.bottleneck_index)
    state.last_trajectory = trajectory.model_dump()

    voice_payload = voice.dispatch_earthquake_evacuation(
        bottleneck_index=bottleneck.bottleneck_index,
        total_employees=120
    )

    duration = time.perf_counter() - t0
    state.add_log(
        "WEBHOOK", "/v1/disaster/webhook", 200, duration,
        f"[BCP緊急モード発令] 新宿駅ボトルネック: {bottleneck.bottleneck_index} (進入遮断)",
        tag="BCP_ALERT"
    )

    return {
        "bcp_transition": bcp_resp,
        "bottleneck": bottleneck.model_dump(),
        "crowd_balancing_plan": crowd_plan.model_dump(),
        "total_tickets_issued": len(tickets),
        "tickets_preview": [t.model_dump() for t in tickets[:5]],
        "trajectory": trajectory.model_dump(),
        "voice_dispatch": voice_payload.model_dump()
    }

@app.post("/v1/disaster/stranded")
def handle_stranded_rescue(payload: StrandedDistressPayload):
    """
    Stranded employee rescue: BCP partner shelter matching & turn-by-turn routing.
    """
    t0 = time.perf_counter()
    rescue_plan = arbiter.rescue_stranded_employee(
        employee_name=payload.employee_name,
        location=payload.location
    )
    state.last_stranded_rescue = rescue_plan.model_dump()

    voice_payload = voice.dispatch_stranded_rescue(
        employee_name=payload.employee_name,
        shelter_name=rescue_plan.matched_shelter_name
    )

    duration = time.perf_counter() - t0
    state.add_log(
        "POST", "/v1/disaster/stranded", 200, duration,
        f"[帰宅困難者救援] {payload.employee_name} -> {rescue_plan.matched_shelter_name}",
        tag="RESCUE"
    )

    return {
        "status": "SHELTER_MATCHED",
        "rescue_plan": rescue_plan.model_dump(),
        "voice_dispatch": voice_payload.model_dump()
    }

@app.post("/v1/simulation/run")
def run_simulation(payload: SimulationRunPayload):
    """
    Simulation Deck Runner: executes Scenario 1, 2, or 3.
    """
    sid = payload.scenario_id
    if sid == 1:
        res = simulator.run_scenario_1_finops()
        state.last_trajectory = res.visualizer_data
        state.last_approval = res.output_summary.get("e_approval_draft")
        state.add_log("POST", "/v1/simulation/run?id=1", 200, res.execution_latency_ms / 1000.0,
                      f"[SIM 1: FinOps] 4,470円 削減達成 ({res.output_summary['applicant']})", tag="SIMULATOR")
    elif sid == 2:
        res = simulator.run_scenario_2_jalert()
        state.is_bcp_mode = True
        state.bcp_activated_at = time.strftime("%Y-%m-%d %H:%M:%S")
        state.shinjuku_bottleneck_index = res.output_summary["shinjuku_bottleneck_index"]
        state.last_trajectory = res.visualizer_data
        state.last_evacuation_plan = res.output_summary
        state.add_log("POST", "/v1/simulation/run?id=2", 200, res.execution_latency_ms / 1000.0,
                      f"[SIM 2: 地震BCP] ボトルネック {res.output_summary['shinjuku_bottleneck_index']} - 3避難回廊編成", tag="SIMULATOR")
    elif sid == 3:
        res = simulator.run_scenario_3_stranded_rescue()
        state.last_stranded_rescue = res.output_summary
        state.add_log("POST", "/v1/simulation/run?id=3", 200, res.execution_latency_ms / 1000.0,
                      f"[SIM 3: 孤立救援] 避難所マッチング {res.output_summary['matched_bcp_shelter']}", tag="SIMULATOR")
    else:
        raise HTTPException(status_code=400, detail="無効な scenario_id です (1, 2, または 3)")

    return res.model_dump()

@app.post("/v1/mobility/tts")
def synthesize_tts_speech(payload: TTSRequestPayload):
    """
    Synthesizes speech using Google Gemini TTS / Google Cloud Text-to-Speech API (Japanese).
    Returns base64 audio string strictly from Google APIs.
    """
    res = voice.synthesize_speech_gcp(payload.text)
    if res and res.get("audio_base64"):
        return {
            "status": "SUCCESS",
            "audio_base64": res["audio_base64"],
            "audio_mime_type": res.get("audio_mime_type", "audio/wav"),
            "engine": res.get("engine", "GOOGLE_GEMINI_3.8_FLASH_TTS")
        }
    return {
        "status": "OFFLINE",
        "audio_base64": None,
        "audio_mime_type": "audio/wav",
        "engine": "GOOGLE_API_OFFLINE"
    }

@app.post("/v1/mobility/stt")
def transcribe_speech_gemini(payload: STTRequestPayload):
    """
    Transcribes Japanese speech using Google Gemini Multimodal Audio API.
    """
    import urllib.request, json
    clean_base64 = payload.audio_base64
    if "," in clean_base64:
        clean_base64 = clean_base64.split(",", 1)[1]
    
    mime = payload.mime_type or "audio/webm"
    body = {
        "contents": [{
            "parts": [
                {
                    "inlineData": {
                        "mimeType": mime,
                        "data": clean_base64
                    }
                },
                {
                    "text": "添付の音声を正確に日本語で文字起こししてください。文字起こししたテキストのみを1行で返し、それ以外の前置きや解説・引用符は一切出力しないでください。"
                }
            ]
        }],
        "generationConfig": {
            "temperature": 0.0
        }
    }
    for model_name in [settings.GEMINI_MODEL, "gemini-3.8-flash", "gemini-2.5-flash", "gemini-1.5-flash"]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={settings.GEMINI_API_KEY}"
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                transcript = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return {
                    "status": "SUCCESS",
                    "transcript": transcript,
                    "engine": f"GOOGLE_GEMINI_{model_name.upper()}_STT"
                }
        except Exception:
            continue
    return {
        "status": "FALLBACK",
        "transcript": "",
        "engine": "GOOGLE_STT_UNAVAILABLE"
    }

@app.get("/v1/mobility/trajectory")
def get_trajectory():
    """Returns current Tri-Line Trajectory data."""
    if state.last_trajectory:
        return state.last_trajectory
    if state.is_bcp_mode:
        return visualizer.generate_disaster_trajectory().model_dump()
    return visualizer.generate_finops_trajectory().model_dump()

@app.get("/v1/mobility/cache/stats")
def get_cache_stats():
    """Returns Pluggable Cache Adapter operational telemetry."""
    return cache_instance.get_cache_stats()

@app.post("/v1/mobility/reset")
def reset_system():
    """Resets system state back to Normal mode."""
    ingress.reset_bcp_mode()
    state.is_bcp_mode = False
    state.bcp_activated_at = None
    state.last_jalert = None
    state.shinjuku_bottleneck_index = 0.15
    state.last_approval = None
    state.last_evacuation_plan = None
    state.last_stranded_rescue = None
    state.last_trajectory = visualizer.generate_finops_trajectory().model_dump()
    state.add_log("POST", "/v1/mobility/reset", 200, 0.001, "平時FinOpsガバナンスモードへリセット完了", tag="SYSTEM")
    return {"status": "RESET_COMPLETE", "mode": "NORMAL_FINOPS"}

# Mount static frontend files
static_dir = Path(__file__).resolve().parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", response_class=HTMLResponse)
def index_page():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return index_file.read_text(encoding="utf-8")
    return "<h1>ResiliRoute v3.3 Backend Running. Frontend loading...</h1>"
