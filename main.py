from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict
import random
import math
import time

class AlertLevel(Enum):
    STANDARD = "standard"
    HEIGHTENED = "heightened"
    CRITICAL = "critical"
    COMBAT = "combat"

class MissionType(Enum):
    RECON = "recon"
    DIRECT_ACTION = "direct_action"
    AMBUSH = "ambush"
    WITHDRAWAL = "withdrawal"
    HOLDING = "holding"

class ThreatType(Enum):
    AMBUSH = "ambush"
    SNIPER = "sniper"
    IED = "ied"
    DIRECT_FIRE = "direct_fire"
    INDIRECT_FIRE = "indirect_fire"
    PURSUIT = "pursuit"

class SoldierStatus(Enum):
    NORMAL = "normal"
    WOUNDED = "wounded"
    EXHAUSTED = "exhausted"
    PANICKED = "panicked"
    FOCUSED = "focused"
    TUNNEL_VISION = "tunnel_vision"

@dataclass
class PhysiologicalMetrics:
    heart_rate_bpm: float
    respiratory_rate: float
    pupil_dilation: float
    tremor_intensity: float
    auditory_threshold: float
    visual_field: float
    reaction_time_ms: float
    situational_awareness: float

class Adrenaline:
    def __init__(self, baseline: float = 1.0):
        self.concentration = baseline
        self.baseline = baseline
        self.half_life_seconds = 120
        self.peak_response = False
        self.peak_timestamp = 0
        
    def metabolize(self, seconds_elapsed: float) -> None:
        decay_factor = 0.5 ** (seconds_elapsed / self.half_life_seconds)
        self.concentration *= decay_factor
        if self.concentration < self.baseline * 1.1:
            self.peak_response = False
            
    def acute_stress_response(self, threat: ThreatType) -> Dict:
        threat_multipliers = {
            ThreatType.AMBUSH: 7.5,
            ThreatType.SNIPER: 6.8,
            ThreatType.IED: 8.2,
            ThreatType.DIRECT_FIRE: 5.9,
            ThreatType.INDIRECT_FIRE: 4.7,
            ThreatType.PURSUIT: 3.9
        }
        
        self.concentration *= threat_multipliers.get(threat, 3.0)
        self.peak_response = True
        self.peak_timestamp = time.time()
        
        metrics = PhysiologicalMetrics(
            heart_rate_bpm=110 + self.concentration * 8,
            respiratory_rate=22 + self.concentration * 2.5,
            pupil_dilation=min(0.95, 0.3 + self.concentration * 0.08),
            tremor_intensity=self.concentration * 0.12,
            auditory_threshold=min(0.85, 0.2 + self.concentration * 0.09),
            visual_field=min(0.75, 0.15 + self.concentration * 0.1),
            reaction_time_ms=max(160, 320 - self.concentration * 18),
            situational_awareness=max(0.25, 0.95 - self.concentration * 0.12)
        )
        
        return {
            "concentration": round(self.concentration, 1),
            "sympathetic_activation": min(1.0, 0.4 + self.concentration * 0.1),
            "pain_threshold": min(0.95, 0.4 + self.concentration * 0.08),
            "auditory_gating": metrics.auditory_threshold > 0.45,
            "peripheral_vision_loss": metrics.visual_field < 0.35,
            "reaction_time_improvement": metrics.reaction_time_ms < 210,
            "metrics": metrics
        }
    
    def performance_modifier(self) -> float:
        if not self.peak_response:
            return 1.0
        duration = time.time() - self.peak_timestamp
        if duration > 180:
            return max(0.4, 1.0 - (duration - 180) * 0.008)
        return 1.0 + self.concentration * 0.08

