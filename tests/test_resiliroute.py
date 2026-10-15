"""
Comprehensive Test Suite for ResiliRoute v3.3 (Japanese Localization)
Tests all 6 architectural layers, mathematical models, Ekispert MCP client, and simulation scenarios.
"""
import pytest
from fastapi.testclient import TestClient

from layer0_ingress import IngressPerimeter, ConfidentialTripDLP, JAlertPayload
from layer0_5_dynamics import MobilityDynamicsEngine, TripHistoryItem
from cache_adapter import LocalMemoryMobilityCache, VertexAIMobilityCache
from layer2_mobility_core import EkispertMCPClient, CorporateTravelPolicyEngine
from layer3_arbiter import ChiefMobilityArbiter
from layer4_visualizer import TrajectoryVisualizer
from layer5_voice_dispatcher import VoiceDispatcher
from simulator import SyntheticSimulator
from server import app

client = TestClient(app)

# ----------------- LAYER 0 TESTS ----------------- #
def test_dlp_masking():
    dlp = ConfidentialTripDLP()
    raw = "来週東京出張の際に法人カード 1111-2222-3333-4444 を利用し、極秘プロジェクトオデッセイ関連のミーティングです。"
    result = dlp.sanitize(raw)
    assert "[CORP_CARD_***4444]" in result.sanitized_text
    assert "[CONFIDENTIAL_PROJECT_CODE]" in result.sanitized_text
    assert len(result.masked_entities) >= 2

def test_jalert_sub_100ms_transition():
    ingress = IngressPerimeter()
    payload = JAlertPayload(magnitude=6.2, epicenter="東京湾 (Tokyo Bay)")
    result = ingress.trigger_jalert(payload)
    assert result["status"] == "BCP_MODE_ACTIVATED"
    assert result["sub_100ms_guarantee"] is True
    assert ingress.is_bcp_mode is True

# ----------------- LAYER 0.5 TESTS ----------------- #
def test_transit_debt_integral():
    engine = MobilityDynamicsEngine()
    history = [
        TripHistoryItem(trip_id="T1", date_offset_days=1.0, travel_hours=5.0, is_late_night=False, origin="東京", destination="博多"),
        TripHistoryItem(trip_id="T2", date_offset_days=2.0, travel_hours=6.0, is_late_night=True, origin="東京", destination="大阪")
    ]
    res = engine.calculate_transit_debt("EMP-1", "田中 主任", "主任", history)
    assert res.transit_debt_hours > 0
    assert res.threshold_hours == 15.0

def test_bottleneck_integral_and_shutdown():
    engine = MobilityDynamicsEngine()
    inflows = [500, 1000, 2000, 3000]
    caps = [1000, 200, 0, 0]
    state = engine.calculate_bottleneck_integral("新宿駅", inflows, caps, 5000)
    assert state.bottleneck_index > 0.70
    assert state.is_shutdown is True

def test_crowd_balancing_allocation():
    engine = MobilityDynamicsEngine()
    emp_ids = [f"EMP-{i}" for i in range(120)]
    plan = engine.allocate_crowd_balancing(emp_ids, "新宿駅", 0.92)
    assert len(plan.groups) == 3
    assert sum(g.target_count for g in plan.groups) == 120
    assert plan.is_hub_station_shutdown is True

# ----------------- CACHE ADAPTER TESTS ----------------- #
def test_local_memory_cache():
    cache = LocalMemoryMobilityCache()
    cache.set("test_key", "test_value", ttl_seconds=10)
    assert cache.get("test_key") == "test_value"
    policy_doc = cache.get_policy_document()
    assert "社内旅費規程第14条" in policy_doc
    stats = cache.get_cache_stats()
    assert stats["cost_usd"] == 0.0

def test_vertex_ai_cache_adapter():
    cache = VertexAIMobilityCache("test-proj", "asia-northeast1")
    stats = cache.get_cache_stats()
    assert stats["cached_tokens"] > 32768
    assert stats["is_cloud_cached"] is True

# ----------------- LAYER 2 & POLICY TESTS ----------------- #
def test_ekispert_shinkansen_query():
    client_mcp = EkispertMCPClient()
    courses = client_mcp.search_shinkansen_courses(origin="東京", destination="新大阪")
    assert len(courses) > 0
    c0 = courses[0]
    assert c0.total_green_jpy > c0.total_reserved_jpy
    assert c0.potential_savings_jpy > 0

