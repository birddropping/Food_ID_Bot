import json
import os
import re

import anthropic
import streamlit as st

from models.patient_profile import PatientProfile
from utils.image_utils import encode_image_for_api
from utils.profile_builder import build_profile_context

MODEL = "claude-opus-4-6"


def get_client() -> anthropic.Anthropic:
    """Resolve API key from Streamlit secrets or environment, return client."""
    api_key = None
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except (KeyError, FileNotFoundError):
        api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not found. "
            "Add it to .streamlit/secrets.toml or set the environment variable."
        )
    return anthropic.Anthropic(api_key=api_key)


def _extract_json(text: str):
    """
    Extract JSON from an LLM response that may contain markdown code fences
    or surrounding prose.
    """
    # Try JSON inside a code fence first
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try raw parse
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Try to find the first JSON array or object in the text
    for pattern in [r"\[[\s\S]*\]", r"\{[\s\S]*\}"]:
        match = re.search(pattern, text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

    raise ValueError(
        f"Could not extract valid JSON from model response. "
        f"Raw output (first 400 chars): {text[:400]}"
    )


def identify_food(
    uploaded_file,
    patient_text: str,
    profile: PatientProfile,
) -> list[dict]:
    """
    Step 3 — Identify the top-3 probable foods from the submitted image.

    Uses streaming to avoid HTTP timeouts on slow connections.
    Returns a list of up to 3 dicts with keys:
        dish_name, confidence, brief_description,
        typical_key_ingredients, cuisine_origin
    """
    client = get_client()
    profile_context = build_profile_context(profile)
    image_b64, media_type = encode_image_for_api(uploaded_file)

    nationality_hint = profile.nationality or "unknown"
    patient_note = (
        f"\nAdditional context from patient: \"{patient_text.strip()}\""
        if patient_text.strip()
        else ""
    )

    system_prompt = f"""You are a clinical dietary assistant helping patients with chronic \
medical conditions identify foods and assess their suitability.

Patient medical and dietary profile:
{profile_context}

Rules:
- Always respond with valid JSON only — no prose outside the JSON.
- Use culturally appropriate, localised food names for the patient's nationality.
- If you cannot identify any food in the image, return an array with one item \
  where dish_name is "Unable to identify" and confidence is "Low"."""

    user_prompt = f"""Identify the food shown in this image.{patient_note}

Considering the patient's nationality ({nationality_hint}), return the top 3 \
most likely foods or dishes.

Respond with a JSON array of exactly 3 objects. Each object must have:
- "dish_name": string (localised name)
- "confidence": "High" | "Medium" | "Low"
- "brief_description": string (1–2 sentences)
- "typical_key_ingredients": array of 5–8 ingredient strings
- "cuisine_origin": string (e.g. "Chinese", "Indian", "Western")

JSON only — no other text."""

    with client.messages.stream(
        model=MODEL,
        max_tokens=1024,
        thinking={"type": "adaptive"},
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_b64,
                        },
                    },
                    {"type": "text", "text": user_prompt},
                ],
            }
        ],
    ) as stream:
        final = stream.get_final_message()

    # Extract text blocks only (skip thinking blocks)
    raw = ""
    for block in final.content:
        if block.type == "text":
            raw = block.text
            break

    result = _extract_json(raw)
    if isinstance(result, list):
        return result[:3]
    raise ValueError(f"Expected JSON array from food identification, got: {type(result)}")


def assess_food_safety(
    confirmed_food: dict,
    profile: PatientProfile,
) -> dict:
    """
    Step 4 — Assess dietary safety of a confirmed food for this patient.

    Uses streaming + adaptive thinking for nuanced clinical reasoning.
    Returns a dict with keys:
        overall_verdict, summary, nutrient_concerns,
        positive_aspects, preparation_tips, when_to_seek_advice
    """
    client = get_client()
    profile_context = build_profile_context(profile)

    dish_name = confirmed_food.get("dish_name", "the selected food")
    dish_description = confirmed_food.get("brief_description", "")
    dish_ingredients = ", ".join(confirmed_food.get("typical_key_ingredients", []))

    system_prompt = f"""You are a clinical dietary assistant with deep expertise in \
renal, cardiovascular, and diabetic nutrition. You apply evidence-based guidelines \
(KDOQI 2020, ADA 2024 Standards of Care, AHA/ACC 2019) to assess food safety for \
patients with complex medical needs.

Patient medical and dietary profile:
{profile_context}

Rules:
- Always respond with valid JSON only — no prose outside the JSON.
- Use plain, patient-friendly language. Avoid medical jargon.
- When conditions create conflicting dietary requirements (e.g. potassium is beneficial \
  for hypertension but dangerous in CKD), always apply the more restrictive constraint \
  and explicitly flag the conflict in the reason field.
- Only include nutrient_concerns that are actually relevant to this patient's conditions.
- overall_verdict must be one of: "Safe", "Consume with Caution", "Avoid"."""

    user_prompt = f"""The patient has confirmed they are considering eating:

Dish: {dish_name}
Description: {dish_description}
Typical key ingredients: {dish_ingredients}

Provide a dietary safety assessment. Return a JSON object with these exact fields:

{{
  "overall_verdict": "Safe" | "Consume with Caution" | "Avoid",
  "summary": "2–3 plain-language sentences for the patient",
  "nutrient_concerns": [
    {{
      "nutrient": "string",
      "severity": "High Risk" | "Moderate Risk" | "Low Risk / Monitor",
      "reason": "plain language, max 2 sentences",
      "recommendation": "specific actionable advice (e.g. Avoid, Limit to half portion, Ask for sauce on side)"
    }}
  ],
  "positive_aspects": ["array of nutritional benefits relevant to patient's conditions"],
  "preparation_tips": ["practical tips to make the dish safer, if applicable"],
  "when_to_seek_advice": "one sentence — when patient should consult dietitian/doctor about this food"
}}

JSON only — no other text."""

    with client.messages.stream(
        model=MODEL,
        max_tokens=2048,
        thinking={"type": "adaptive"},
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        final = stream.get_final_message()

    raw = ""
    for block in final.content:
        if block.type == "text":
            raw = block.text
            break

    return _extract_json(raw)
