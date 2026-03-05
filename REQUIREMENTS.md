# Food_ID_Bot — Requirements & Design Specification

## 1. Product Overview

**Food_ID_Bot** is a patient-facing mobile-friendly web application that helps patients with chronic conditions (renal, cardiovascular, or diabetic) evaluate whether a specific food is safe to eat, given their individual medical and dietary profile.

The core problem: Patients often receive generic dietary guidelines from dietitians (e.g., "limit potassium", "avoid high-sodium foods") but struggle to apply these to real meals — especially culturally familiar foods or restaurant dishes. This app bridges that gap by combining multimodal AI with a personalised patient profile to deliver actionable, localised, context-aware food safety assessments.

---

## 2. Target Users

| Role | Responsibilities in App |
|---|---|
| **Clinician** | Sets up the patient's medical diagnoses and clinical flags |
| **Dietitian** | Provides demographic context and detailed nutritional restrictions |
| **Patient** | Submits food images/text, reviews AI output, confirms food identification |

---

## 3. Supported Conditions

### 3.1 Renal Conditions
- Chronic Kidney Disease (CKD) Stages 1–5
- End-Stage Renal Disease (ESRD) / Dialysis (Haemodialysis or Peritoneal Dialysis)
- Nephrotic Syndrome
- Renal Transplant (post-operative dietary restrictions)

### 3.2 Cardiovascular Conditions
- Hypertension
- Heart Failure (fluid and sodium restriction)
- Hyperlipidaemia / Dyslipidaemia
- Post-Myocardial Infarction dietary guidance
- Atrial Fibrillation (warfarin / Vitamin K considerations)

### 3.3 Diabetic Conditions
- Type 1 Diabetes Mellitus
- Type 2 Diabetes Mellitus
- Gestational Diabetes
- Pre-Diabetes / Insulin Resistance

### 3.4 Combined Conditions (common comorbidities)
- CKD + Diabetes (Diabetic Nephropathy) — most restrictive overlap
- CKD + Heart Failure — potassium, phosphate, fluid, and sodium all restricted
- Diabetes + Cardiovascular Disease

---

## 4. Clinical Guidelines & Nutritional Restriction Frameworks

All flagging logic should be grounded in the following evidence-based guidelines:

### 4.1 Renal Diet (CKD / Dialysis)
- **Potassium**: Limit <2,000–2,500 mg/day (CKD 3–5); Dialysis patients may require <2,000 mg/day
  - High-risk foods: bananas, oranges, potatoes, tomatoes, legumes, nuts, chocolate, salt substitutes
  - Leaching techniques (boiling and discarding water) can reduce potassium in vegetables
- **Phosphate**: Limit <800–1,000 mg/day; avoid inorganic phosphate additives (cola, processed meats)
  - High-risk foods: dairy, nuts, seeds, wholegrains, processed/packaged foods with phosphate additives (E-numbers: E338–E452)
- **Sodium**: <2,000 mg/day
- **Protein**: Variable — restricted in CKD (0.6–0.8 g/kg/day pre-dialysis); increased in dialysis (~1.2 g/kg/day)
- **Fluid restriction**: Relevant for dialysis and heart failure patients
- **Reference**: KDOQI Clinical Practice Guidelines for Nutrition in CKD (2020 Update); Kidney Health Australia dietary guidelines

### 4.2 Cardiovascular Diet
- **Sodium**: <2,300 mg/day (AHA); <1,500 mg/day for hypertension/heart failure
- **Saturated fat**: <7% of total calories; avoid trans fats
- **Cholesterol**: <200 mg/day for high-risk patients
- **Potassium**: Adequate intake (3,500–4,700 mg/day) for hypertension *unless* CKD present
- **Vitamin K / Warfarin interactions**: Flag high-Vitamin-K foods (leafy greens, broccoli) for anticoagulated patients
- **Reference**: AHA/ACC 2019 Cardiovascular Risk Reduction Dietary Guidelines; DASH Diet framework