class Cortisol:
    def __init__(self, baseline: float = 12.0):
        self.concentration = baseline
        self.baseline = baseline
        self.half_life_hours = 1.5
        self.deployment_days = 0
        self.recovery_deficit = 0.0
        self.chronic_adaptation = False
        
    def metabolize(self, hours_elapsed: float) -> None:
        decay = 0.5 ** (hours_elapsed / self.half_life_hours)
        self.concentration *= decay
        if self.concentration < self.baseline:
            self.concentration = self.baseline
            
    def stress_accumulation(self, duration_hours: float, mission: MissionType) -> None:
        mission_factors = {
            MissionType.RECON: 1.15,
            MissionType.DIRECT_ACTION: 1.65,
            MissionType.AMBUSH: 1.9,
            MissionType.WITHDRAWAL: 1.55,
            MissionType.HOLDING: 1.35
        }
        
        factor = mission_factors.get(mission, 1.2)
        self.concentration += duration_hours * factor * 1.8
        self.deployment_days += duration_hours / 24
        
        if self.deployment_days > 7:
            self.baseline *= 1.15
            self.chronic_adaptation = True
            
    def cognitive_assessment(self) -> Dict:
        elevation = self.concentration - self.baseline
        metrics = {
            "working_memory": max(0.45, 1.0 - elevation * 0.025),
            "processing_speed": max(0.55, 1.0 - elevation * 0.018),
            "immune_competence": max(0.35, 1.0 - elevation * 0.035),
            "tissue_repair": max(0.25, 1.0 - elevation * 0.04),
            "muscle_recovery_rate": max(0.4, 1.0 - elevation * 0.025)
        }
        
        if self.chronic_adaptation:
            metrics.update({
                "baseline_elevation": self.baseline > 15,
                "irritability_index": min(1.0, 0.3 + elevation * 0.02),
                "sleep_quality": max(0.2, 1.0 - self.recovery_deficit * 0.1),
                "metabolic_cost": self.deployment_days > 21,
                "long_term_risk": self.deployment_days > 45
            })
            
        return metrics
    
    def circadian_modulation(self, hour: int, active_duty: bool) -> None:
        if active_duty:
            self.concentration *= 1.25
            self.recovery_deficit += 0.4
        else:
            if 5 <= hour <= 9:
                self.concentration *= 1.35
            elif 23 <= hour or hour <= 4:
                self.concentration *= 1.15 if self.chronic_adaptation else 0.75

