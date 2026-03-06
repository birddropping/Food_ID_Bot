"""
Clinician Setup page.
Clinicians enter the patient's medical conditions, medications, dialysis status,
and optional recent lab values.
"""
import streamlit as st

from config.conditions import CONDITIONS, DIALYSIS_TYPES
from models.patient_profile import PatientProfile
from utils.styles import inject_css

st.set_page_config(
    page_title="Clinician Setup — Food ID Bot",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="expanded",
)
inject_css()

# ── Session state ─────────────────────────────────────────────────────────────
if "profile" not in st.session_state:
    st.session_state.profile = PatientProfile()
profile: PatientProfile = st.session_state.profile

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🏥 Clinician Setup")
st.markdown("Enter the patient's medical conditions and clinical parameters.")

# ── Form ─────────────────────────────────────────────────────────────────────
with st.form("clinician_form"):

    # Medical conditions
    st.subheader("Medical Conditions")
    selected_conditions: list[str] = []
    for category, condition_list in CONDITIONS.items():
        st.markdown(f"**{category}**")
        cols = st.columns(2)
        for idx, condition in enumerate(condition_list):
            with cols[idx % 2]:
                checked = st.checkbox(
                    condition,
                    value=condition in profile.conditions,
                    key=f"cond_{condition}",
                )
                if checked:
                    selected_conditions.append(condition)

    st.divider()

    # Dialysis
    st.subheader("Dialysis")
    dialysis_idx = DIALYSIS_TYPES.index(profile.dialysis_type) if profile.dialysis_type in DIALYSIS_TYPES else 0
    dialysis_type = st.selectbox("Dialysis Type", DIALYSIS_TYPES, index=dialysis_idx)

    fluid_restriction = st.number_input(
        "Fluid Restriction (mL/day) — leave 0 if not applicable",
        min_value=0,
        max_value=5000,
        value=profile.fluid_restriction_ml or 0,
        step=100,
    )

    st.divider()

    # Medications
    st.subheader("Current Medications")
    medications_text = st.text_area(
        "List medications (one per line)",
        value="\n".join(profile.medications),
        placeholder="e.g.\nWarfarin 5mg daily\nAmlodipine 10mg daily\nInsulin Glargine 20 units nocte",
        height=100,
    )

    st.divider()

    # Lab values
    st.subheader("Recent Lab Values (optional)")
    col1, col2 = st.columns(2)
    with col1:
        egfr = st.number_input(
            "eGFR (mL/min/1.73m²)",
            min_value=0.0, max_value=150.0,
            value=float(profile.egfr or 0), step=1.0,
        )
        serum_k = st.number_input(
            "Serum Potassium (mmol/L)",
            min_value=0.0, max_value=10.0,
            value=float(profile.serum_potassium or 0.0), step=0.1, format="%.1f",
        )
        hba1c = st.number_input(
            "HbA1c (%)",
            min_value=0.0, max_value=20.0,
            value=float(profile.hba1c or 0.0), step=0.1, format="%.1f",
        )
    with col2:
        serum_phos = st.number_input(
            "Serum Phosphate (mmol/L)",
            min_value=0.0, max_value=5.0,
            value=float(profile.serum_phosphate or 0.0), step=0.01, format="%.2f",
        )
        ldl = st.number_input(
            "LDL Cholesterol (mmol/L)",
            min_value=0.0, max_value=20.0,
            value=float(profile.ldl_cholesterol or 0.0), step=0.1, format="%.1f",
        )

    submitted = st.form_submit_button("💾 Save Clinician Profile", type="primary")

    if submitted:
        profile.conditions = selected_conditions
        profile.dialysis_type = dialysis_type
        profile.fluid_restriction_ml = fluid_restriction if fluid_restriction > 0 else None
        profile.medications = [m.strip() for m in medications_text.splitlines() if m.strip()]
        profile.egfr = egfr if egfr > 0 else None
        profile.serum_potassium = serum_k if serum_k > 0 else None
        profile.serum_phosphate = serum_phos if serum_phos > 0 else None
        profile.hba1c = hba1c if hba1c > 0 else None
        profile.ldl_cholesterol = ldl if ldl > 0 else None
        profile.clinician_complete = bool(selected_conditions)
        st.session_state.profile = profile

        if profile.clinician_complete:
            st.success("✅ Clinician profile saved! Proceed to **Dietitian Setup**.")
        else:
            st.warning("Please select at least one medical condition.")

# ── Current profile summary (read-only) ───────────────────────────────────────
if profile.clinician_complete:
    st.markdown("---")
    st.subheader("Current Profile")
    st.write("**Conditions:**", ", ".join(profile.conditions))
    if profile.dialysis_type != "None":
        st.write("**Dialysis:**", profile.dialysis_type)
    if profile.medications:
        st.write("**Medications:**", ", ".join(profile.medications))