### 4.3 Diabetic Diet
- **Glycaemic Index (GI) / Glycaemic Load (GL)**: Prefer low-GI foods; flag high-GI foods
- **Carbohydrate**: ~45–60% of total calories; consistent distribution across meals
- **Refined sugars**: Minimise; flag added sugars, sweetened beverages
- **Fibre**: Target >25–30 g/day (slows glucose absorption)
- **Saturated fat**: Limit (increases insulin resistance)
- **Reference**: ADA Standards of Medical Care in Diabetes (2024); Diabetes UK dietary guidelines

### 4.4 Conflict Resolution (Comorbidities)
When conditions conflict (e.g., potassium is *good* for hypertension but *dangerous* in CKD), the more restrictive clinical constraint always takes precedence. The app must surface these conflicts transparently.

---

## 5. Patient Profile Schema

### 5.1 Clinician-Entered Fields
```
- patient_id (system-generated, anonymised)
- conditions: List[Condition]  # from supported conditions list
- medications: List[str]       # especially warfarin, ACE inhibitors, diuretics
- lab_values (optional):
    - eGFR (mL/min/1.73m²)
    - serum_potassium (mmol/L)
    - serum_phosphate (mmol/L)
    - HbA1c (%)
    - LDL cholesterol (mmol/L)
- dialysis_type: None | Haemodialysis | Peritoneal Dialysis
- fluid_restriction_ml_per_day: int | None
```

### 5.2 Dietitian-Entered Fields
```
- demographics:
    - age: int
    - gender: str
    - ethnicity: str
    - nationality: str           # drives localised food context
    - primary_language: str      # for future localisation
- dietary_restrictions: List[str]  # free text + structured flags
- priority_nutrients_to_restrict: List[Nutrient]
- priority_nutrients_to_encourage: List[Nutrient]
- dietary_preferences:
    - vegetarian: bool
    - vegan: bool
    - halal: bool
    - kosher: bool
    - other: str
- dietitian_notes: str           # free-text clinical notes
- educational_materials: str     # optional: paste or upload dietitian's notes
```

---

## 6. Application Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1 — Clinician Setup (one-time per patient)                 │
│  Input: Diagnoses, medications, key lab values                   │
│  Output: Stored patient medical profile                          │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│  STEP 2 — Dietitian Setup (one-time per patient, updatable)      │
│  Input: Demographics, nutritional restrictions, notes            │
│  Output: Enriched patient profile with dietary context           │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│  STEP 3 — Patient Food Submission (repeated use)                 │
│  Input: Photo of food + optional free-text description           │
│  Processing: Multimodal LLM analyses image in context of profile │
│  Output A: Top 3 probable food identifications (with confidence) │
└─────────────────────────────┬───────────────────────────────────┘
                              │ Patient confirms correct food
┌─────────────────────────────▼───────────────────────────────────┐
│  STEP 4 — Dietary Safety Assessment                              │
│  Processing: LLM evaluates typical ingredients of confirmed food │
│  considering patient profile, nationality/cultural context        │
│  Output B: Structured safety report (see Section 8)              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Recommended Tech Stack

### 7.1 Frontend
| Component | Recommendation | Rationale |
|---|---|---|
| Web Framework | **Streamlit** | Rapid prototyping, mobile-responsive via `st.set_page_config(layout="wide")`, Python-native |
| Image Upload | `st.camera_input()` + `st.file_uploader()` | Camera capture on mobile; file upload fallback |
| Mobile UX | Streamlit Cloud deployment + PWA considerations | Accessible via mobile browser without app install |

### 7.2 AI / LLM
| Component | Recommendation | Rationale |
|---|---|---|
| Vision + Reasoning | **Claude claude-sonnet-4-6** (Anthropic) | Best-in-class multimodal performance; strong reasoning for clinical nuance; supports image + text in single call |
| Fallback / Cost Optimisation | Claude Haiku for low-stakes queries | Faster, cheaper for simple follow-ups |
| Prompt Engineering | Structured system prompt with patient profile injection | Ensures consistent, profile-aware responses |

