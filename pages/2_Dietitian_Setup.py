"""
Dietitian Setup page.
Dietitians enter demographics, dietary restrictions, nutritional priorities,
and any supporting clinical notes or educational materials.
"""
import streamlit as st

from config.conditions import ETHNICITIES, NATIONALITIES, NUTRIENTS
from models.patient_profile import PatientProfile
from utils.styles import inject_css

st.set_page_config(
    page_title="Dietitian Setup — Food ID Bot",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="expanded",
)
inject_css()

# ── Session state ─────────────────────────────────────────────────────────────
if "profile" not in st.session_state:
    st.session_state.profile = PatientProfile()
profile: PatientProfile = st.session_state.profile

# ── Guard ─────────────────────────────────────────────────────────────────────
st.title("🥗 Dietitian Setup")
st.markdown("Enter the patient's demographics and dietary restrictions.")

if not profile.clinician_complete:
    st.warning("⚠️ Please complete **Clinician Setup** first before entering dietitian details.")
    st.stop()

# ── Form ─────────────────────────────────────────────────────────────────────
with st.form("dietitian_form"):

    # Demographics
    st.subheader("Patient Demographics")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=1, max_value=120, value=profile.age or 50, step=1)
        nationality_opts = [""] + NATIONALITIES
        nat_idx = nationality_opts.index(profile.nationality) if profile.nationality in nationality_opts else 0
        nationality = st.selectbox("Nationality", nationality_opts, index=nat_idx)
    with col2:
        gender_opts = ["", "Male", "Female", "Non-binary / Other"]
        gen_idx = gender_opts.index(profile.gender) if profile.gender in gender_opts else 0
        gender = st.selectbox("Gender", gender_opts, index=gen_idx)
        ethnicity_opts = [""] + ETHNICITIES
        eth_idx = ethnicity_opts.index(profile.ethnicity) if profile.ethnicity in ethnicity_opts else 0
        ethnicity = st.selectbox("Ethnicity", ethnicity_opts, index=eth_idx)

    st.divider()

    # Dietary preferences
    st.subheader("Dietary Preferences")
    pref_col1, pref_col2 = st.columns(2)
    with pref_col1:
        vegetarian = st.checkbox("Vegetarian", value=profile.vegetarian)
        vegan = st.checkbox("Vegan", value=profile.vegan)
    with pref_col2:
        halal = st.checkbox("Halal", value=profile.halal)
        kosher = st.checkbox("Kosher", value=profile.kosher)

    st.divider()

    # Nutritional priorities
    st.subheader("Nutritional Priorities")
    st.markdown("**Nutrients to Restrict:**")
    restrict_cols = st.columns(3)
    nutrients_to_restrict = []
    for i, nutrient in enumerate(NUTRIENTS):
        with restrict_cols[i % 3]:
            if st.checkbox(nutrient, value=nutrient in profile.nutrients_to_restrict, key=f"r_{nutrient}"):
                nutrients_to_restrict.append(nutrient)

    st.markdown("**Nutrients to Encourage:**")
    encourage_cols = st.columns(3)
    nutrients_to_encourage = []
    for i, nutrient in enumerate(NUTRIENTS):
        with encourage_cols[i % 3]:
            if st.checkbox(nutrient, value=nutrient in profile.nutrients_to_encourage, key=f"e_{nutrient}"):
                nutrients_to_encourage.append(nutrient)

    st.divider()

    # Specific dietary restrictions
    st.subheader("Specific Dietary Restrictions")
    dietary_restrictions_text = st.text_area(
        "List specific restrictions (one per line)",
        value="\n".join(profile.dietary_restrictions),
        placeholder=(
            "e.g.\nNo processed meats\nLow phosphate diet\n"
            "Avoid salt substitutes\nNo grapefruit"
        ),
        height=100,
    )

    st.divider()

    # Clinical notes
    st.subheader("Clinical Notes")
    dietitian_notes = st.text_area(
        "Dietitian's notes and contextual information",
        value=profile.dietitian_notes,
        placeholder=(
            "e.g. Patient is a recent immigrant from Malaysia. Traditional diet includes "
            "rice-based meals. Struggling with salt reduction. Family often cooks at home."
        ),
        height=120,
    )

    educational_materials = st.text_area(
        "Educational materials / dietary guidelines (paste content here)",
        value=profile.educational_materials,
        placeholder="Paste any handouts or dietary guideline text provided to the patient...",
        height=150,
    )

    submitted = st.form_submit_button("💾 Save Dietitian Profile", type="primary")

    if submitted:
        profile.age = age
        profile.gender = gender
        profile.nationality = nationality
        profile.ethnicity = ethnicity
        profile.vegetarian = vegetarian
        profile.vegan = vegan
        profile.halal = halal
        profile.kosher = kosher
        profile.nutrients_to_restrict = nutrients_to_restrict
        profile.nutrients_to_encourage = nutrients_to_encourage
        profile.dietary_restrictions = [
            r.strip() for r in dietary_restrictions_text.splitlines() if r.strip()
        ]
        profile.dietitian_notes = dietitian_notes
        profile.educational_materials = educational_materials
        profile.dietitian_complete = True
        st.session_state.profile = profile
        st.success("✅ Dietitian profile saved! The patient can now use **Patient View**.")

# ── Summary ───────────────────────────────────────────────────────────────────
if profile.dietitian_complete:
    st.markdown("---")
    st.subheader("Current Dietitian Profile")
    if profile.nationality:
        st.write("**Nationality:**", profile.nationality)
    if profile.nutrients_to_restrict:
        st.write("**Nutrients to restrict:**", ", ".join(profile.nutrients_to_restrict))
    if profile.dietary_restrictions:
        st.write("**Dietary restrictions:**", ", ".join(profile.dietary_restrictions))
