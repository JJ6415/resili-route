"""
Layer 0.5: Mobility Dynamics & Crowd Balancing Engine
Implements:
1. Cumulative Transit Debt Integral (Fatigue / Burnout model)
2. Station Bottleneck Integral (Crowd stampede risk model)
3. 3-Group Crowd Balancing Allocation Algorithm
4. Department Travel Budget Acceleration & Burn Rate
"""
from typing import List, Dict, Any, Optional
import math
import time
from pydantic import BaseModel, Field

class TripHistoryItem(BaseModel):
    trip_id: str
    date_offset_days: float  # days ago (0 = today, 2 = 2 days ago)
    travel_hours: float
    is_late_night: bool = False  # after 22:00
    origin: str
    destination: str

class TransitDebtResult(BaseModel):
    employee_id: str
    employee_name: str
    rank: str
    transit_debt_hours: float
    threshold_hours: float = 15.0
    is_exhausted: bool
    burnout_risk_level: str  # "LOW", "MODERATE", "CRITICAL"
    recommendation: str

class StationBottleneckState(BaseModel):
    station_name: str
    current_inflow_rate: float        # people per minute
    evacuation_capacity: float        # people per minute
    max_safety_capacity: float        # max platform safe capacity
    bottleneck_index: float           # 0.0 ~ 1.0+
    threshold: float = 0.70
    is_shutdown: bool
    status_label: str                 # "NORMAL", "CAUTION", "CRITICAL_SHUTDOWN"
    simulation_steps: List[Dict[str, Any]] = []

class CrowdGroupAllocation(BaseModel):
    group_id: str
    group_name: str
    target_count: int
    assigned_employees: List[str]
    route_description: str
    hazard_reduction: float           # % risk reduction
    destination: str

class CrowdBalancingPlan(BaseModel):
    total_employees: int
    hub_station: str
    bottleneck_index: float
    is_hub_station_shutdown: bool
    groups: List[CrowdGroupAllocation]
    timestamp: str