**Why Claude over GPT-4V or Gemini?**
- Superior instruction-following for structured clinical output formats
- Better nuance with culturally-specific food contexts
- Anthropic's Constitutional AI reduces risk of medically unsafe hallucinations
- Competitive multimodal vision performance

### 7.3 Backend / Data
| Component | Recommendation | Rationale |
|---|---|---|
| Session State | Streamlit `st.session_state` (MVP) | Sufficient for prototype; no database needed initially |
| Patient Profile Storage | JSON files (MVP) → SQLite or PostgreSQL (production) | Start simple, migrate when needed |
| API Layer | Direct Anthropic SDK calls (MVP) → FastAPI wrapper (production) | Clean separation of concerns at scale |

### 7.4 Infrastructure
| Component | Recommendation |
|---|---|
| Deployment (MVP) | Streamlit Community Cloud (free tier) |
| Deployment (Production) | AWS/GCP + Docker container |
| Secrets Management | `st.secrets` (MVP) → AWS Secrets Manager (production) |

---

## 8. LLM Prompt Architecture

### 8.1 System Prompt (injected per session)
The system prompt should include:
1. Role definition: Clinical dietary assistant
2. Patient profile: All clinician + dietitian fields serialised
3. Behavioural guardrails: "Do not provide medical advice. Flag concerns for clinician review. When uncertain, err on the side of caution."
4. Output format instructions: Structured JSON response

### 8.2 Food Identification Prompt (Step 3)
```
You are a dietary safety assistant for a patient with the following profile:
{patient_profile}

The patient has submitted this image of food they are considering eating.
Additional context from patient: "{patient_text}"

Task 1 — Food Identification:
Identify the top 3 most likely foods or dishes in the image.
Consider the patient's nationality ({nationality}) and cultural context for localised food names.
For each option provide:
  - dish_name: string
  - confidence: "High" | "Medium" | "Low"
  - brief_description: string (1–2 sentences)
  - typical_key_ingredients: list of 5–8 main ingredients
Return as JSON array.
```

### 8.3 Dietary Safety Assessment Prompt (Step 4)
```
The patient has confirmed the food is: {confirmed_food}

Task 2 — Dietary Safety Assessment:
Based on the patient's medical profile and the typical ingredients of {confirmed_food},
identify any nutritional concerns.

For each concern provide:
  - nutrient_of_concern: string
  - severity: "High Risk" | "Moderate Risk" | "Low Risk / Monitor"
  - reason: string (plain language, max 2 sentences)
  - recommendation: string (actionable advice, e.g. "Avoid", "Limit portion to X", "Request sauce on the side")

Also provide:
  - overall_verdict: "Safe" | "Consume with Caution" | "Avoid"
  - summary: string (2–3 sentence plain language summary for patient)
  - positive_aspects: list of nutritional benefits relevant to patient's condition (if any)

Return as structured JSON. Use simple language appropriate for a patient audience.
```

---

## 9. Output Display (Patient-Facing UI)

### 9.1 Food Identification Panel
- Display top 3 food options as cards with:
  - Food name (localised)
  - Confidence indicator (colour-coded badge)
  - Key ingredients preview
  - "This is my food" confirmation button

### 9.2 Safety Assessment Panel
After patient confirms food:
- **Overall Verdict Banner**: Green (Safe) / Amber (Caution) / Red (Avoid)
- **Nutrient Concern Cards**: Each concern displayed with severity colour-coding
- **Positive Aspects**: What's good about this food for the patient
- **Actionable Recommendations**: Specific, practical tips (e.g., "Ask for less salt", "Small portion only")
- **Disclaimer**: "This is AI-generated dietary guidance. Always consult your dietitian or doctor for personalised medical advice."

---

## 10. Safety, Ethics & Compliance

### 10.1 Clinical Safety Guardrails
- The app is a **decision support tool**, not a diagnostic or prescriptive medical device
- All outputs must include a disclaimer directing patients to their healthcare team
- The LLM must be instructed to flag uncertainty and encourage clinician consultation
- High-risk flags (e.g., hyperkalemia risk for dialysis patients) should include an explicit "Speak to your dietitian before eating this" message

