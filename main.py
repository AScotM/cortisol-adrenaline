
import argparse
import json
import math
import random
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Optional


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def round_values(value):
    if isinstance(value, float):
        return round(value, 3)
    if isinstance(value, dict):
        return {key: round_values(item) for key, item in value.items()}
    if isinstance(value, list):
        return [round_values(item) for item in value]
    return value


class AlertLevel(str, Enum):
    STANDARD = "standard"
    HEIGHTENED = "heightened"
    CRITICAL = "critical"
    COMBAT = "combat"


class MissionType(str, Enum):
    RECON = "recon"
    DIRECT_ACTION = "direct_action"
    AMBUSH = "ambush"
    WITHDRAWAL = "withdrawal"
    HOLDING = "holding"


class ThreatType(str, Enum):
    AMBUSH = "ambush"
    SNIPER = "sniper"
    IED = "ied"
    DIRECT_FIRE = "direct_fire"
    INDIRECT_FIRE = "indirect_fire"
    PURSUIT = "pursuit"


class SoldierStatus(str, Enum):
    NORMAL = "normal"
    WOUNDED = "wounded"
    EXHAUSTED = "exhausted"
    PANICKED = "panicked"
    FOCUSED = "focused"
    TUNNEL_VISION = "tunnel_vision"


@dataclass
class SimulationClock:
    elapsed_hours: float = 0.0

    @property
    def day(self):
        return int(self.elapsed_hours // 24) + 1

    @property
    def hour(self):
        return int(self.elapsed_hours % 24)

    def advance(self, hours):
        if not math.isfinite(hours) or hours < 0:
            raise ValueError("Time increment must be finite and nonnegative")
        self.elapsed_hours += hours


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
    def __init__(self):
        self.baseline = 1.0
        self.concentration = self.baseline
        self.maximum = 12.0
        self.half_life_seconds = 120.0
        self.last_surge_hour = None

    def metabolize(self, hours):
        seconds = hours * 3600.0
        decay = math.exp(
            -math.log(2.0) * seconds / self.half_life_seconds
        )
        self.concentration = self.baseline + (
            self.concentration - self.baseline
        ) * decay

    def trigger_combat_surge(self, threat, intensity, clock):
        intensity = clamp(intensity, 0.0, 1.0)

        factors = {
            ThreatType.AMBUSH: 7.0,
            ThreatType.SNIPER: 6.0,
            ThreatType.IED: 8.0,
            ThreatType.DIRECT_FIRE: 5.5,
            ThreatType.INDIRECT_FIRE: 4.5,
            ThreatType.PURSUIT: 4.0,
        }

        increase = factors[threat] * intensity

        self.concentration = clamp(
            self.concentration + increase,
            self.baseline,
            self.maximum,
        )

        self.last_surge_hour = clock.elapsed_hours
        return self.concentration

    def assess_effectiveness(self, fatigue, stress):
        arousal = self.concentration - self.baseline
        moderate_benefit = min(arousal, 3.0) * 0.06
        overload = max(0.0, arousal - 4.0) * 0.09

        effectiveness = (
            1.0
            + moderate_benefit
            - overload
            - fatigue * 0.35
            - stress * 0.2
        )

        return clamp(effectiveness, 0.15, 1.2)


class Cortisol:
    def __init__(self):
        self.baseline = 10.0
        self.concentration = self.baseline
        self.maximum = 60.0
        self.half_life_hours = 1.5
        self.combat_hours = 0.0
        self.sleep_debt = 0.0
        self.chronic_elevation = False

    def metabolize(self, hours):
        decay = math.exp(
            -math.log(2.0) * hours / self.half_life_hours
        )

        self.concentration = self.baseline + (
            self.concentration - self.baseline
        ) * decay

    def accumulate(self, hours, mission, intensity):
        factors = {
            MissionType.RECON: 1.2,
            MissionType.DIRECT_ACTION: 1.8,
            MissionType.AMBUSH: 2.0,
            MissionType.WITHDRAWAL: 1.6,
            MissionType.HOLDING: 1.4,
        }

        intensity = clamp(intensity, 0.0, 1.0)
        increase = hours * factors[mission] * intensity * 3.0

        self.concentration = clamp(
            self.concentration + increase,
            self.baseline,
            self.maximum,
        )

        self.combat_hours += hours * intensity
        self.update_chronic_state()

    def update_chronic_state(self):
        self.chronic_elevation = (
            self.combat_hours >= 48.0
            or self.sleep_debt >= 16.0
        )

    def recover_sleep(self, hours):
        self.sleep_debt = clamp(
            self.sleep_debt - hours * 0.75,
            0.0,
            48.0,
        )
        self.update_chronic_state()

    def add_sleep_debt(self, hours):
        self.sleep_debt = clamp(
            self.sleep_debt + hours,
            0.0,
            48.0,
        )
        self.update_chronic_state()

    def stress_index(self):
        hormonal = (
            self.concentration - self.baseline
        ) / (self.maximum - self.baseline)

        sleep_component = self.sleep_debt / 48.0

        return clamp(
            hormonal * 0.7 + sleep_component * 0.3,
            0.0,
            1.0,
        )

    def assess_operational_effects(self):
        stress = self.stress_index()

        return {
            "memory_score": clamp(1.0 - stress * 0.45, 0.3, 1.0),
            "decision_score": clamp(1.0 - stress * 0.4, 0.3, 1.0),
            "recovery_score": clamp(1.0 - stress * 0.5, 0.2, 1.0),
            "stress_index": stress,
            "sleep_debt_hours": self.sleep_debt,
            "chronic_elevation": self.chronic_elevation,
        }


class CombatStressResponse:
    def __init__(self, operator_name, unit, clock, rng):
        self.operator = operator_name
        self.unit = unit
        self.clock = clock
        self.rng = rng

        self.adrenaline = Adrenaline()
        self.cortisol = Cortisol()

        self.alert_level = AlertLevel.STANDARD
        self.current_mission = None
        self.status = SoldierStatus.NORMAL

        self.fatigue = 0.0
        self.injury_severity = 0.0
        self.casualties_witnessed = 0
        self.threat_history = []
        self.mission_log = []

    def record_event(self, event, details):
        entry = {
            "time_hours": self.clock.elapsed_hours,
            "day": self.clock.day,
            "operator": self.operator,
            "event": event,
            "details": details,
        }

        self.mission_log.append(entry)
        return entry

    def mission_brief(self, mission, duration_hours):
        self.current_mission = mission
        self.alert_level = AlertLevel.HEIGHTENED

        self.adrenaline.concentration = clamp(
            self.adrenaline.concentration + 0.5,
            1.0,
            self.adrenaline.maximum,
        )

        return self.record_event(
            "mission_brief",
            {
                "mission": mission.value,
                "duration_hours": duration_hours,
            },
        )

    def calculate_vitals(self):
        arousal = self.adrenaline.concentration - 1.0
        stress = self.cortisol.stress_index()

        return TacticalVitals(
            heart_rate_bpm=clamp(
                70 + arousal * 9 + stress * 25,
                55,
                190,
            ),
            respiratory_rate=clamp(
                14 + arousal * 1.8 + stress * 6,
                10,
                40,
            ),
            pupil_dilation=clamp(
                0.25 + arousal * 0.055,
                0.0,
                1.0,
            ),
            tremor_intensity=clamp(
                arousal * 0.075 + stress * 0.2,
                0.0,
                1.0,
            ),
            auditory_exclusion=clamp(
                arousal * 0.065,
                0.0,
                1.0,
            ),
            visual_tunnel=clamp(
                arousal * 0.07 + stress * 0.15,
                0.0,
                1.0,
            ),
            reaction_time_ms=clamp(
                290 - min(arousal, 3) * 22
                + max(0, arousal - 4) * 18
                + self.fatigue * 110,
                150,
                650,
            ),
            situational_awareness=clamp(
                1.0
                - max(0, arousal - 3) * 0.065
                - stress * 0.25
                - self.fatigue * 0.2,
                0.1,
                1.0,
            ),
        )

    def assess_effectiveness(self):
        value = self.adrenaline.assess_effectiveness(
            self.fatigue,
            self.cortisol.stress_index(),
        )

        value *= 1.0 - self.injury_severity * 0.65
        return clamp(value, 0.0, 1.2)

    def update_status(self):
        stress = self.cortisol.stress_index()
        arousal = self.adrenaline.concentration

        if self.injury_severity >= 0.65:
            self.status = SoldierStatus.WOUNDED
        elif self.fatigue >= 0.85:
            self.status = SoldierStatus.EXHAUSTED
        elif stress >= 0.85 and arousal >= 8:
            self.status = SoldierStatus.PANICKED
        elif arousal >= 9:
            self.status = SoldierStatus.TUNNEL_VISION
        elif arousal >= 3:
            self.status = SoldierStatus.FOCUSED
        else:
            self.status = SoldierStatus.NORMAL

    def contact_engaged(self, threat, intensity):
        intensity = clamp(intensity, 0.0, 1.0)

        self.alert_level = AlertLevel.COMBAT
        self.threat_history.append(threat)

        self.adrenaline.trigger_combat_surge(
            threat,
            intensity,
            self.clock,
        )

        mission = self.current_mission or MissionType.DIRECT_ACTION

        self.cortisol.accumulate(
            0.25,
            mission,
            intensity,
        )

        self.fatigue = clamp(
            self.fatigue + intensity * 0.035,
            0.0,
            1.0,
        )

        self.update_status()

        return self.record_event(
            "contact",
            {
                "threat": threat.value,
                "intensity": intensity,
                "adrenaline": self.adrenaline.concentration,
                "cortisol": self.cortisol.concentration,
                "status": self.status.value,
                "vitals": asdict(self.calculate_vitals()),
                "effectiveness": self.assess_effectiveness(),
            },
        )

    def buddy_wounded(self, severity):
        severity = clamp(severity, 0.0, 1.0)
        self.casualties_witnessed += 1

        self.adrenaline.concentration = clamp(
            self.adrenaline.concentration + severity * 5,
            1.0,
            self.adrenaline.maximum,
        )

        self.cortisol.concentration = clamp(
            self.cortisol.concentration + severity * 12,
            self.cortisol.baseline,
            self.cortisol.maximum,
        )

        self.update_status()

        return self.record_event(
            "buddy_wounded",
            {
                "severity": severity,
                "casualties_witnessed": self.casualties_witnessed,
                "status": self.status.value,
            },
        )

    def tactical_withdrawal(self, pursuit_active):
        self.current_mission = MissionType.WITHDRAWAL
        self.alert_level = AlertLevel.CRITICAL

        if pursuit_active:
            self.adrenaline.trigger_combat_surge(
                ThreatType.PURSUIT,
                0.8,
                self.clock,
            )

        self.update_status()

        return self.record_event(
            "withdrawal",
            {
                "pursuit_active": pursuit_active,
                "effectiveness": self.assess_effectiveness(),
                "status": self.status.value,
            },
        )

    def advance_time(self, hours, on_watch=False):
        self.adrenaline.metabolize(hours)
        self.cortisol.metabolize(hours)

        if on_watch:
            self.cortisol.add_sleep_debt(hours * 0.2)
            self.fatigue = clamp(
                self.fatigue + hours * 0.012,
                0.0,
                1.0,
            )
        else:
            self.cortisol.recover_sleep(hours * 0.15)
            self.fatigue = clamp(
                self.fatigue - hours * 0.008,
                0.0,
                1.0,
            )

        self.update_status()

    def extract_and_recovery(self, recovery_hours):
        self.current_mission = None
        self.alert_level = AlertLevel.STANDARD

        self.adrenaline.metabolize(recovery_hours)
        self.cortisol.metabolize(recovery_hours)
        self.cortisol.recover_sleep(recovery_hours * 0.3)

        self.fatigue = clamp(
            self.fatigue - recovery_hours * 0.012,
            0.0,
            1.0,
        )

        self.update_status()

        return self.record_event(
            "recovery",
            {
                "recovery_hours": recovery_hours,
                "adrenaline": self.adrenaline.concentration,
                "cortisol": self.cortisol.concentration,
                "fatigue": self.fatigue,
                "status": self.status.value,
            },
        )

    def snapshot(self):
        return {
            "operator": self.operator,
            "unit": self.unit,
            "status": self.status.value,
            "adrenaline": self.adrenaline.concentration,
            "cortisol": self.cortisol.concentration,
            "fatigue": self.fatigue,
            "sleep_debt": self.cortisol.sleep_debt,
            "injury_severity": self.injury_severity,
            "effectiveness": self.assess_effectiveness(),
            "contacts": len(self.threat_history),
            "casualties_witnessed": self.casualties_witnessed,
        }


class PlatoonOperations:
    def __init__(self, platoon_id, seed=42):
        self.platoon_id = platoon_id
        self.seed = seed
        self.rng = random.Random(seed)
        self.clock = SimulationClock()
        self.operators = {}
        self.current_threat_level = AlertLevel.STANDARD
        self.mission_days = 0
        self.daily_reports = []

    def add_operator(self, name, unit):
        if name in self.operators:
            raise ValueError(f"Operator already exists: {name}")

        self.operators[name] = CombatStressResponse(
            name,
            unit,
            self.clock,
            self.rng,
        )

    def squad_ambushed(self, location, intensity):
        self.current_threat_level = AlertLevel.COMBAT

        responses = {}

        for name, operator in self.operators.items():
            responses[name] = operator.contact_engaged(
                ThreatType.AMBUSH,
                intensity,
            )

        return {
            "location": location,
            "intensity": intensity,
            "responses": responses,
            "platoon": self.assess_platoon_status(),
        }

    def assess_platoon_status(self):
        operators = list(self.operators.values())
        count = len(operators)

        if count == 0:
            return {
                "platoon": self.platoon_id,
                "total_operators": 0,
                "combat_effective": 0,
                "cohesion": 0.0,
            }

        average_adrenaline = sum(
            op.adrenaline.concentration for op in operators
        ) / count

        average_cortisol = sum(
            op.cortisol.concentration for op in operators
        ) / count

        average_fatigue = sum(
            op.fatigue for op in operators
        ) / count

        average_stress = sum(
            op.cortisol.stress_index() for op in operators
        ) / count

        effective = sum(
            op.assess_effectiveness() >= 0.6
            and op.status not in (
                SoldierStatus.PANICKED,
                SoldierStatus.WOUNDED,
                SoldierStatus.EXHAUSTED,
            )
            for op in operators
        )

        cohesion = clamp(
            1.0 - average_stress * 0.5 - average_fatigue * 0.3,
            0.1,
            1.0,
        )

        return {
            "platoon": self.platoon_id,
            "day": self.clock.day,
            "elapsed_hours": self.clock.elapsed_hours,
            "total_operators": count,
            "avg_adrenaline": average_adrenaline,
            "avg_cortisol": average_cortisol,
            "avg_fatigue": average_fatigue,
            "avg_stress": average_stress,
            "combat_effective": effective,
            "cohesion": cohesion,
            "rotation_priority": (
                "high"
                if average_stress > 0.65 or average_fatigue > 0.75
                else "normal"
            ),
        }

    def advance_time(self, hours):
        for operator in self.operators.values():
            on_watch = self.rng.random() < 0.33
            operator.advance_time(hours, on_watch)

        self.clock.advance(hours)

    def prolonged_combat_simulation(self, days):
        if days < 0:
            raise ValueError("Deployment days cannot be negative")

        threats = list(ThreatType)

        for _ in range(days):
            for _ in range(24):
                hour = self.clock.hour

                if 6 <= hour <= 18 and self.rng.random() < 0.2:
                    threat = self.rng.choice(threats)
                    intensity = self.rng.uniform(0.3, 1.0)

                    for operator in self.operators.values():
                        operator.contact_engaged(threat, intensity)

                self.advance_time(1.0)

            self.mission_days += 1

            report = self.assess_platoon_status()
            report["deployment_day"] = self.mission_days
            self.daily_reports.append(report)

        return self.daily_reports

    def extract_platoon(self, extraction_point, recovery_hours=72):
        for operator in self.operators.values():
            operator.extract_and_recovery(recovery_hours)

        self.clock.advance(recovery_hours)
        self.current_threat_level = AlertLevel.STANDARD

        return {
            "extraction_point": extraction_point,
            "recovery_hours": recovery_hours,
            "platoon": self.assess_platoon_status(),
            "operators": {
                name: op.snapshot()
                for name, op in self.operators.items()
            },
        }

    def export(self):
        return {
            "simulation": {
                "name": self.platoon_id,
                "seed": self.seed,
                "deployment_days": self.mission_days,
                "elapsed_hours": self.clock.elapsed_hours,
            },
            "daily_reports": self.daily_reports,
            "final_status": self.assess_platoon_status(),
            "operators": {
                name: {
                    "snapshot": op.snapshot(),
                    "events": op.mission_log,
                }
                for name, op in self.operators.items()
            },
        }


def build_simulation(seed):
    platoon = PlatoonOperations("TF Raider", seed)

    platoon.add_operator("Maverick", "Alpha")
    platoon.add_operator("Ghost", "Alpha")
    platoon.add_operator("Reaper", "Bravo")
    platoon.add_operator("Havoc", "Bravo")

    for operator in platoon.operators.values():
        operator.mission_brief(MissionType.DIRECT_ACTION, 24)

    return platoon


def print_report(platoon, extraction):
    print("=== CORTISOL-ADRENALINE SIMULATION ===")
    print(f"Platoon: {platoon.platoon_id}")
    print(f"Seed: {platoon.seed}")
    print(f"Deployment: {platoon.mission_days} days")
    print()

    print("=== DAILY DEPLOYMENT SUMMARY ===")
    print(
        f"{'Day':>4} {'Cortisol':>10} "
        f"{'Adrenaline':>12} {'Fatigue':>9} "
        f"{'Cohesion':>10} {'Effective':>10}"
    )

    for report in platoon.daily_reports:
        print(
            f"{report['deployment_day']:>4} "
            f"{report['avg_cortisol']:>10.2f} "
            f"{report['avg_adrenaline']:>12.2f} "
            f"{report['avg_fatigue']:>9.2f} "
            f"{report['cohesion']:>10.2f} "
            f"{report['combat_effective']:>10}"
        )

    print()
    print("=== POST-RECOVERY STATUS ===")

    for name, status in extraction["operators"].items():
        print(
            f"{name:<10} "
            f"Status={status['status']:<14} "
            f"Cortisol={status['cortisol']:.2f} "
            f"Fatigue={status['fatigue']:.2f} "
            f"Effectiveness={status['effectiveness']:.2f}"
        )

    print()
    print("=== FINAL ASSESSMENT ===")
    final = extraction["platoon"]

    print(f"Average cortisol: {final['avg_cortisol']:.2f}")
    print(f"Average adrenaline: {final['avg_adrenaline']:.2f}")
    print(f"Team cohesion: {final['cohesion']:.2f}")
    print(f"Rotation priority: {final['rotation_priority']}")


def main():
    parser = argparse.ArgumentParser(
        description="Deterministic fictional combat stress simulation"
    )

    parser.add_argument(
        "--days",
        type=int,
        default=30,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )

    parser.add_argument(
        "--json",
        dest="json_path",
        default=None,
    )

    args = parser.parse_args()

    if args.days < 0:
        parser.error("--days must be nonnegative")

    platoon = build_simulation(args.seed)

    platoon.squad_ambushed("Sector 7-4", 0.9)
    platoon.operators["Ghost"].buddy_wounded(0.7)
    platoon.operators["Reaper"].tactical_withdrawal(True)

    platoon.prolonged_combat_simulation(args.days)

    extraction = platoon.extract_platoon(
        "LZ Phoenix",
        recovery_hours=72,
    )

    print_report(platoon, extraction)

    if args.json_path:
        with open(args.json_path, "w", encoding="utf-8") as file:
            json.dump(
                round_values(platoon.export()),
                file,
                indent=2,
            )

        print()
        print(f"JSON report written to: {args.json_path}")


if __name__ == "__main__":
    main()
