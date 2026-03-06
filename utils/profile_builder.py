from models.patient_profile import PatientProfile


def build_profile_context(profile: PatientProfile) -> str:
    """
    Serialise the patient profile into a structured plain-text block
    for injection into LLM system prompts.
    """
    lines = []

    if profile.conditions:
        lines.append(f"MEDICAL CONDITIONS: {', '.join(profile.conditions)}")

    if profile.dialysis_type and profile.dialysis_type != "None":
        lines.append(f"DIALYSIS TYPE: {profile.dialysis_type}")

    if profile.medications:
        lines.append(f"MEDICATIONS: {', '.join(profile.medications)}")

    lab_parts = []
    if profile.egfr is not None:
        lab_parts.append(f"eGFR {profile.egfr} mL/min/1.73m²")
    if profile.serum_potassium is not None:
        lab_parts.append(f"Serum K⁺ {profile.serum_potassium} mmol/L")
    if profile.serum_phosphate is not None:
        lab_parts.append(f"Serum Phosphate {profile.serum_phosphate} mmol/L")
    if profile.hba1c is not None:
        lab_parts.append(f"HbA1c {profile.hba1c}%")
    if profile.ldl_cholesterol is not None:
        lab_parts.append(f"LDL Cholesterol {profile.ldl_cholesterol} mmol/L")
    if lab_parts:
        lines.append(f"RECENT LAB VALUES: {', '.join(lab_parts)}")

    if profile.fluid_restriction_ml:
        lines.append(f"FLUID RESTRICTION: {profile.fluid_restriction_ml} mL/day")

    demo_parts = []
    if profile.age:
        demo_parts.append(f"{profile.age} years old")
    if profile.gender:
        demo_parts.append(profile.gender)
    if profile.ethnicity:
        demo_parts.append(f"{profile.ethnicity} ethnicity")
    if profile.nationality:
        demo_parts.append(f"{profile.nationality} nationality")
    if demo_parts:
        lines.append(f"PATIENT DEMOGRAPHICS: {', '.join(demo_parts)}")

    if profile.dietary_restrictions:
        lines.append(f"DIETARY RESTRICTIONS: {', '.join(profile.dietary_restrictions)}")

    if profile.nutrients_to_restrict:
        lines.append(f"NUTRIENTS TO RESTRICT: {', '.join(profile.nutrients_to_restrict)}")

    if profile.nutrients_to_encourage:
        lines.append(f"NUTRIENTS TO ENCOURAGE: {', '.join(profile.nutrients_to_encourage)}")

    prefs = []
    if profile.vegetarian:
        prefs.append("Vegetarian")
    if profile.vegan:
        prefs.append("Vegan")
    if profile.halal:
        prefs.append("Halal")
    if profile.kosher:
        prefs.append("Kosher")
    if prefs:
        lines.append(f"DIETARY PREFERENCES: {', '.join(prefs)}")

    if profile.dietitian_notes:
        lines.append(f"DIETITIAN NOTES: {profile.dietitian_notes}")

    if profile.educational_materials:
        lines.append(f"EDUCATIONAL MATERIALS: {profile.educational_materials}")

    return "\n".join(lines) if lines else "No profile data available."
