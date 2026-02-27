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
class TacticalVitals:
    heart_rate_bpm: float
    respiratory_rate: float
    pupil_dilation: float
    tremor_intensity: float
    auditory_exclusion: float
    visual_tunnel: float
    reaction_time_ms: float
    situational_awareness: float

class Adrenaline:
    def __init__(self, concentration: float = 1.0):
        self.concentration = concentration
        self.half_life_seconds = 120
        self.surge_active = False
        self.surge_start_time = 0
        
    def metabolize(self, seconds_passed: float) -> None:
        decay_factor = 0.5 ** (seconds_passed / self.half_life_seconds)
        self.concentration *= decay_factor
        if self.concentration < 0.1:
            self.surge_active = False
            
    def trigger_combat_surge(self, threat_level: ThreatType) -> Dict:
        base_multiplier = {
            ThreatType.AMBUSH: 8.0,
            ThreatType.SNIPER: 7.0,
            ThreatType.IED: 9.0,
            ThreatType.DIRECT_FIRE: 6.0,
            ThreatType.INDIRECT_FIRE: 5.0,
            ThreatType.PURSUIT: 4.0
        }
        
        self.concentration *= base_multiplier.get(threat_level, 3.0)
        self.surge_active = True
        self.surge_start_time = time.time()
        
        vitals = TacticalVitals(
            heart_rate_bpm=120 + self.concentration * 10,
            respiratory_rate=25 + self.concentration * 3,
            pupil_dilation=min(1.0, 0.3 + self.concentration * 0.1),
            tremor_intensity=self.concentration * 0.15,
            auditory_exclusion=min(0.9, 0.2 + self.concentration * 0.1),
            visual_tunnel=min(0.8, 0.1 + self.concentration * 0.12),
            reaction_time_ms=max(150, 300 - self.concentration * 20),
            situational_awareness=max(0.2, 1.0 - self.concentration * 0.15)
        )
        
        effects = {
            "strength_boost": 1.0 + self.concentration * 0.2,
            "pain_suppression": min(0.9, 0.3 + self.concentration * 0.1),
            "auditory_exclusion": vitals.auditory_exclusion > 0.5,
            "tunnel_vision": vitals.visual_tunnel > 0.4,
            "reaction_time_advantage": vitals.reaction_time_ms < 200,
            "vitals": vitals,
            "message": f"Combat surge activated: {threat_level.value}"
        }
        
        return effects
    
    def assess_combat_effectiveness(self) -> float:
        if not self.surge_active:
            return 1.0
        time_in_surge = time.time() - self.surge_start_time
        if time_in_surge > 180:
            return max(0.3, 1.0 - (time_in_surge - 180) * 0.01)
        return 1.0 + self.concentration * 0.1

class Cortisol:
    def __init__(self, concentration: float = 10.0):
        self.concentration = concentration
        self.baseline = 10.0
        self.half_life_hours = 1.5
        self.combat_days = 0
        self.sleep_debt = 0.0
        self.chronic_elevation = False
        
    def metabolize(self, hours_passed: float) -> None:
        decay_factor = 0.5 ** (hours_passed / self.half_life_hours)
        self.concentration *= decay_factor
        if self.concentration < self.baseline:
            self.concentration = self.baseline
            
    def combat_stress_accumulation(self, mission_duration_hours: float, mission_type: MissionType) -> None:
        stress_factors = {
            MissionType.RECON: 1.2,
            MissionType.DIRECT_ACTION: 1.8,
            MissionType.AMBUSH: 2.0,
            MissionType.WITHDRAWAL: 1.6,
            MissionType.HOLDING: 1.4
        }
        
        stress_multiplier = stress_factors.get(mission_type, 1.0)
        self.concentration += mission_duration_hours * stress_multiplier * 2
        self.combat_days += mission_duration_hours / 24
        
        if self.combat_days > 7:
            self.baseline *= 1.2
            self.chronic_elevation = True
            
    def assess_operational_effects(self) -> Dict:
        effects = {
            "memory_recall": max(0.4, 1.0 - (self.concentration - self.baseline) * 0.03),
            "decision_speed": max(0.5, 1.0 - (self.concentration - self.baseline) * 0.02),
            "immune_function": max(0.3, 1.0 - (self.concentration - self.baseline) * 0.04),
            "wound_healing": max(0.2, 1.0 - (self.concentration - self.baseline) * 0.05),
            "muscle_recovery": max(0.3, 1.0 - (self.concentration - self.baseline) * 0.03)
        }
        
        if self.chronic_elevation:
            effects.update({
                "hypervigilance": True,
                "irritability": self.concentration > self.baseline * 1.5,
                "sleep_disruption": True,
                "weight_loss": self.combat_days > 14,
                "ptsd_risk": self.combat_days > 30
            })
            
        return effects
    
    def circadian_combat_cycle(self, hour: int, watch_duty: bool) -> None:
        if watch_duty:
            self.concentration *= 1.3
            self.sleep_debt += 0.5
        else:
            if 4 <= hour <= 8:
                self.concentration *= 1.4
            elif 22 <= hour or hour <= 3:
                self.concentration *= 1.2 if self.chronic_elevation else 0.8