class OperatorPhysiology:
    def __init__(self, identifier: str, element: str):
        self.identifier = identifier
        self.element = element
        self.adrenaline = Adrenaline()
        self.cortisol = Cortisol()
        self.posture = AlertLevel.STANDARD
        self.current_mission: Optional[MissionType] = None
        self.state = SoldierStatus.NORMAL
        self.event_log: List[Dict] = []
        self.threat_encounters: List[ThreatType] = []
        self.communication_channels = []
        self.element_casualties = 0
        self.ammunition_expended = 0
        
    def operational_briefing(self, mission: MissionType, duration: float) -> Dict:
        self.current_mission = mission
        self.posture = AlertLevel.HEIGHTENED
        self.adrenaline.concentration *= 1.4
        self.cortisol.concentration *= 1.15
        
        return {
            "operator": self.identifier,
            "element": self.element,
            "mission_type": mission.value,
            "projected_duration": duration,
            "adrenaline_baseline": round(self.adrenaline.concentration, 1),
            "cortisol_baseline": round(self.cortisol.concentration, 1),
            "readiness_state": self.posture.value
        }
    
    def threat_engagement(self, threat: ThreatType, severity: float) -> Dict:
        self.posture = AlertLevel.COMBAT
        self.threat_encounters.append(threat)
        self.ammunition_expended += random.randint(45, 450)
        
        response = self.adrenaline.acute_stress_response(threat)
        
        self.cortisol.stress_accumulation(0.5, self.current_mission or MissionType.DIRECT_ACTION)
        
        if threat == ThreatType.AMBUSH:
            self.state = SoldierStatus.PANICKED if random.random() < 0.25 else SoldierStatus.FOCUSED
        elif threat == ThreatType.SNIPER:
            self.state = SoldierStatus.FOCUSED
        elif threat == ThreatType.IED:
            self.state = SoldierStatus.TUNNEL_VISION
            
        engagement_record = {
            "timestamp": time.time(),
            "threat_classification": threat.value,
            "severity_index": severity,
            "adrenaline_response": response["concentration"],
            "cortisol_concentration": round(self.cortisol.concentration, 1),
            "physiological_response": response,
            "operator_state": self.state.value,
            "rounds_expended": self.ammunition_expended,
            "awareness_index": response["metrics"].situational_awareness
        }
        
        self.event_log.append(engagement_record)
        return engagement_record
    
    def element_casualty(self, severity: float) -> Dict:
        self.element_casualties += 1
        self.adrenaline.concentration *= 2.3
        self.cortisol.concentration *= 1.7
        
        if self.element_casualties > 2:
            self.state = SoldierStatus.PANICKED
        else:
            self.state = SoldierStatus.FOCUSED
            
        vitals = PhysiologicalMetrics(
            heart_rate_bpm=135 + random.randint(5, 25),
            respiratory_rate=28 + random.randint(3, 12),
            pupil_dilation=0.75,
            tremor_intensity=0.28,
            auditory_threshold=0.65,
            visual_field=0.55,
            reaction_time_ms=175,
            situational_awareness=0.48
        )
        
        return {
            "event": "element_casualty",
            "cumulative_casualties": self.element_casualties,
            "adrenaline_spike": round(self.adrenaline.concentration, 1),
            "cortisol_level": round(self.cortisol.concentration, 1),
            "psychological_state": self.state.value,
            "combat_effectiveness": self.adrenaline.performance_modifier(),
            "physiological_state": vitals,
            "immediate_response": "suppressive_fire" if self.state != SoldierStatus.PANICKED else "cover"
        }
    
    def tactical_retrograde(self, pursued: bool) -> Dict:
        self.posture = AlertLevel.CRITICAL
        self.current_mission = MissionType.WITHDRAWAL
        
        if pursued:
            self.adrenaline.concentration *= 1.9
            self.cortisol.concentration *= 1.25
            
        effectiveness = self.adrenaline.performance_modifier()
        
        assessment = {
            "maneuver": "tactical_retrograde",
            "pursuit_ongoing": pursued,
            "adrenaline_state": round(self.adrenaline.concentration, 1),
            "cortisol_state": round(self.cortisol.concentration, 1),
            "movement_efficiency": 1.0 + self.adrenaline.concentration * 0.12,
            "accuracy_degradation": self.adrenaline.concentration * 0.08 if pursued else 0.03,
            "cover_utilization": self.cortisol.concentration > 18,
            "communication_discipline": self.cortisol.concentration < 22,
            "effectiveness_coefficient": effectiveness
        }
        
        self.event_log.append(assessment)
        return assessment
    
    def extraction_debrief(self, recovery_period: float) -> Dict:
        self.posture = AlertLevel.STANDARD
        self.current_mission = None
        
        self.adrenaline.metabolize(recovery_period * 3600)
        self.cortisol.metabolize(recovery_period)
        
        cognitive_state = self.cortisol.cognitive_assessment()
        
        if self.cortisol.chronic_adaptation:
            report = {
                "operator": self.identifier,
                "deployment_duration_days": round(self.cortisol.deployment_days, 1),
                "threat_encounters": len(self.threat_encounters),
                "element_losses": self.element_casualties,
                "chronic_stress_indicators": True,
                "cognitive_decline": round(cognitive_state["working_memory"], 2),
                "immune_status": round(cognitive_state["immune_competence"], 2),
                "rotation_required": self.cortisol.deployment_days > 40,
                "psychological_evaluation_recommended": self.cortisol.deployment_days > 55
            }
        else:
            report = {
                "operator": self.identifier,
                "mission_completion": True,
                "final_adrenaline": round(self.adrenaline.concentration, 1),
                "final_cortisol": round(self.cortisol.concentration, 1),
                "recovery_allocated": recovery_period,
                "operational_readiness": self.cortisol.concentration < 14
            }
            
        return report
    
    def unit_cohesion_analysis(self, team_roster: List[str]) -> Dict:
        mean_cortisol = self.cortisol.concentration
        cohesion_index = 1.0 - (mean_cortisol - self.cortisol.baseline) * 0.018
        
        comms_effectiveness = "reduced" if cohesion_index < 0.72 else "nominal"
        if self.cortisol.chronic_adaptation:
            comms_effectiveness = "degraded"
            
        return {
            "unit_composition": team_roster,
            "mean_cortisol": round(mean_cortisol, 1),
            "cohesion_index": max(0.35, round(cohesion_index, 2)),
            "communication_efficacy": comms_effectiveness,
            "blue_on_blue_risk": "elevated" if mean_cortisol > 28 else "baseline",
            "mutual_support_index": max(0.45, 1.0 - (self.cortisol.deployment_days * 0.008))
        }

