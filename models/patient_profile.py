from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PatientProfile:
    # --- Clinician fields ---
    conditions: List[str] = field(default_factory=list)
    medications: List[str] = field(default_factory=list)
    dialysis_type: str = "None"
    egfr: Optional[float] = None
    serum_potassium: Optional[float] = None
    serum_phosphate: Optional[float] = None
    hba1c: Optional[float] = None
    ldl_cholesterol: Optional[float] = None
    fluid_restriction_ml: Optional[int] = None
    clinician_complete: bool = False

    # --- Dietitian fields ---
    age: Optional[int] = None
    gender: str = ""
    ethnicity: str = ""
    nationality: str = ""
    dietary_restrictions: List[str] = field(default_factory=list)
    nutrients_to_restrict: List[str] = field(default_factory=list)
    nutrients_to_encourage: List[str] = field(default_factory=list)
    vegetarian: bool = False
    vegan: bool = False
    halal: bool = False
    kosher: bool = False
    dietitian_notes: str = ""
    educational_materials: str = ""
    dietitian_complete: bool = False