class CombatStressResponse:
    def __init__(self, operator_name: str, unit: str):
        self.operator = operator_name
        self.unit = unit
        self.adrenaline = Adrenaline()
        self.cortisol = Cortisol()
        self.alert_level = AlertLevel.STANDARD
        self.current_mission: Optional[MissionType] = None
        self.status = SoldierStatus.NORMAL
        self.mission_log: List[Dict] = []
        self.threat_history: List[ThreatType] = []
        self.team_comms = []
        self.casualties_taken = 0
        self.rounds_fired = 0
        
    def mission_brief(self, mission: MissionType, duration_hours: float) -> Dict:
        self.current_mission = mission
        self.alert_level = AlertLevel.HEIGHTENED
        self.adrenaline.concentration *= 1.5
        self.cortisol.concentration *= 1.2
        
        return {
            "operator": self.operator,
            "unit": self.unit,
            "mission": mission.value,
            "duration": duration_hours,
            "initial_adrenaline": self.adrenaline.concentration,
            "initial_cortisol": self.cortisol.concentration,
            "alert_status": self.alert_level.value,
            "briefing_complete": True
        }
    
    def contact_engaged(self, threat: ThreatType, intensity: float) -> Dict:
        self.alert_level = AlertLevel.CRITICAL
        self.threat_history.append(threat)
        self.rounds_fired += random.randint(30, 300)
        
        surge_effects = self.adrenaline.trigger_combat_surge(threat)
        
        self.cortisol.combat_stress_accumulation(0.5, self.current_mission or MissionType.DIRECT_ACTION)
        
        if threat == ThreatType.AMBUSH:
            self.status = SoldierStatus.PANICKED if random.random() < 0.3 else SoldierStatus.FOCUSED
        elif threat == ThreatType.SNIPER:
            self.status = SoldierStatus.FOCUSED
        elif threat == ThreatType.IED:
            self.status = SoldierStatus.TUNNEL_VISION
            
        contact_report = {
            "timestamp": time.time(),
            "threat": threat.value,
            "intensity": intensity,
            "adrenaline_spike": self.adrenaline.concentration,
            "cortisol_level": self.cortisol.concentration,
            "physiological_state": surge_effects,
            "operator_status": self.status.value,
            "rounds_expended": self.rounds_fired,
            "situational_awareness": surge_effects["vitals"].situational_awareness
        }
        
        self.mission_log.append(contact_report)
        return contact_report
    
    def buddy_wounded(self, severity: float) -> Dict:
        self.casualties_taken += 1
        self.adrenaline.concentration *= 2.5
        self.cortisol.concentration *= 1.8
        
        if self.casualties_taken > 2:
            self.status = SoldierStatus.PANICKED
        else:
            self.status = SoldierStatus.FOCUSED
            
        vitals = TacticalVitals(
            heart_rate_bpm=140 + random.randint(10, 30),
            respiratory_rate=30 + random.randint(5, 15),
            pupil_dilation=0.8,
            tremor_intensity=0.3,
            auditory_exclusion=0.7,
            visual_tunnel=0.6,
            reaction_time_ms=180,
            situational_awareness=0.5
        )
        
        return {
            "event": "buddy_wounded",
            "casualties": self.casualties_taken,
            "adrenaline": self.adrenaline.concentration,
            "cortisol": self.cortisol.concentration,
            "status": self.status.value,
            "combat_effectiveness": self.adrenaline.assess_combat_effectiveness(),
            "vitals": vitals,
            "action": "return_fire" if self.status != SoldierStatus.PANICKED else "freeze"
        }
    
    def tactical_withdrawal(self, pursuit_active: bool) -> Dict:
        self.alert_level = AlertLevel.CRITICAL
        self.current_mission = MissionType.WITHDRAWAL
        
        if pursuit_active:
            self.adrenaline.concentration *= 2.0
            self.cortisol.concentration *= 1.3
            
        effectiveness = self.adrenaline.assess_combat_effectiveness()
        
        withdrawal_assessment = {
            "maneuver": "tactical_withdrawal",
            "pursuit_active": pursuit_active,
            "adrenaline_level": self.adrenaline.concentration,
            "cortisol_level": self.cortisol.concentration,
            "movement_speed": 1.0 + self.adrenaline.concentration * 0.15,
            "accuracy_penalty": self.adrenaline.concentration * 0.1 if pursuit_active else 0,
            "cover_seeking": self.cortisol.concentration > 20,
            "comms_discipline": self.cortisol.concentration < 25,
            "effectiveness": effectiveness
        }
        
        self.mission_log.append(withdrawal_assessment)
        return withdrawal_assessment
    
    def extract_and_recovery(self, recovery_hours: float) -> Dict:
        self.alert_level = AlertLevel.STANDARD
        self.current_mission = None
        
        self.adrenaline.metabolize(recovery_hours * 3600)
        self.cortisol.metabolize(recovery_hours)
        
        cortisol_effects = self.cortisol.assess_operational_effects()
        
        if self.cortisol.chronic_elevation:
            debrief = {
                "operator": self.operator,
                "total_combat_days": self.cortisol.combat_days,
                "contacts": len(self.threat_history),
                "casualties_witnessed": self.casualties_taken,
                "chronic_stress": True,
                "cognitive_decline": cortisol_effects["memory_recall"],
                "immune_status": cortisol_effects["immune_function"],
                "rotation_recommended": self.cortisol.combat_days > 45,
                "ptsd_screening": self.cortisol.combat_days > 60,
                "debrief_complete": True
            }
        else:
            debrief = {
                "operator": self.operator,
                "mission_success": True,
                "final_adrenaline": self.adrenaline.concentration,
                "final_cortisol": self.cortisol.concentration,
                "recovery_needed": recovery_hours,
                "ready_for_next": self.cortisol.concentration < 15
            }
            
        return debrief
    
    def team_cohesion_check(self, team_members: List[str]) -> Dict:
        avg_cortisol = self.cortisol.concentration
        cohesion_factor = 1.0 - (avg_cortisol - self.cortisol.baseline) * 0.02
        
        comms_quality = "degraded" if cohesion_factor < 0.7 else "effective"
        if self.cortisol.chronic_elevation:
            comms_quality = "compromised"
            
        return {
            "team": team_members,
            "avg_cortisol": avg_cortisol,
            "cohesion_factor": max(0.3, cohesion_factor),
            "comms_quality": comms_quality,
            "fratricide_risk": "elevated" if avg_cortisol > 30 else "normal",
            "buddy_trust": max(0.4, 1.0 - (self.cortisol.combat_days * 0.01))
        }