class BattalionTaskForce:
    def __init__(self, task_force_designation: str):
        self.task_force_designation = task_force_designation
        self.personnel: Dict[str, OperatorPhysiology] = {}
        self.current_operational_tempo = AlertLevel.STANDARD
        self.area_classification = "contested"
        self.cumulative_deployment_days = 0
        
    def attach_operator(self, identifier: str, element: str) -> None:
        self.personnel[identifier] = OperatorPhysiology(identifier, element)
        
    def element_contact(self, grid_reference: str, threat_intensity: float) -> Dict:
        self.current_operational_tempo = AlertLevel.COMBAT
        
        element_responses = {}
        for identifier, operator in self.personnel.items():
            response = operator.threat_engagement(ThreatType.AMBUSH, threat_intensity)
            element_responses[identifier] = {
                "state": response["operator_state"],
                "adrenaline": response["adrenaline_response"],
                "awareness": response["awareness_index"]
            }
            
        unit_status = self.assess_unit_readiness()
        
        return {
            "contact_location": grid_reference,
            "threat_magnitude": threat_intensity,
            "element_responses": element_responses,
            "unit_cohesion_index": unit_status["cohesion_index"],
            "personnel_casualties": sum(1 for op in self.personnel.values() if op.element_casualties > 0),
            "combat_effective_personnel": unit_status["effective_personnel"]
        }
    
    def assess_unit_readiness(self) -> Dict:
        total_adrenaline = sum(op.adrenaline.concentration for op in self.personnel.values())
        total_cortisol = sum(op.cortisol.concentration for op in self.personnel.values())
        mean_adrenaline = total_adrenaline / len(self.personnel) if self.personnel else 0
        mean_cortisol = total_cortisol / len(self.personnel) if self.personnel else 0
        
        effective_personnel = 0
        for op in self.personnel.values():
            if op.state != SoldierStatus.PANICKED and op.adrenaline.performance_modifier() > 0.58:
                effective_personnel += 1
                
        cohesion_index = 1.0 - (mean_cortisol - 10) * 0.018 if mean_cortisol > 10 else 1.0
        
        return {
            "task_force": self.task_force_designation,
            "assigned_personnel": len(self.personnel),
            "mean_adrenaline": round(mean_adrenaline, 1),
            "mean_cortisol": round(mean_cortisol, 1),
            "effective_personnel": effective_personnel,
            "cohesion_index": max(0.25, round(cohesion_index, 2)),
            "operational_tempo": self.current_operational_tempo.value,
            "deployment_duration": round(self.cumulative_deployment_days, 1),
            "relief_priority": "urgent" if mean_cortisol > 24 else "routine"
        }
    
    def night_operations_cycle(self, hour: int) -> None:
        for operator in self.personnel.values():
            watch_duty = random.random() < 0.3
            operator.cortisol.circadian_modulation(hour, watch_duty)
            
    def extended_deployment_simulation(self, days: int) -> List[Dict]:
        daily_assessments = []
        for day in range(days):
            self.cumulative_deployment_days += 1
            
            for hour in range(24):
                if hour % 4 == 0:
                    for operator in self.personnel.values():
                        operator.cortisol.metabolize(4)
                        
                if 6 <= hour <= 19 and random.random() < 0.15:
                    threat = random.choice(list(ThreatType))
                    severity = random.uniform(0.25, 0.95)
                    for operator in self.personnel.values():
                        operator.threat_engagement(threat, severity)
                        
            daily_assessment = self.assess_unit_readiness()
            daily_assessments.append(daily_assessment)
            
        return daily_assessments
    
    def unit_extraction(self, extraction_zone: str) -> Dict:
        recovery_allocation = 72
        final_status = {}
        
        for identifier, operator in self.personnel.items():
            debrief = operator.extraction_debrief(recovery_allocation)
            final_status[identifier] = debrief
            
        unit_assessment = self.assess_unit_readiness()
        
        return {
            "extraction_zone": extraction_zone,
            "personnel_status": final_status,
            "unit_readiness": unit_assessment,
            "command_recommendation": "immediate_relief" if unit_assessment["mean_cortisol"] > 28 else "operational_standby",
            "mission_termination": True
        }

