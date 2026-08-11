from app.services.diagnosis.fault_models import (
    FaultRule,
    SensorRange,
)


FAULT_LIBRARY: list[FaultRule] = [

    # =========================================================
    # 1. BEARING WEAR
    # =========================================================
    FaultRule(
        code="BRG001",
        name="Bearing Wear",
        category="Mechanical",
        severity="Major",

        sensor_ranges={
            "temperature": SensorRange(
                minimum=40.0,
                maximum=70.0,
                weight=1.0,
            ),
            "vibration": SensorRange(
                minimum=1.2,
                maximum=2.8,
                weight=2.0,
            ),
            "current": SensorRange(
                minimum=1.0,
                maximum=2.4,
                weight=0.7,
            ),
            "sound": SensorRange(
                minimum=65.0,
                maximum=90.0,
                weight=1.8,
            ),
        },

        root_cause=(
            "Progressive deterioration of the bearing surface is "
            "creating abnormal vibration and acoustic noise."
        ),

        possible_causes=[
            "Normal bearing fatigue",
            "Insufficient lubrication",
            "Contaminated grease",
            "Incorrect bearing installation",
            "Excessive radial or axial load",
        ],

        recommendation=(
            "Inspect bearing condition, lubrication quality and "
            "bearing housing. Replace the bearing if wear is confirmed."
        ),

        maintenance_priority="High",
        estimated_downtime="2–4 hours",

        spare_parts=[
            "6201 or 6202 bearing",
            "High-temperature bearing grease",
            "Bearing seal",
        ],

        tools=[
            "Bearing puller",
            "Torque wrench",
            "Alignment tool",
            "Infrared thermometer",
        ],

        maintenance_steps=[
            "Stop and isolate the machine.",
            "Inspect bearing housing and mounting.",
            "Check lubrication quantity and contamination.",
            "Remove and inspect the bearing.",
            "Replace the bearing if surface damage is visible.",
            "Verify shaft alignment after installation.",
            "Run a low-speed vibration test.",
        ],

        safety_precautions=[
            "Disconnect electrical power before inspection.",
            "Allow the motor and bearing to cool.",
            "Use gloves while handling hot components.",
        ],

        minimum_confidence=58.0,
    ),

    # =========================================================
    # 2. BEARING SEIZURE
    # =========================================================
    FaultRule(
        code="BRG002",
        name="Bearing Seizure",
        category="Mechanical",
        severity="Emergency",

        sensor_ranges={
            "temperature": SensorRange(
                minimum=75.0,
                maximum=130.0,
                weight=2.0,
            ),
            "vibration": SensorRange(
                minimum=2.0,
                maximum=5.0,
                weight=2.0,
            ),
            "current": SensorRange(
                minimum=1.8,
                maximum=5.0,
                weight=1.4,
            ),
            "sound": SensorRange(
                minimum=75.0,
                maximum=120.0,
                weight=1.8,
            ),
        },

        root_cause=(
            "The bearing is experiencing severe friction or partial "
            "locking, causing extreme heat, vibration and abnormal sound."
        ),

        possible_causes=[
            "Complete lubrication loss",
            "Bearing cage collapse",
            "Severe contamination",
            "Bearing installed with incorrect clearance",
            "Rotor or shaft binding",
        ],

        recommendation=(
            "Shut down the machine immediately. Inspect the bearing, "
            "shaft and housing before attempting a restart."
        ),

        maintenance_priority="Immediate shutdown",
        estimated_downtime="4–8 hours",

        spare_parts=[
            "6201 or 6202 bearing",
            "Bearing grease",
            "Bearing seal",
            "Shaft sleeve if damaged",
        ],

        tools=[
            "Bearing puller",
            "Torque wrench",
            "Dial indicator",
            "Alignment tool",
        ],

        maintenance_steps=[
            "Perform emergency shutdown.",
            "Apply lockout and tagout.",
            "Allow components to cool.",
            "Remove the bearing assembly.",
            "Inspect shaft surface and bearing housing.",
            "Replace damaged bearing and seals.",
            "Lubricate according to manufacturer guidance.",
            "Verify free shaft rotation before restart.",
        ],

        safety_precautions=[
            "Do not touch the bearing immediately after shutdown.",
            "Do not restart before mechanical inspection.",
            "Use lockout and tagout procedures.",
        ],

        minimum_confidence=65.0,
    ),

    # =========================================================
    # 3. LUBRICATION FAILURE
    # =========================================================
    FaultRule(
        code="BRG003",
        name="Bearing Lubrication Failure",
        category="Mechanical",
        severity="Critical",

        sensor_ranges={
            "temperature": SensorRange(
                minimum=55.0,
                maximum=95.0,
                weight=1.8,
            ),
            "vibration": SensorRange(
                minimum=1.0,
                maximum=2.5,
                weight=1.5,
            ),
            "current": SensorRange(
                minimum=1.0,
                maximum=2.8,
                weight=0.8,
            ),
            "sound": SensorRange(
                minimum=68.0,
                maximum=100.0,
                weight=1.8,
            ),
        },

        root_cause=(
            "The bearing is operating with insufficient, degraded or "
            "contaminated lubricant, increasing friction and temperature."
        ),

        possible_causes=[
            "Insufficient grease quantity",
            "Wrong lubricant grade",
            "Contaminated lubricant",
            "Expired or degraded grease",
            "Damaged bearing seal",
        ],

        recommendation=(
            "Stop the machine, inspect lubricant condition and replenish "
            "or replace the lubricant using the correct grade."
        ),

        maintenance_priority="Urgent",
        estimated_downtime="1–3 hours",

        spare_parts=[
            "High-temperature bearing grease",
            "Bearing seal",
            "Replacement bearing if damaged",
        ],

        tools=[
            "Grease gun",
            "Cleaning cloth",
            "Infrared thermometer",
        ],

        maintenance_steps=[
            "Stop and isolate the machine.",
            "Inspect bearing temperature.",
            "Check grease condition and quantity.",
            "Clean contaminated lubricant.",
            "Apply the recommended lubricant.",
            "Inspect bearing seals.",
            "Run the motor at low speed and monitor temperature.",
        ],

        safety_precautions=[
            "Do not overfill the bearing with grease.",
            "Use lubricant recommended for the bearing.",
        ],

        minimum_confidence=57.0,
    ),

    # =========================================================
    # 4. SHAFT MISALIGNMENT
    # =========================================================
    FaultRule(
        code="SFT001",
        name="Shaft Misalignment",
        category="Mechanical",
        severity="Major",

        sensor_ranges={
            "temperature": SensorRange(
                minimum=35.0,
                maximum=70.0,
                weight=0.8,
            ),
            "vibration": SensorRange(
                minimum=1.0,
                maximum=2.7,
                weight=2.0,
            ),
            "current": SensorRange(
                minimum=1.5,
                maximum=3.5,
                weight=1.5,
            ),
            "sound": SensorRange(
                minimum=55.0,
                maximum=85.0,
                weight=1.0,
            ),
        },

        root_cause=(
            "The motor shaft and driven shaft are not correctly aligned, "
            "creating additional vibration and mechanical load."
        ),

        possible_causes=[
            "Incorrect motor installation",
            "Loose base bolts",
            "Coupling displacement",
            "Foundation movement",
            "Bent shaft",
        ],

        recommendation=(
            "Check angular and parallel shaft alignment and correct the "
            "motor or coupling position."
        ),

        maintenance_priority="High",
        estimated_downtime="2–4 hours",

        spare_parts=[
            "Flexible coupling",
            "Coupling insert",
            "Mounting bolts",
        ],

        tools=[
            "Laser alignment tool",
            "Dial indicator",
            "Feeler gauge",
            "Torque wrench",
        ],

        maintenance_steps=[
            "Stop and isolate the machine.",
            "Inspect motor and driven equipment mounting.",
            "Check coupling condition.",
            "Measure angular and parallel alignment.",
            "Correct alignment using suitable shims.",
            "Tighten mounting bolts to specification.",
            "Run and monitor vibration.",
        ],

        safety_precautions=[
            "Do not perform alignment while the machine is energised.",
            "Secure all rotating parts before measurement.",
        ],

        minimum_confidence=57.0,
    ),

    # =========================================================
    # 5. ROTOR IMBALANCE
    # =========================================================
    FaultRule(
        code="ROT001",
        name="Rotor Imbalance",
        category="Mechanical",
        severity="Major",

        sensor_ranges={
            "temperature": SensorRange(
                minimum=30.0,
                maximum=65.0,
                weight=0.6,
            ),
            "vibration": SensorRange(
                minimum=1.3,
                maximum=3.5,
                weight=2.2,
            ),
            "current": SensorRange(
                minimum=0.8,
                maximum=2.5,
                weight=0.7,
            ),
            "sound": SensorRange(
                minimum=50.0,
                maximum=80.0,
                weight=1.0,
            ),
        },

        root_cause=(
            "Uneven mass distribution around the rotating shaft is "
            "producing excessive periodic vibration."
        ),

        possible_causes=[
            "Dust or material buildup",
            "Damaged fan blade",
            "Uneven rotor mass",
            "Loose rotating component",
            "Incorrectly fitted coupling",
        ],

        recommendation=(
            "Inspect the rotor, coupling and fan assembly. Clean material "
            "buildup and perform rotor balancing."
        ),

        maintenance_priority="High",
        estimated_downtime="2–5 hours",

        spare_parts=[
            "Fan blade if damaged",
            "Balancing weights",
            "Coupling insert",
        ],

        tools=[
            "Vibration analyser",
            "Balancing equipment",
            "Torque wrench",
        ],

        maintenance_steps=[
            "Stop and isolate the machine.",
            "Inspect the rotor and cooling fan.",
            "Remove dust or material buildup.",
            "Check for missing or loose components.",
            "Perform static or dynamic balancing.",
            "Verify vibration after correction.",
        ],

        safety_precautions=[
            "Do not operate with a visibly damaged fan or rotor.",
            "Secure balancing weights correctly.",
        ],

        minimum_confidence=56.0,
    ),

    # =========================================================
    # 6. MECHANICAL LOOSENESS
    # =========================================================
    FaultRule(
        code="MEC001",
        name="Mechanical Looseness",
        category="Mechanical",
        severity="Moderate",

        sensor_ranges={
            "temperature": SensorRange(
                minimum=25.0,
                maximum=65.0,
                weight=0.5,
            ),
            "vibration": SensorRange(
                minimum=0.9,
                maximum=2.5,
                weight=1.8,
            ),
            "current": SensorRange(
                minimum=0.7,
                maximum=2.5,
                weight=0.6,
            ),
            "sound": SensorRange(
                minimum=65.0,
                maximum=100.0,
                weight=2.0,
            ),
        },

        root_cause=(
            "Loose mounting bolts, bearing housing or coupling components "
            "are producing vibration and impact noise."
        ),

        possible_causes=[
            "Loose motor foundation bolts",
            "Loose bearing housing",
            "Loose coupling",
            "Cracked mounting base",
            "Improper assembly torque",
        ],

        recommendation=(
            "Inspect and tighten mounting, bearing housing and coupling "
            "fasteners using the specified torque."
        ),

        maintenance_priority="Medium",
        estimated_downtime="1–2 hours",

        spare_parts=[
            "Mounting bolts",
            "Lock washers",
            "Coupling insert",
        ],

        tools=[
            "Torque wrench",
            "Spanner set",
            "Thread-locking compound",
        ],

        maintenance_steps=[
            "Stop the machine.",
            "Inspect base and foundation.",
            "Check mounting bolts.",
            "Inspect bearing housing.",
            "Inspect coupling fasteners.",
            "Tighten components to specified torque.",
            "Run and confirm noise reduction.",
        ],

        safety_precautions=[
            "Do not tighten rotating components while energised.",
            "Replace damaged bolts rather than reusing them.",
        ],

        minimum_confidence=55.0,
    ),

    # =========================================================
    # 7. MOTOR OVERLOAD
    # =========================================================
    FaultRule(
        code="ELE001",
        name="Motor Overload",
        category="Electrical",
        severity="Critical",

        sensor_ranges={
            "temperature": SensorRange(
                minimum=60.0,
                maximum=110.0,
                weight=1.8,
            ),
            "vibration": SensorRange(
                minimum=0.4,
                maximum=2.2,
                weight=0.6,
            ),
            "current": SensorRange(
                minimum=2.2,
                maximum=6.0,
                weight=2.2,
            ),
            "sound": SensorRange(
                minimum=45.0,
                maximum=85.0,
                weight=0.7,
            ),
        },

        root_cause=(
            "The motor is drawing more current than its expected operating "
            "condition, producing excessive heat."
        ),

        possible_causes=[
            "Excessive mechanical load",
            "Jammed driven equipment",
            "Incorrect power supply",
            "Shaft or bearing friction",
            "Motor undersized for the application",
        ],

        recommendation=(
            "Reduce or remove the mechanical load and inspect the motor, "
            "driven equipment and power supply before restarting."
        ),

        maintenance_priority="Urgent",
        estimated_downtime="1–4 hours",

        spare_parts=[
            "Overload relay if defective",
            "Motor cooling fan",
            "Replacement coupling if damaged",
        ],

        tools=[
            "Clamp meter",
            "Multimeter",
            "Insulation resistance tester",
        ],

        maintenance_steps=[
            "Stop the motor.",
            "Measure supply voltage.",
            "Check current without mechanical load.",
            "Inspect driven equipment for jamming.",
            "Check shaft rotation.",
            "Inspect overload protection settings.",
            "Restart under controlled load.",
        ],

        safety_precautions=[
            "Do not bypass overload protection.",
            "Use electrically insulated tools.",
            "Disconnect the supply before mechanical inspection.",
        ],

        minimum_confidence=60.0,
    ),

    # =========================================================
    # 8. COOLING SYSTEM FAILURE
    # =========================================================
    FaultRule(
        code="THM001",
        name="Cooling System Failure",
        category="Thermal",
        severity="Critical",

        sensor_ranges={
            "temperature": SensorRange(
                minimum=70.0,
                maximum=120.0,
                weight=2.4,
            ),
            "vibration": SensorRange(
                minimum=0.1,
                maximum=1.5,
                weight=0.5,
            ),
            "current": SensorRange(
                minimum=0.8,
                maximum=2.5,
                weight=0.7,
            ),
            "sound": SensorRange(
                minimum=30.0,
                maximum=75.0,
                weight=0.5,
            ),
        },

        root_cause=(
            "Heat is not being removed effectively from the motor or "
            "bearing assembly."
        ),

        possible_causes=[
            "Cooling fan failure",
            "Blocked ventilation openings",
            "Dust accumulation",
            "Insufficient airflow",
            "Motor operating in a hot environment",
        ],

        recommendation=(
            "Stop the machine and inspect the cooling fan, ventilation "
            "openings and accumulated dust."
        ),

        maintenance_priority="Urgent",
        estimated_downtime="1–3 hours",

        spare_parts=[
            "Cooling fan",
            "Fan guard",
            "Air filter if installed",
        ],

        tools=[
            "Infrared thermometer",
            "Compressed-air cleaner",
            "Multimeter",
        ],

        maintenance_steps=[
            "Stop and isolate the machine.",
            "Allow the motor to cool.",
            "Inspect cooling fan operation.",
            "Clean ventilation openings and fins.",
            "Check ambient airflow.",
            "Replace the cooling fan if defective.",
            "Monitor temperature after restart.",
        ],

        safety_precautions=[
            "Do not apply compressed air while the motor is running.",
            "Wear eye protection during cleaning.",
        ],

        minimum_confidence=58.0,
    ),

    # =========================================================
    # 9. ROTOR OR SHAFT BINDING
    # =========================================================
    FaultRule(
        code="MEC002",
        name="Rotor or Shaft Binding",
        category="Mechanical",
        severity="Emergency",

        sensor_ranges={
            "temperature": SensorRange(
                minimum=65.0,
                maximum=120.0,
                weight=1.5,
            ),
            "vibration": SensorRange(
                minimum=1.0,
                maximum=4.5,
                weight=1.3,
            ),
            "current": SensorRange(
                minimum=2.8,
                maximum=8.0,
                weight=2.5,
            ),
            "sound": SensorRange(
                minimum=65.0,
                maximum=110.0,
                weight=1.0,
            ),
        },

        root_cause=(
            "The rotating assembly is facing severe mechanical resistance, "
            "causing high current, heat and vibration."
        ),

        possible_causes=[
            "Jammed shaft",
            "Bearing seizure",
            "Rotor rubbing",
            "Misaligned coupling",
            "Foreign object obstruction",
        ],

        recommendation=(
            "Perform immediate shutdown. Inspect whether the shaft rotates "
            "freely and locate the mechanical obstruction."
        ),

        maintenance_priority="Immediate shutdown",
        estimated_downtime="3–8 hours",

        spare_parts=[
            "Bearing",
            "Shaft sleeve",
            "Flexible coupling",
        ],

        tools=[
            "Clamp meter",
            "Bearing puller",
            "Dial indicator",
            "Torque wrench",
        ],

        maintenance_steps=[
            "Perform emergency shutdown.",
            "Disconnect electrical power.",
            "Attempt manual shaft rotation after cooling.",
            "Inspect bearings and coupling.",
            "Check for rotor rubbing or obstruction.",
            "Repair or replace damaged components.",
            "Verify no-load current before returning to service.",
        ],

        safety_precautions=[
            "Do not repeatedly restart a stalled motor.",
            "Do not rotate hot or energised equipment manually.",
        ],

        minimum_confidence=63.0,
    ),

    # =========================================================
    # 10. HEALTHY OPERATING CONDITION
    # =========================================================
    FaultRule(
        code="HLT001",
        name="Healthy Operating Condition",
        category="Normal",
        severity="Healthy",

        sensor_ranges={
            "temperature": SensorRange(
                minimum=20.0,
                maximum=50.0,
                weight=1.0,
            ),
            "vibration": SensorRange(
                minimum=0.0,
                maximum=0.7,
                weight=1.5,
            ),
            "current": SensorRange(
                minimum=0.3,
                maximum=1.7,
                weight=1.0,
            ),
            "sound": SensorRange(
                minimum=20.0,
                maximum=55.0,
                weight=1.0,
            ),
        },

        root_cause=(
            "All monitored sensor readings are within the expected "
            "prototype operating range."
        ),

        possible_causes=[],

        recommendation=(
            "Continue normal operation and routine condition monitoring."
        ),

        maintenance_priority="Routine monitoring",
        estimated_downtime="No downtime required",

        spare_parts=[],

        tools=[
            "Routine inspection checklist",
        ],

        maintenance_steps=[
            "Continue periodic sensor monitoring.",
            "Maintain normal lubrication schedule.",
            "Inspect mounting and wiring periodically.",
        ],

        safety_precautions=[
            "Continue following standard machine safety procedures.",
        ],

        minimum_confidence=65.0,
    ),
]
def get_fault_library() -> list[FaultRule]:
    return FAULT_LIBRARY.copy()


def get_fault_by_code(code: str) -> FaultRule | None:
    normalised_code = code.strip().upper()

    for fault in FAULT_LIBRARY:
        if fault.code.upper() == normalised_code:
            return fault

    return None


def get_faults_by_category(category: str) -> list[FaultRule]:
    normalised_category = category.strip().lower()

    return [
        fault
        for fault in FAULT_LIBRARY
        if fault.category.lower() == normalised_category
    ]