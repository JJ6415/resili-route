"""
Layer 2: Mobility Native Core - Corporate Travel Policy RAG & Rule Validator
Evaluates company travel guidelines deterministically.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class PolicyComplianceEvaluation(BaseModel):
    is_compliant: bool
    employee_name: str
    employee_rank: str
    requested_seat_type: str
    recommended_seat_type: str
    original_fare_jpy: int
    approved_fare_jpy: int
    cost_saving_jpy: int
    policy_article: str
    decision_reason: str
    transit_debt_hours: float
    transit_debt_compliant: bool
    needs_hotel_stay: bool

class CorporateTravelPolicyEngine:
    """
    Deterministic rule engine aligned with Company Travel Policy Article 14.
    """
    RANK_HIERARCHY = {
        # Japanese Ranks
        "社員": 1,
        "主任": 2,
        "係長": 2,
        "課長": 3,
        "次長": 4,
        "部長": 5,
        "役員": 6,
        "取締役": 6,
        "代表取締役": 7,
        # English Aliases
        "Staff": 1,
        "Assistant Manager": 2,
        "Manager": 3,
        "Senior Manager": 4,
        "General Manager": 5,
        "Director": 6,
        "CEO": 7
    }

    HOTEL_LIMITS = {
        "社員": 12000,
        "主任": 12000,
        "課長": 15000,
        "次長": 15000,
        "部長": 18000,
        "役員": 25000
    }

    def evaluate_request(
        self,
        employee_name: str,
        employee_rank: str,
        requested_seat: str,            # "GREEN", "RESERVED", "FREE"
        green_fare: int = 19390,
        reserved_fare: int = 14920,
        transit_debt_hours: float = 6.4
    ) -> PolicyComplianceEvaluation:
        rank_level = self.RANK_HIERARCHY.get(employee_rank, 2)
        green_allowed = rank_level >= 6  # Only Director / Executive allowed
        transit_debt_compliant = transit_debt_hours < 15.0
        needs_hotel = not transit_debt_compliant

        is_green_requested = requested_seat.upper() in ["GREEN", "グリーン", "グリーン車"]

        if is_green_requested and not green_allowed:
            # Policy Violation -> Automatic FinOps Downgrade to Reserved Seat
            cost_saving = green_fare - reserved_fare
            return PolicyComplianceEvaluation(
                is_compliant=False,
                employee_name=employee_name,
                employee_rank=employee_rank,
                requested_seat_type="グリーン車 (Green Car)",
                recommended_seat_type="普通車指定席 (Standard Reserved)",
                original_fare_jpy=green_fare,
                approved_fare_jpy=reserved_fare,
                cost_saving_jpy=cost_saving,
                policy_article="社内旅費規程第14条（新幹線利用基準）",
                decision_reason=f"{employee_rank}の役職はグリーン車利用対象外のため、規程に基づき普通車指定席へ自動調整され、{cost_saving:,}円の経費が削減されました。",
                transit_debt_hours=transit_debt_hours,
                transit_debt_compliant=transit_debt_compliant,
                needs_hotel_stay=needs_hotel
            )

        # Compliant
        return PolicyComplianceEvaluation(
            is_compliant=True,
            employee_name=employee_name,
            employee_rank=employee_rank,
            requested_seat_type=requested_seat,
            recommended_seat_type=requested_seat,
            original_fare_jpy=reserved_fare if not is_green_requested else green_fare,
            approved_fare_jpy=reserved_fare if not is_green_requested else green_fare,
            cost_saving_jpy=0,
            policy_article="社内旅費規程第14条遵守",
            decision_reason="社内旅費規程の利用基準を満たしています。",
            transit_debt_hours=transit_debt_hours,
            transit_debt_compliant=transit_debt_compliant,
            needs_hotel_stay=needs_hotel
        )
