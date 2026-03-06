"""
Patient View page.
Patients submit a food image (camera or upload) plus optional text,
confirm the identified food, and receive a personalised dietary safety assessment.
"""
import streamlit as st

from models.patient_profile import PatientProfile
from utils.llm_client import assess_food_safety, identify_food
from utils.styles import inject_css

st.set_page_config(
    page_title="Food Check — Food ID Bot",
    page_icon="📸",
    layout="centered",
    initial_sidebar_state="collapsed",
)
inject_css()

# ── Session state ─────────────────────────────────────────────────────────────
if "profile" not in st.session_state:
    st.session_state.profile = PatientProfile()

for key in ["food_options", "confirmed_food", "assessment"]:
    if key not in st.session_state:
        st.session_state[key] = None

profile: PatientProfile = st.session_state.profile

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📸 Food Check")
st.markdown("Take a photo or upload an image of your food to check if it's safe to eat.")

# ── Guards ────────────────────────────────────────────────────────────────────
if not profile.clinician_complete:
    st.error(
        "❌ Your medical profile has not been set up yet. "
        "Please ask your healthcare team to complete **Clinician Setup** first."
    )
    st.stop()

if not profile.dietitian_complete:
    st.warning("⚠️ Dietitian setup is pending. Results may be less personalised.")

# ── Step 1: Image input ───────────────────────────────────────────────────────
st.subheader("Step 1 — Add your food image")

input_method = st.radio(
    "How would you like to add the image?",
    ["📷 Use Camera", "📁 Upload File"],
    horizontal=True,
)

uploaded_file = None
if input_method == "📷 Use Camera":
    uploaded_file = st.camera_input("Take a photo of your food")
else:
    uploaded_file = st.file_uploader(
        "Upload a food image",
        type=["jpg", "jpeg", "png", "webp"],
    )

patient_text = st.text_area(
    "Additional context (optional)",
    placeholder=(
        "e.g. 'This is from a Singaporean hawker stall' or "
        "'I think this might be chicken rice'"
    ),
    height=80,
)

# ── Identify food ─────────────────────────────────────────────────────────────
if uploaded_file is not None:
    if st.button("🔍 Identify Food", type="primary"):
        # Reset downstream state
        st.session_state.food_options = None
        st.session_state.confirmed_food = None
        st.session_state.assessment = None

        with st.spinner("Analysing your food image…"):
            try:
                food_options = identify_food(uploaded_file, patient_text, profile)
                st.session_state.food_options = food_options
                st.rerun()
            except ValueError as e:
                if "ANTHROPIC_API_KEY" in str(e):
                    st.error(
                        "❌ API key not found. "
                        "Add `ANTHROPIC_API_KEY` to `.streamlit/secrets.toml`."
                    )
                else:
                    st.error(f"❌ Could not identify food: {e}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {e}")

# ── Step 2: Confirm food ──────────────────────────────────────────────────────
if st.session_state.food_options and st.session_state.confirmed_food is None:
    st.divider()
    st.subheader("Step 2 — Confirm your food")
    st.markdown("We identified these possible foods. Tap the one that matches:")

    confidence_icon = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}

    for i, food in enumerate(st.session_state.food_options):
        icon = confidence_icon.get(food.get("confidence", "Low"), "⚪")
        ingredients_preview = ", ".join(food.get("typical_key_ingredients", [])[:5])
        st.markdown(
            f"""<div class="food-card">
<strong>{icon} {food.get('dish_name', 'Unknown')}</strong>
<span style="color:#6c757d;font-size:0.85rem"> — {food.get('cuisine_origin', '')}</span><br>
<small>{food.get('brief_description', '')}</small><br>
<small><em>Key ingredients: {ingredients_preview}…</em></small>
</div>""",
            unsafe_allow_html=True,
        )
        if st.button(f"✅ This is my food", key=f"confirm_{i}"):
            st.session_state.confirmed_food = food
            st.rerun()

    if st.button("❌ None of these — try again"):
        st.session_state.food_options = None
        st.rerun()

# ── Step 3: Safety assessment ─────────────────────────────────────────────────
if st.session_state.confirmed_food is not None:
    confirmed = st.session_state.confirmed_food

    if st.session_state.assessment is None:
        st.divider()
        st.info(f"✅ Selected: **{confirmed.get('dish_name')}**")

        if st.button("⚕️ Check Safety for My Conditions", type="primary"):
            with st.spinner("Assessing dietary safety… this may take a moment."):
                try:
                    assessment = assess_food_safety(confirmed, profile)
                    st.session_state.assessment = assessment
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Safety assessment failed: {e}")

    if st.session_state.assessment:
        assessment = st.session_state.assessment
        dish_name = confirmed.get("dish_name", "this food")

        st.divider()
        st.subheader(f"Step 3 — Safety Assessment: {dish_name}")

        # Verdict banner
        verdict = assessment.get("overall_verdict", "Consume with Caution")
        verdict_class = {
            "Safe": "verdict-safe",
            "Consume with Caution": "verdict-caution",
            "Avoid": "verdict-avoid",
        }.get(verdict, "verdict-caution")
        verdict_icon = {
            "Safe": "✅",
            "Consume with Caution": "⚠️",
            "Avoid": "🚫",
        }.get(verdict, "⚠️")

        st.markdown(
            f"""<div class="{verdict_class}">
<h2 style="margin:0">{verdict_icon} {verdict}</h2>
<p style="margin:0.5rem 0 0">{assessment.get('summary', '')}</p>
</div>""",
            unsafe_allow_html=True,
        )

        # Nutrient concerns
        concerns = assessment.get("nutrient_concerns", [])
        if concerns:
            st.subheader("⚠️ Nutritional Concerns")
            for concern in concerns:
                severity = concern.get("severity", "Low Risk / Monitor")
                if "High" in severity:
                    css_class = "concern-high"
                elif "Moderate" in severity:
                    css_class = "concern-moderate"
                else:
                    css_class = "concern-low"

                st.markdown(
                    f"""<div class="{css_class}">
<strong>{concern.get('nutrient', '')}</strong>
<em style="color:#666;font-size:0.9rem"> — {severity}</em><br>
{concern.get('reason', '')}<br>
<strong>👉 {concern.get('recommendation', '')}</strong>
</div>""",
                    unsafe_allow_html=True,
                )

        # Positive aspects
        positives = assessment.get("positive_aspects", [])
        if positives:
            st.subheader("✅ Positive Aspects")
            for p in positives:
                st.markdown(f"- {p}")

        # Preparation tips
        tips = assessment.get("preparation_tips", [])
        if tips:
            st.subheader("💡 Tips to Make It Safer")
            for tip in tips:
                st.markdown(f"- {tip}")

        # When to seek advice
        seek_advice = assessment.get("when_to_seek_advice", "")
        if seek_advice:
            st.info(f"💬 **When to check with your dietitian:** {seek_advice}")

        # Reset
        st.divider()
        if st.button("🔄 Check a different food"):
            st.session_state.food_options = None
            st.session_state.confirmed_food = None
            st.session_state.assessment = None
            st.rerun()

# ── Disclaimer ────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "⚕️ *This is AI-generated dietary guidance for educational purposes only. "
    "It is not a substitute for professional medical or dietetic advice. "
    "Always consult your dietitian or doctor before making changes to your diet.*"
)