class MobilityDynamicsEngine:
    """
    Continuous state-space mathematical modeling for transit fatigue and crowd dynamics.
    """
    def __init__(self, tau_recovery_days: float = 3.5, late_night_weight: float = 1.5):
        self.tau_recovery_days = tau_recovery_days
        self.late_night_weight = late_night_weight

    def calculate_transit_debt(
        self,
        employee_id: str,
        employee_name: str,
        rank: str,
        trip_history: List[TripHistoryItem]
    ) -> TransitDebtResult:
        """
        Calculates TransitDebt(t) = sum_{i=1}^N Delta TravelHours_i * omega_{late_night} * exp(-(t - t_i)/tau_{recovery})
        """
        debt = 0.0
        for item in trip_history:
            weight = self.late_night_weight if item.is_late_night else 1.0
            decay = math.exp(-item.date_offset_days / self.tau_recovery_days)
            debt += item.travel_hours * weight * decay

        debt = round(debt, 2)
        is_exhausted = debt >= 15.0
        
        if debt < 8.0:
            risk = "LOW"
            rec = "正常出張承認可能（規程範囲内）"
        elif debt < 15.0:
            risk = "MODERATE"
            rec = "移動疲労蓄積注意（近距離出張推奨）"
        else:
            risk = "CRITICAL"
            rec = "疲労負債15時間超過: 日帰り出張不許可・前日宿泊またはオンライン会議必須推奨"

        return TransitDebtResult(
            employee_id=employee_id,
            employee_name=employee_name,
            rank=rank,
            transit_debt_hours=debt,
            threshold_hours=15.0,
            is_exhausted=is_exhausted,
            burnout_risk_level=risk,
            recommendation=rec
        )

    def calculate_bottleneck_integral(
        self,
        station_name: str,
        inflow_series: List[float],      # InflowRate per minute
        evacuation_capacity_series: List[float], # Evacuation capacity per minute
        max_station_safety_capacity: float,
        dt_minutes: float = 1.0
    ) -> StationBottleneckState:
        """
        Calculates:
        BottleneckIndex(s, t) = int_{t_0}^t (InflowRate(s, tau) - EvacuationCapacity(s, tau)) d tau / MaxStationSafetyCapacity(s)
        """
        cumulative_crowd = 0.0
        steps = []
        n = min(len(inflow_series), len(evacuation_capacity_series))
        
        for i in range(n):
            net_inflow = inflow_series[i] - evacuation_capacity_series[i]
            cumulative_crowd = max(0.0, cumulative_crowd + net_inflow * dt_minutes)
            current_index = round(cumulative_crowd / max_station_safety_capacity, 3)
            steps.append({
                "minute": i + 1,
                "inflow": inflow_series[i],
                "evacuation_cap": evacuation_capacity_series[i],
                "net_inflow": net_inflow,
                "accumulated_crowd": round(cumulative_crowd, 1),
                "bottleneck_index": current_index
            })

        final_index = steps[-1]["bottleneck_index"] if steps else 0.0
        is_shutdown = final_index >= 0.70
        
        status_label = "NORMAL"
        if final_index >= 0.70:
            status_label = "CRITICAL_SHUTDOWN"
        elif final_index >= 0.40:
            status_label = "CAUTION"

        return StationBottleneckState(
            station_name=station_name,
            current_inflow_rate=inflow_series[-1] if inflow_series else 0.0,
            evacuation_capacity=evacuation_capacity_series[-1] if evacuation_capacity_series else 0.0,
            max_safety_capacity=max_station_safety_capacity,
            bottleneck_index=final_index,
            threshold=0.70,
            is_shutdown=is_shutdown,
            status_label=status_label,
            simulation_steps=steps
        )

    def allocate_crowd_balancing(
        self,
        employee_ids: List[str],
        hub_station: str = "新宿駅 (Shinjuku Station)",
        bottleneck_index: float = 0.92
    ) -> CrowdBalancingPlan:
        """
        Divides employees into 3 intelligent evacuation corridors:
        Group A (Western Tokyo): Meiji Jingu green corridor walking route
        Group B (Eastern Tokyo): Hatsudai emergency bus route
        Group C (Remote / Vulnerable): HQ 4th floor seismic shelter & emergency rations
        """
        total = len(employee_ids)
        split = total // 3
        group_a_ids = employee_ids[:split]
        group_b_ids = employee_ids[split:2*split]
        group_c_ids = employee_ids[2*split:]

        groups = [
            CrowdGroupAllocation(
                group_id="GROUP_A",
                group_name="グループA（東京西部・近距離避難班）",
                target_count=len(group_a_ids),
                assigned_employees=group_a_ids,
                route_description="新宿駅進入遮断 ──▶ 明治神宮外郭緑道迂回誘導（混雑回避）",
                hazard_reduction=88.5,
                destination="明治神宮北門 安心緑地帯"
            ),
            CrowdGroupAllocation(
                group_id="GROUP_B",
                group_name="グループB（東京東部・交通結節班）",
                target_count=len(group_b_ids),
                assigned_employees=group_b_ids,
                route_description="新宿南側徒歩 ──▶ 初台方面緊急臨時路線バス乗車",
                hazard_reduction=82.0,
                destination="初台 緊急モビリティ・バスゾーン"
            ),
            CrowdGroupAllocation(
                group_id="GROUP_C",
                group_name="グループC（遠距離・社内拠点残留班）",
                target_count=len(group_c_ids),
                assigned_employees=group_c_ids,
                route_description="無理な屋外帰宅禁止 ──▶ 本社4階特等級耐震防災エリア残留＆非常食受取",
                hazard_reduction=95.0,
                destination="東京本社 4Fセーフティバンカーゾーン"
            )
        ]

        return CrowdBalancingPlan(
            total_employees=total,
            hub_station=hub_station,
            bottleneck_index=bottleneck_index,
            is_hub_station_shutdown=bottleneck_index >= 0.70,
            groups=groups,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S+09:00")
        )

    def calculate_budget_acceleration(
        self,
        monthly_budget: float = 20_000_000, # 20M JPY
        spent_amount: float = 8_500_000,     # 8.5M JPY (42.5%)
        day_of_month: int = 12,
        total_days_in_month: int = 30
    ) -> Dict[str, Any]:
        """
        Calculates travel budget burn rate and FinOps acceleration.
        """
        burn_ratio = round((spent_amount / monthly_budget) * 100, 1)
        expected_ratio = round((day_of_month / total_days_in_month) * 100, 1)
        acceleration_index = round(burn_ratio / max(1.0, expected_ratio), 2)
        
        status = "HEALTHY"
        if acceleration_index > 1.25:
            status = "ACCELERATING_FAST"
        elif acceleration_index < 0.85:
            status = "UNDER_BUDGET"

        return {
            "monthly_budget_jpy": monthly_budget,
            "spent_amount_jpy": spent_amount,
            "burn_ratio_pct": burn_ratio,
            "calendar_elapsed_pct": expected_ratio,
            "acceleration_index": acceleration_index,
            "budget_status": status,
            "audit_urgency": "HIGH" if acceleration_index > 1.2 else "NORMAL"
        }
