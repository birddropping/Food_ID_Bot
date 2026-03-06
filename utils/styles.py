SHARED_CSS = """
<style>
    /* Mobile-first layout */
    .main .block-container {
        padding: 1rem 1rem 3rem 1rem;
        max-width: 640px;
    }
    /* Full-width buttons */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-size: 1rem;
        padding: 0.6rem 1rem;
    }
    /* Status indicators */
    .status-complete { color: #28a745; font-weight: bold; }
    .status-pending  { color: #dc3545; font-weight: bold; }

    /* Food identification cards */
    .food-card {
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.6rem;
        background-color: #f8f9fa;
    }

    /* Verdict banners */
    .verdict-safe {
        background: #d4edda;
        border: 2px solid #28a745;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .verdict-caution {
        background: #fff3cd;
        border: 2px solid #ffc107;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .verdict-avoid {
        background: #f8d7da;
        border: 2px solid #dc3545;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        margin-bottom: 1rem;
    }

    /* Nutrient concern cards */
    .concern-high {
        border-left: 4px solid #dc3545;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        background: #fff5f5;
        border-radius: 0 8px 8px 0;
    }
    .concern-moderate {
        border-left: 4px solid #fd7e14;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        background: #fff8f0;
        border-radius: 0 8px 8px 0;
    }
    .concern-low {
        border-left: 4px solid #ffc107;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        background: #fffdf0;
        border-radius: 0 8px 8px 0;
    }
</style>
"""


def inject_css():
    import streamlit as st
    st.markdown(SHARED_CSS, unsafe_allow_html=True)