if __name__ == "__main__":
    battletask_force_raider = BattalionTaskForce("TF Raider")
    
    battletask_force_raider.attach_operator("Maverick", "Alpha")
    battletask_force_raider.attach_operator("Ghost", "Alpha")
    battletask_force_raider.attach_operator("Reaper", "Bravo")
    battletask_force_raider.attach_operator("Havoc", "Bravo")
    
    print("=== MISSION BRIEF: OPERATION URBAN RESOLVE ===")
    print(battletask_force_raider.personnel["Maverick"].operational_briefing(MissionType.DIRECT_ACTION, 24))
    
    print("\n=== CONTACT REPORT: ELEMENT AMBUSHED ===")
    contact = battletask_force_raider.element_contact("Sector 7-4", 0.9)
    print(f"Contact Location: {contact['contact_location']}")
    print(f"Combat Effective Personnel: {contact['combat_effective_personnel']}")
    
    print("\n=== CASUALTY REPORT: ELEMENT LOSS ===")
    print(battletask_force_raider.personnel["Ghost"].element_casualty(0.7))
    
    print("\n=== TACTICAL MOVEMENT: RETROGRADE ===")
    print(battletask_force_raider.personnel["Reaper"].tactical_retrograde(True))
    
    print("\n=== 30-DAY DEPLOYMENT ANALYSIS ===")
    deployment = battletask_force_raider.extended_deployment_simulation(30)
    print(f"Final Day Cohesion Index: {deployment[-1]['cohesion_index']}")
    print(f"Final Day Mean Cortisol: {deployment[-1]['mean_cortisol']}")
    
    print("\n=== UNIT READINESS ASSESSMENT ===")
    status = battletask_force_raider.assess_unit_readiness()
    print(f"Effective Personnel: {status['effective_personnel']}/{status['assigned_personnel']}")
    print(f"Relief Priority: {status['relief_priority']}")
    
    print("\n=== COHESION ANALYSIS: ALPHA-BRAVO INTEGRATION ===")
    print(battletask_force_raider.personnel["Maverick"].unit_cohesion_analysis(["Ghost", "Reaper", "Havoc"]))
    
    print("\n=== EXTRACTION & DEBRIEFING SUMMARY ===")
    extraction = battletask_force_raider.unit_extraction("LZ Phoenix")
    print(f"Command Recommendation: {extraction['command_recommendation']}")
    print(f"Total Deployment Days: {extraction['unit_readiness']['deployment_duration']}")