class PlatoonOperations:
    def __init__(self, platoon_id: str):
        self.platoon_id = platoon_id
        self.operators: Dict[str, CombatStressResponse] = {}
        self.current_threat_level = AlertLevel.STANDARD
        self.area_of_operations = "hostile"
        self.mission_days = 0
        
    def add_operator(self, name: str, unit: str) -> None:
        self.operators[name] = CombatStressResponse(name, unit)
        
    def squad_ambushed(self, location: str, intensity: float) -> Dict:
        self.current_threat_level = AlertLevel.CRITICAL
        
        squad_response = {}
        for name, operator in self.operators.items():
            response = operator.contact_engaged(ThreatType.AMBUSH, intensity)
            squad_response[name] = response
            
        team_status = self.assess_platoon_status()
        
        return {
            "location": location,
            "intensity": intensity,
            "squad_responses": squad_response,
            "platoon_cohesion": team_status["cohesion"],
            "casualties": sum(1 for op in self.operators.values() if op.casualties_taken > 0),
            "effective_fighters": team_status["combat_effective"]
        }
    
    def assess_platoon_status(self) -> Dict:
        total_adrenaline = sum(op.adrenaline.concentration for op in self.operators.values())
        total_cortisol = sum(op.cortisol.concentration for op in self.operators.values())
        avg_adrenaline = total_adrenaline / len(self.operators) if self.operators else 0
        avg_cortisol = total_cortisol / len(self.operators) if self.operators else 0
        
        combat_effective = 0
        for op in self.operators.values():
            if op.status != SoldierStatus.PANICKED and op.adrenaline.assess_combat_effectiveness() > 0.6:
                combat_effective += 1
                
        cohesion = 1.0 - (avg_cortisol - 10) * 0.02 if avg_cortisol > 10 else 1.0
        
        return {
            "platoon": self.platoon_id,
            "total_operators": len(self.operators),
            "avg_adrenaline": avg_adrenaline,
            "avg_cortisol": avg_cortisol,
            "combat_effective": combat_effective,
            "cohesion": max(0.2, cohesion),
            "alert_level": self.current_threat_level.value,
            "days_deployed": self.mission_days,
            "rotation_priority": "high" if avg_cortisol > 25 else "normal"
        }
    
    def night_ops_cycle(self, hour: int) -> None:
        for operator in self.operators.values():
            on_watch = random.random() < 0.33
            operator.cortisol.circadian_combat_cycle(hour, on_watch)
            
    def prolonged_combat_simulation(self, days: int) -> List[Dict]:
        daily_reports = []
        for day in range(days):
            self.mission_days += 1
            
            for hour in range(24):
                if hour % 4 == 0:
                    for operator in self.operators.values():
                        operator.cortisol.metabolize(4)
                        
                if 6 <= hour <= 18 and random.random() < 0.2:
                    threat = random.choice(list(ThreatType))
                    intensity = random.uniform(0.3, 1.0)
                    for operator in self.operators.values():
                        operator.contact_engaged(threat, intensity)
                        
            daily_report = self.assess_platoon_status()
            daily_reports.append(daily_report)
            
        return daily_reports
    
    def extract_platoon(self, extraction_point: str) -> Dict:
        total_recovery_hours = 72
        final_status = {}
        
        for name, operator in self.operators.items():
            recovery = operator.extract_and_recovery(total_recovery_hours)
            final_status[name] = recovery
            
        platoon_assessment = self.assess_platoon_status()
        
        return {
            "extraction_point": extraction_point,
            "operators": final_status,
            "platoon_assessment": platoon_assessment,
            "recommendation": "immediate_rotation" if platoon_assessment["avg_cortisol"] > 30 else "standby",
            "operation_complete": True
        }