def test_corporate_travel_policy():
    engine = CorporateTravelPolicyEngine()
    # Tanaka (Assistant Manager) requesting Green car
    eval_res = engine.evaluate_request("田中 主任", "主任", "GREEN", green_fare=19390, reserved_fare=14920)
    assert eval_res.is_compliant is False
    assert eval_res.cost_saving_jpy == 4470
    assert eval_res.recommended_seat_type == "普通車指定席 (Standard Reserved)"

# ----------------- LAYER 3 ARBITER TESTS ----------------- #
def test_arbiter_and_stranded_rescue():
    arbiter = ChiefMobilityArbiter()
    rescue = arbiter.rescue_stranded_employee("佐藤 課長", "六本木ヒルズ付近道路")
    assert "森タワー" in rescue.matched_shelter_name
    assert rescue.distance_meters == 300
    assert len(rescue.turn_by_turn_steps) == 4
    assert rescue.safety_verification_status == "SAFE_CHECK_CONFIRMED"

# ----------------- SIMULATOR TESTS ----------------- #
def test_scenario_1_finops_simulation():
    sim = SyntheticSimulator()
    res = sim.run_scenario_1_finops()
    assert res.status == "SUCCESS"
    assert res.output_summary["cost_savings_jpy"] == 4470
    assert "visualizer_data" in res.model_dump()

def test_scenario_2_jalert_simulation():
    sim = SyntheticSimulator()
    res = sim.run_scenario_2_jalert()
    assert res.status == "SUCCESS"
    assert res.output_summary["shinjuku_bottleneck_index"] >= 0.70
    assert res.output_summary["total_evacuees"] == 120

def test_scenario_3_stranded_simulation():
    sim = SyntheticSimulator()
    res = sim.run_scenario_3_stranded_rescue()
    assert res.status == "SUCCESS"
    assert "六本木ヒルズ 森タワー" in res.output_summary["matched_bcp_shelter"]

# ----------------- FASTAPI SERVER TESTS ----------------- #
def test_api_status_and_reset():
    r1 = client.get("/v1/mobility/status")
    assert r1.status_code == 200
    
    r2 = client.post("/v1/mobility/reset")
    assert r2.status_code == 200
    assert r2.json()["mode"] == "NORMAL_FINOPS"

def test_api_run_simulation():
    r = client.post("/v1/simulation/run", json={"scenario_id": 1})
    assert r.status_code == 200
    data = r.json()
    assert data["scenario_id"] == 1
    assert data["output_summary"]["cost_savings_jpy"] == 4470

def test_api_jalert_webhook():
    payload = {
        "event_id": "TEST-JALERT-01",
        "magnitude": 6.2,
        "epicenter": "東京湾 (Tokyo Bay)",
        "max_intensity": "6弱",
        "affected_areas": ["東京都"]
    }
    r = client.post("/v1/disaster/webhook", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["bcp_transition"]["status"] == "BCP_MODE_ACTIVATED"
    assert data["bottleneck"]["bottleneck_index"] >= 0.70

def test_api_tts_endpoint():
    r = client.post("/v1/mobility/tts", json={"text": "避難テスト"})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in ["SUCCESS", "OFFLINE"]
    if data["status"] == "SUCCESS":
        assert data["audio_base64"] is not None
        assert data["audio_mime_type"] in ["audio/wav", "audio/mp3"]

def test_api_mobility_natural_language_intents():
    client.post("/v1/mobility/reset")
    # 1. FinOps Travel
    r1 = client.post("/v1/mobility/request", json={
        "message": "来週火曜日に東京から新大阪への出張ですが、のぞみグリーン車で手配してください。法人カード 4520-1122-3344-9988"
    })
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["intent_type"] == "TRAVEL_BOOKING"
    assert d1["policy_compliance"]["cost_saving_jpy"] == 4470

    # 2. Stranded Rescue
    r2 = client.post("/v1/mobility/request", json={
        "message": "六本木ヒルズ付近で外出ミーティング終了後に地下鉄全面運休のため道路で孤立しました。避難所の案内をお願いします。"
    })
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["intent_type"] == "STRANDED_RESCUE"
    assert "rescue_plan" in d2
    assert "森タワー" in d2["rescue_plan"]["matched_shelter_name"]

    # 3. Earthquake BCP
    r3 = client.post("/v1/mobility/request", json={
        "message": "新宿本社 社員120名 緊急避難回廊編成指令を発令"
    })
    assert r3.status_code == 200
    d3 = r3.json()
    assert d3["intent_type"] == "DISASTER_EVACUATION"
    assert d3["bottleneck"]["bottleneck_index"] >= 0.70
