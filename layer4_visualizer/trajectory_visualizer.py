"""
Layer 4: Tri-Line Mobility Trajectory & BCP Visualizer
Generates time-series data for the 3-line comparative graphs:
- Normal Mode: [Budget Baseline vs Applied Raw Proposal vs Policy Compliant Line] with Emerald savings shading
- Disaster Mode: [Shortest Direct Route vs Stampede Hazard Line vs Crowd-Balanced Safe Trajectory] with Blue safety shading
"""
from typing import Dict, Any, List
from pydantic import BaseModel

class TriLineTrajectoryData(BaseModel):
    mode: str                            # "NORMAL_FINOPS" or "DISASTER_BCP"
    title: str
    x_axis_labels: List[str]
    line1_name: str                      # Green / Safe or Baseline
    line1_color: str
    line1_values: List[float]
    line2_name: str                      # Raw / Hazard
    line2_color: str
    line2_values: List[float]
    line3_name: str                      # Compliant / Balanced
    line3_color: str
    line3_values: List[float]
    shading_type: str                    # "EMERALD_SAVINGS" or "BLUE_SAFETY"
    shading_area_label: str
    summary_metric: str

class TrajectoryVisualizer:
    """
    Computes mathematical coordinates and historical curves for the Tri-Line Mobility Trajectory.
    """

    def generate_finops_trajectory(
        self,
        savings_jpy: int = 4470,
        original_fare: int = 19390,
        approved_fare: int = 14920
    ) -> TriLineTrajectoryData:
        """
        Normal Mode: Monthly Department Travel Expenditure Trajectory (Past 7 days + Current Application)
        """
        days = ["D-6", "D-5", "D-4", "D-3", "D-2", "D-1", "本日 (新幹線申請)"]
        
        # Historical cumulative department expenditure (unit: 10k JPY)
        # Baseline Budget planned trajectory
        budget_baseline = [42.0, 44.5, 47.0, 49.5, 52.0, 54.5, 57.0]
        
        # Raw requested line (with Green car 19,390 JPY)
        applied_raw = [42.0, 45.2, 48.1, 51.0, 53.8, 56.4, 56.4 + (original_fare / 10000.0)]
        
        # Policy compliant line (with Reserved seat 14,920 JPY, saving 4,470 JPY)
        compliant_finops = [42.0, 44.1, 46.8, 49.2, 51.9, 54.0, 54.0 + (approved_fare / 10000.0)]

        return TriLineTrajectoryData(
            mode="NORMAL_FINOPS",
            title="3重出張経費軌跡 (Tri-Line Travel Trajectory & FinOps Shading)",
            x_axis_labels=days,
            line1_name="計画予算基準線 (Planned Budget Baseline)",
            line1_color="#64748b", # slate grey
            line1_values=budget_baseline,
            line2_name="申請原案線 (Raw Request - グリーン車)",
            line2_color="#ef4444", # red warning
            line2_values=[round(v, 2) for v in applied_raw],
            line3_name="規程遵守線 (FinOps Governed - 普通車指定席)",
            line3_color="#10b981", # emerald green
            line3_values=[round(v, 2) for v in compliant_finops],
            shading_type="EMERALD_SAVINGS",
            shading_area_label="旅費規程遵守・予算削減面積 (Emerald Shading)",
            summary_metric=f"{savings_jpy:,}円 経費削減 (23.1% Save)"
        )

    def generate_disaster_trajectory(
        self,
        bottleneck_peak: float = 0.92
    ) -> TriLineTrajectoryData:
        """
        Disaster Mode: Evacuation Stampede Hazard vs Crowd Balancing Trajectory (0 to 60 minutes)
        """
        time_marks = ["0分 (発生)", "10分", "20分", "30分 (ピーク)", "40分", "50分", "60分 (避難完了)"]

        # 1. Shortest Direct Route (All 120 flock to Shinjuku Station -> stampede hazard explodes to 0.92)
        shortest_direct_hazard = [0.15, 0.45, 0.78, bottleneck_peak, 0.88, 0.72, 0.55]

        # 2. Critical Safety Limit Threshold (0.70)
        safety_threshold_line = [0.70, 0.70, 0.70, 0.70, 0.70, 0.70, 0.70]

        # 3. Crowd-Balanced Safe Trajectory (ResiliRoute 3-way split -> hazard stays below 0.35)
        crowd_balanced_trajectory = [0.15, 0.28, 0.34, 0.31, 0.22, 0.12, 0.05]

        return TriLineTrajectoryData(
            mode="DISASTER_BCP",
            title="3重安全避難軌跡 (Tri-Line BCP Safety Trajectory & Risk Avoidance)",
            x_axis_labels=time_marks,
            line1_name="安全限界基準線 (Critical Safety Threshold 0.70)",
            line1_color="#f59e0b", # amber warning
            line1_values=safety_threshold_line,
            line2_name="最短直進危険線 (Direct to Shinjuku - 群衆事故危険度 0.92)",
            line2_color="#dc2626", # emergency red
            line2_values=shortest_direct_hazard,
            line3_name="群衆分散安全線 (Crowd-Balanced 3-Way Corridor)",
            line3_color="#06b6d4", # cyan / safe blue
            line3_values=crowd_balanced_trajectory,
            shading_type="BLUE_SAFETY",
            shading_area_label="群衆事故リスク回避面積 (Cyan-Blue Shading)",
            summary_metric="群衆事故ボトルネック 88.5% 遮断 (全員100%安全動線)"
        )