if __name__ == "__main__":
    task_force_raider = PlatoonOperations("TF Raider")
    
    task_force_raider.add_operator("Maverick", "Alpha")
    task_force_raider.add_operator("Ghost", "Alpha")
    task_force_raider.add_operator("Reaper", "Bravo")
    task_force_raider.add_operator("Havoc", "Bravo")
    
    print("=== OPERATION URBAN RESOLVE ===")
    print(task_force_raider.operators["Maverick"].mission_brief(MissionType.DIRECT_ACTION, 24))
    
    print("\n=== CONTACT AMBUSH ===")
    ambush_response = task_force_raider.squad_ambushed("Sector 7-4", 0.9)
    print(f"Ambushed at {ambush_response['location']}")
    print(f"Combat effective: {ambush_response['effective_fighters']}")
    
    print("\n=== CASUALTY EVENT ===")
    print(task_force_raider.operators["Ghost"].buddy_wounded(0.7))
    
    print("\n=== TACTICAL WITHDRAWAL ===")
    print(task_force_raider.operators["Reaper"].tactical_withdrawal(True))
    
    print("\n=== 30 DAY DEPLOYMENT SIMULATION ===")
    deployment_report = task_force_raider.prolonged_combat_simulation(30)
    print(f"Final day cohesion: {deployment_report[-1]['cohesion']:.2f}")
    print(f"Avg cortisol final day: {deployment_report[-1]['avg_cortisol']:.1f}")
    
    print("\n=== PLATOON STATUS POST-DEPLOYMENT ===")
    status = task_force_raider.assess_platoon_status()
    print(f"Combat effective: {status['combat_effective']}/{status['total_operators']}")
    print(f"Rotation priority: {status['rotation_priority']}")
    
    print("\n=== TEAM COHESION CHECK ===")
    print(task_force_raider.operators["Maverick"].team_cohesion_check(["Ghost", "Reaper", "Havoc"]))
    
    print("\n=== EXTRACTION AND DEBRIEF ===")
    extraction = task_force_raider.extract_platoon("LZ Phoenix")
    print(f"Recommendation: {extraction['recommendation']}")
    print(f"Mission days: {extraction['platoon_assessment']['days_deployed']}")
