"""
Food ID Bot — Main entry point.
Initialises session state and shows the setup status dashboard.
"""
import streamlit as st

from models.patient_profile import PatientProfile
from utils.styles import inject_css

st.set_page_config(
    page_title="Food ID Bot",
    page_icon="🍽️",
    layout="centered",
    initial_sidebar_state="expanded",
)

inject_css()


def init_session_state():
    if "profile" not in st.session_state:
        st.session_state.profile = PatientProfile()


init_session_state()
profile: PatientProfile = st.session_state.profile

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🍽️ Food ID Bot")
st.markdown(
    "**AI-powered dietary guidance for patients with renal, cardiovascular "
    "or diabetic conditions.**"
)
st.markdown("---")

# ── Setup status ──────────────────────────────────────────────────────────────
st.subheader("Setup Status")
col1, col2 = st.columns(2)
with col1:
    if profile.clinician_complete:
        st.markdown(
            '<p class="status-complete">✅ Clinician Setup</p>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<p class="status-pending">⚠️ Clinician Setup Required</p>',
            unsafe_allow_html=True,
        )
with col2:
    if profile.dietitian_complete:
        st.markdown(
            '<p class="status-complete">✅ Dietitian Setup</p>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<p class="status-pending">⚠️ Dietitian Setup Pending</p>',
            unsafe_allow_html=True,
        )

st.markdown("---")

# ── How it works ──────────────────────────────────────────────────────────────
st.subheader("How it works")
st.markdown(
    """
1. **Clinician Setup** — Enter the patient's diagnoses, medications, and key lab values
2. **Dietitian Setup** — Add demographics, dietary restrictions, and nutritional guidance
3. **Patient View** — Take or upload a food photo to get an instant personalised safety assessment
"""
)

if not profile.clinician_complete:
    st.info("👈 Open the sidebar and go to **Clinician Setup** to get started.")
elif not profile.dietitian_complete:
    st.info("👈 Navigate to **Dietitian Setup** to complete the patient profile.")
else:
    st.success(
        "✅ Profile complete! Go to **Patient View** to start checking foods."
    )

st.markdown("---")
st.caption(
    "⚕️ *This app provides AI-generated dietary guidance for educational purposes only. "
    "Always consult your dietitian or doctor for personalised medical advice.*"
)
