"""
Synthetic Disaster & Travel Injector (Non-Mock Runtime Simulator)
Injects realistic employee travel requests, J-Alert earthquake webhooks, and stranded mobility distress packets in Japanese.
"""
from typing import Dict, Any, List
import time
import logging
from pydantic import BaseModel

from layer0_ingress import IngressPerimeter, JAlertPayload
from layer0_5_dynamics import MobilityDynamicsEngine, TripHistoryItem
from layer1_orchestrator import TravelCrisisOrchestrator
from layer2_mobility_core import EkispertMCPClient, CorporateTravelPolicyEngine
from layer3_arbiter import ChiefMobilityArbiter
from layer4_visualizer import TrajectoryVisualizer
from layer5_voice_dispatcher import VoiceDispatcher

logger = logging.getLogger("SyntheticSimulator")

class SimulationExecutionResult(BaseModel):
    scenario_id: int
    scenario_name: str
    execution_latency_ms: float
    status: str
    layer_trace: List[Dict[str, Any]]
    output_summary: Dict[str, Any]
    visualizer_data: Dict[str, Any]
    voice_dispatch: Dict[str, Any]

class SyntheticSimulator:
    """
    Simulation Injector driving the 3 core enterprise scenarios.
    """
    def __init__(self):
        self.ingress = IngressPerimeter()
        self.dynamics = MobilityDynamicsEngine()
        self.orchestrator = TravelCrisisOrchestrator()
        self.ekispert = EkispertMCPClient()
        self.policy = CorporateTravelPolicyEngine()
        self.arbiter = ChiefMobilityArbiter()
        self.visualizer = TrajectoryVisualizer()
        self.voice = VoiceDispatcher()

    def run_scenario_1_finops(self) -> SimulationExecutionResult:
        """
        Scenario 1: Daily Travel FinOps
        Applicant: Tanaka (田中 主任)
        Action: Requests Shinkansen Nozomi Green Car ("来週火曜日に東京から新大阪への出張ですが...")
        Outcome: Ekispert MCP query + Policy Article 14 -> Downshift to Reserved Seat -> 4,470 JPY saved.
        """
        start = time.perf_counter()
        trace = []

        # 1. Raw Message Ingress & DLP
        raw_msg = "来週火曜日に東京から新大阪へのミーティング出張ですが、疲労防止のため新幹線「のぞみ」グリーン車を手配してください。法人カード 4520-1122-3344-9988 で決済お願いします。"
        sanitized = self.ingress.process_travel_request(raw_msg)
        trace.append({
            "layer": "Layer 0 (Ingress Perimeter & DLP)",
            "action": "インライン個人情報・カード番号マスキング",
            "sanitized_text": sanitized.sanitized_text,
            "masked_entities_count": len(sanitized.masked_entities),
            "latency_ms": sanitized.latency_ms
        })

        # 2. Layer 0.5 Mobility Dynamics (Transit Debt & Budget Acceleration)
        history = [
            TripHistoryItem(trip_id="T1", date_offset_days=3.0, travel_hours=2.5, is_late_night=False, origin="東京", destination="名古屋"),
            TripHistoryItem(trip_id="T2", date_offset_days=7.0, travel_hours=3.0, is_late_night=True, origin="東京", destination="仙台")
        ]
        debt_result = self.dynamics.calculate_transit_debt("EMP-2041", "田中 主任", "主任", history)
        budget_accel = self.dynamics.calculate_budget_acceleration()
        trace.append({
            "layer": "Layer 0.5 (Mobility Dynamics)",
            "transit_debt_hours": debt_result.transit_debt_hours,
            "burnout_risk": debt_result.burnout_risk_level,
            "budget_burn_ratio": f"{budget_accel['burn_ratio_pct']}%"
        })

        # 3. Layer 1 Orchestrator
        directive = self.orchestrator.orchestrate_request(sanitized.sanitized_text, is_bcp_mode=False)
        trace.append({
            "layer": "Layer 1 (Travel Orchestrator)",
            "intent": directive.intent.intent_type,
            "origin": directive.intent.origin,
            "destination": directive.intent.destination,
            "requested_seat": directive.intent.requested_seat,
            "cache_applied": directive.cached_policy_applied
        })

        # 4. Layer 2 Mobility Native Core (Ekispert MCP + Policy Check)
        courses = self.ekispert.search_shinkansen_courses(
            origin=directive.intent.origin,
            destination=directive.intent.destination,
            date=directive.intent.departure_date,
            time=directive.intent.departure_time
        )
        selected_course = courses[0]

        compliance = self.policy.evaluate_request(
            employee_name="田中 主任",
            employee_rank="主任",
            requested_seat="GREEN",
            green_fare=selected_course.total_green_jpy,
            reserved_fare=selected_course.total_reserved_jpy,
            transit_debt_hours=debt_result.transit_debt_hours
        )
        trace.append({
            "layer": "Layer 2 (Mobility Native Core & Ekispert MCP)",
            "train": selected_course.train_name,
            "green_fare_jpy": selected_course.total_green_jpy,
            "reserved_fare_jpy": selected_course.total_reserved_jpy,
            "compliant": compliance.is_compliant,
            "cost_saving_jpy": compliance.cost_saving_jpy
        })

        # 5. Layer 3 Chief Arbiter & Governor
        approval_draft = self.arbiter.arbitrate_travel_application(
            compliance=compliance,
            course=selected_course,
            origin="東京 (Tokyo)",
            destination="新大阪 (Shin-Osaka)"
        )
        trace.append({
            "layer": "Layer 3 (Chief Mobility Arbiter)",
            "draft_id": approval_draft.draft_id,
            "status": approval_draft.status,
            "justification": approval_draft.justification
        })

        # 6. Layer 4 Tri-Line Trajectory
        trajectory = self.visualizer.generate_finops_trajectory(
            savings_jpy=compliance.cost_saving_jpy,
            original_fare=compliance.original_fare_jpy,
            approved_fare=compliance.approved_fare_jpy
        )

        # 7. Layer 5 Voice Dispatcher
        voice = self.voice.dispatch_finops_approval(
            employee_name="田中 主任",
            savings_jpy=compliance.cost_saving_jpy,
            approved_seat=compliance.recommended_seat_type
        )

        elapsed_ms = (time.perf_counter() - start) * 1000.0

        return SimulationExecutionResult(
            scenario_id=1,
            scenario_name="シナリオ1: 平時出張FinOpsガバナンス (田中主任 新幹線出張申請)",
            execution_latency_ms=round(elapsed_ms, 2),
            status="SUCCESS",
            layer_trace=trace,
            output_summary={
                "applicant": "田中 主任 (Assistant Manager)",
                "route": "東京 ──▶ 新大阪 (新幹線 のぞみ)",
                "original_request": "グリーン車 (19,390円)",
                "approved_selection": "普通車指定席 (14,920円)",
                "cost_savings_jpy": compliance.cost_saving_jpy,
                "savings_pct": "23.1%",
                "slack_notification": approval_draft.slack_notification_text,
                "e_approval_draft": approval_draft.model_dump()
            },
            visualizer_data=trajectory.model_dump(),
            voice_dispatch=voice.model_dump()
        )

    def run_scenario_2_jalert(self) -> SimulationExecutionResult:
        """
        Scenario 2: Quake J-Alert & Crowd Balancing
        Disaster: M6.2 Earthquake Webhook in Tokyo Bay
        Victims: 120 HQ employees in Shinjuku
        Outcome: 0.1s BCP mode transition -> Shinjuku Bottleneck 0.92 detected -> 3-way Crowd Balancing tickets dispatched.
        """
        start = time.perf_counter()
        trace = []

        # 1. J-Alert Webhook Ingress
        jalert = JAlertPayload(
            magnitude=6.2,
            epicenter="東京湾 (Tokyo Bay)",
            max_intensity="6弱 (Upper 6)"
        )
        bcp_transition = self.ingress.trigger_jalert(jalert)
        trace.append({
            "layer": "Layer 0 (Ingress Perimeter)",
            "action": "J-Alert 緊急地震速報 Webhook受信",
            "status": bcp_transition["status"],
            "transition_latency_ms": bcp_transition["transition_latency_ms"],
            "sub_100ms_guarantee": bcp_transition["sub_100ms_guarantee"]
        })

        # 2. Layer 2 Check Disruptions
        disruptions = self.ekispert.check_railway_disruptions(is_disaster_mode=True)
        suspended_lines = [d.line_name for d in disruptions if d.is_suspended]
        trace.append({
            "layer": "Layer 2 (Ekispert Transit Disruption Monitor)",
            "suspended_lines": suspended_lines,
            "network_status": "全主要路線運転見合わせ (ALL_MAJOR_LINES_SUSPENDED)"
        })

        # 3. Layer 0.5 Shinjuku Station Bottleneck Integral
        inflow = [200, 500, 1000, 1600, 2400, 3200, 3800]
        evac_cap = [1200, 400, 50, 0, 0, 0, 0] # drops to 0 due to train stoppage
        bottleneck = self.dynamics.calculate_bottleneck_integral(
            station_name="新宿駅 (Shinjuku Station)",
            inflow_series=inflow,
            evacuation_capacity_series=evac_cap,
            max_station_safety_capacity=12000
        )
        # 120 employees crowd partition
        employee_ids = [f"EMP-HQ-{i:03d}" for i in range(1, 121)]
        crowd_plan = self.dynamics.allocate_crowd_balancing(
            employee_ids=employee_ids,
            hub_station="新宿駅",
            bottleneck_index=bottleneck.bottleneck_index
        )
        trace.append({
            "layer": "Layer 0.5 (Crowd Dynamics & Bottleneck Integral)",
            "bottleneck_index": bottleneck.bottleneck_index,
            "is_shutdown": bottleneck.is_shutdown,
            "groups_formed": len(crowd_plan.groups),
            "allocated_headcount": crowd_plan.total_employees
        })

        # 4. Layer 3 Governor Ticket Dispatch
        tickets = self.arbiter.generate_evacuation_tickets(crowd_plan)
        trace.append({
            "layer": "Layer 3 (Chief BCP Governor)",
            "tickets_generated": len(tickets),
            "sample_ticket": tickets[0].model_dump()
        })

        # 5. Layer 4 Disaster Trajectory
        trajectory = self.visualizer.generate_disaster_trajectory(bottleneck_peak=bottleneck.bottleneck_index)

        # 6. Layer 5 Voice Dispatch
        voice = self.voice.dispatch_earthquake_evacuation(
            bottleneck_index=bottleneck.bottleneck_index,
            total_employees=120
        )

        elapsed_ms = (time.perf_counter() - start) * 1000.0

        return SimulationExecutionResult(
            scenario_id=2,
            scenario_name="シナリオ2: 地震J-Alert＆群衆分散 (首都圏震度6強および新宿駅避難回廊編成)",
            execution_latency_ms=round(elapsed_ms, 2),
            status="SUCCESS",
            layer_trace=trace,
            output_summary={
                "alert": "首都圏規模 M6.2 地震 (最大震度 6弱)",
                "bcp_transition_time_ms": bcp_transition["transition_latency_ms"],
                "shinjuku_bottleneck_index": bottleneck.bottleneck_index,
                "station_status": "CRITICAL_SHUTDOWN (進入全面遮断)",
                "total_evacuees": 120,
                "group_a": f"{crowd_plan.groups[0].target_count}名 ──▶ {crowd_plan.groups[0].destination}",
                "group_b": f"{crowd_plan.groups[1].target_count}名 ──▶ {crowd_plan.groups[1].destination}",
                "group_c": f"{crowd_plan.groups[2].target_count}名 ──▶ {crowd_plan.groups[2].destination}",
                "total_tickets_issued": len(tickets),
                "tickets_sample": [t.model_dump() for t in tickets[:3]]
            },
            visualizer_data=trajectory.model_dump(),
            voice_dispatch=voice.model_dump()
        )

    def run_scenario_3_stranded_rescue(self) -> SimulationExecutionResult:
        """
        Scenario 3: Stranded Rescue
        Worker: Manager Sato (佐藤 課長) in Roppongi
        Distress: Stranded due to subway shutdown
        Outcome: Ekispert + BCP DB match 300m partner shelter (Mori Tower 3F) -> Turn-by-Turn navigation + QR pass.
        """
        start = time.perf_counter()
        trace = []

        # 1. Distress Message Ingress
        distress_msg = "六本木ヒルズ付近で外出ミーティング終了後に地下鉄全面運休のため道路で孤立しました。避難所の案内をお願いします。"
        sanitized = self.ingress.process_travel_request(distress_msg)
        trace.append({
            "layer": "Layer 0 (Ingress Perimeter)",
            "message": sanitized.sanitized_text,
            "latency_ms": sanitized.latency_ms
        })

        # 2. Layer 1 Crisis Orchestrator
        directive = self.orchestrator.orchestrate_request(distress_msg, is_bcp_mode=True)
        trace.append({
            "layer": "Layer 1 (Crisis Orchestrator)",
            "intent": directive.intent.intent_type,
            "target": directive.intent.employee_name,
            "origin": directive.intent.origin
        })

        # 3. Layer 3 Stranded Rescue & Turn-by-Turn Navigation
        rescue_plan = self.arbiter.rescue_stranded_employee(
            employee_name="佐藤 課長",
            location="六本木ヒルズ付近道路 (Roppongi Hills)"
        )
        trace.append({
            "layer": "Layer 3 (BCP Governor Rescue Engine)",
            "matched_shelter": rescue_plan.matched_shelter_name,
            "distance_meters": rescue_plan.distance_meters,
            "walking_time_minutes": rescue_plan.walking_time_minutes,
            "steps_count": len(rescue_plan.turn_by_turn_steps),
            "qr_pass": rescue_plan.mobile_qr_pass
        })

        # 4. Layer 4 Visualization
        trajectory = self.visualizer.generate_disaster_trajectory(bottleneck_peak=0.85)

        # 5. Layer 5 Voice Dispatch
        voice = self.voice.dispatch_stranded_rescue(
            employee_name="佐藤 課長",
            shelter_name=rescue_plan.matched_shelter_name
        )

        elapsed_ms = (time.perf_counter() - start) * 1000.0

        return SimulationExecutionResult(
            scenario_id=3,
            scenario_name="シナリオ3: 帰宅困難者救援 (六本木外勤孤立者 緊急避難誘導)",
            execution_latency_ms=round(elapsed_ms, 2),
            status="SUCCESS",
            layer_trace=trace,
            output_summary={
                "stranded_employee": "佐藤 課長 (Marketing Manager)",
                "location": "六本木ヒルズ付近 (Roppongi Hills)",
                "matched_bcp_shelter": rescue_plan.matched_shelter_name,
                "distance": f"{rescue_plan.distance_meters}m (徒歩 {rescue_plan.walking_time_minutes}分)",
                "seismic_grade": rescue_plan.seismic_grade,
                "turn_by_turn_guidance": rescue_plan.turn_by_turn_steps,
                "qr_access_ticket": rescue_plan.mobile_qr_pass,
                "safety_status": rescue_plan.safety_verification_status
            },
            visualizer_data=trajectory.model_dump(),
            voice_dispatch=voice.model_dump()
        )