### 10.2 Data Privacy
- **MVP**: No persistent patient data; session-only storage
- **Production**: Must comply with relevant jurisdiction health data regulations:
  - HIPAA (USA)
  - GDPR (Europe)
  - PDPA (Singapore / Southeast Asia)
  - Australian Privacy Act / My Health Records Act
- Patient IDs should be anonymised; avoid storing identifiable information in LLM prompts
- Consider de-identification: refer to patients by ID, not name, in prompts

### 10.3 Intended Use Disclaimer
This application is intended as a **supplementary educational tool** to support dietary self-management. It is not a substitute for professional medical or dietetic advice. Clinical decisions should always be made by qualified healthcare professionals.

---

## 11. MVP Scope vs. Future Roadmap

### MVP (Phase 1)
- [ ] Clinician profile setup form
- [ ] Dietitian profile setup form
- [ ] Patient food submission (image + text)
- [ ] Food identification (top 3) with patient confirmation
- [ ] Dietary safety assessment output
- [ ] Streamlit web app, mobile-responsive
- [ ] Support for: CKD, Dialysis, Hypertension, Type 2 Diabetes
- [ ] Localised context for: Singapore, Malaysia, Australia, UK (initial)

### Phase 2
- [ ] Persistent patient profiles (database backend)
- [ ] Meal history log for patients
- [ ] Clinician/dietitian dashboard to review patient queries
- [ ] Expanded condition coverage (Heart Failure, Warfarin, Nephrotic Syndrome)
- [ ] Barcode scanning for packaged foods (Open Food Facts API integration)
- [ ] Nutrient database integration (USDA FoodData Central, AUSNUT)
- [ ] Multi-language support

### Phase 3
- [ ] Clinician-facing audit trail and alert system
- [ ] Integration with Electronic Health Records (EHR/EMR)
- [ ] Regulatory compliance pathway (TGA, FDA, CE marking as SaMD)
- [ ] Validated clinical study for efficacy and safety

---

## 12. File Structure (Proposed)

```
Food_ID_Bot/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── REQUIREMENTS.md             # This document
│
├── config/
│   └── conditions.py           # Supported conditions and nutrient flags
│
├── prompts/
│   ├── system_prompt.py        # System prompt builder
│   ├── food_identification.py  # Step 3 prompt template
│   └── safety_assessment.py    # Step 4 prompt template
│
├── models/
│   ├── patient_profile.py      # Patient profile dataclass/schema
│   └── assessment_output.py    # Structured output models
│
├── utils/
│   ├── llm_client.py           # Anthropic API wrapper
│   ├── image_utils.py          # Image preprocessing/encoding
│   └── profile_builder.py      # Profile serialisation for prompts
│
└── pages/
    ├── 01_clinician_setup.py   # Clinician profile page
    ├── 02_dietitian_setup.py   # Dietitian profile page
    └── 03_patient_view.py      # Patient-facing food submission page
```

---

## 13. Key Dependencies

```
anthropic>=0.40.0        # Claude API SDK
streamlit>=1.35.0        # Web framework
Pillow>=10.0.0           # Image handling
python-dotenv>=1.0.0     # Environment variable management
pydantic>=2.0.0          # Data validation for patient profiles and LLM outputs
```

---

## 14. Open Questions for Stakeholders

1. **Regulatory pathway**: Is this intended to be a regulated medical device (SaMD) or purely a patient education tool? This significantly impacts compliance requirements.
2. **Authentication**: Should clinician/dietitian setup pages require login? (Recommended: yes, even for MVP)
3. **Multi-patient support**: Should the MVP support multiple patients, or is a single active patient profile sufficient?
4. **Languages**: Which languages should be prioritised for localised food recognition context?
5. **Offline capability**: Is there a need for offline use (relevant for patients in low-connectivity settings)?
6. **Integration**: Are there existing EHR/EMR systems this needs to integrate with eventually?
