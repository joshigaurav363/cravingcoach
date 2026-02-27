import streamlit as st
from datetime import datetime
import pandas as pd
from supabase import create_client

# Page config
st.set_page_config(page_title="Cravings Coach", layout="wide")


# Initialize Supabase
@st.cache_resource
def init_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


supabase = init_supabase()

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'cravings' not in st.session_state:
    st.session_state.cravings = []
if 'show_actions' not in st.session_state:
    st.session_state.show_actions = False
if 'current_craving' not in st.session_state:
    st.session_state.current_craving = ""


# Authentication functions
def sign_in(email, password):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response
    except Exception as e:
        st.error(f"Login error: {e}")
        return None


def sign_up(email, password):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return response
    except Exception as e:
        st.error(f"Sign up error: {e}")
        return None


def sign_out():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.cravings = []
    st.session_state.show_actions = False
    st.session_state.current_craving = ""


# Load user's cravings
def load_cravings(user_id):
    try:
        response = supabase.table("cravings") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .execute()
        return response.data
    except Exception as e:
        st.error(f"Error loading: {e}")
        return []


# Save a new craving
def save_craving(user_id, craving_item, action):
    try:
        new_entry = {
            "user_id": user_id,
            "craving_item": craving_item,
            "created_at": datetime.now().isoformat(),
            "action_taken": action,
            "success": True
        }
        result = supabase.table("cravings").insert(new_entry).execute()
        return True
    except Exception as e:
        st.error(f"Error saving: {e}")
        return False


# Authentication UI
if not st.session_state.user:
    st.title("🍽️ Cravings Coach")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="login_btn"):
            with st.spinner("Logging in..."):
                response = sign_in(email, password)
                if response:
                    st.session_state.user = response.user
                    st.session_state.cravings = load_cravings(response.user.id)
                    st.rerun()

    with tab2:
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_password")
        confirm = st.text_input("Confirm Password", type="password", key="confirm_password")
        if st.button("Sign Up", key="signup_btn"):
            if new_password != confirm:
                st.error("Passwords don't match")
            else:
                with st.spinner("Creating account..."):
                    response = sign_up(new_email, new_password)
                    if response:
                        st.success("Account created! Please login.")

    st.stop()

# ===== MAIN APP =====

# Sidebar
with st.sidebar:
    st.header(f"👤 {st.session_state.user.email}")
    if st.button("🚪 Logout"):
        sign_out()
        st.rerun()

    st.divider()
    st.header("📊 Stats")
    st.write(f"Total cravings: {len(st.session_state.cravings)}")

    if st.button("🔄 Refresh"):
        st.session_state.cravings = load_cravings(st.session_state.user.id)
        st.rerun()

# Main content
st.title("🍽️ Cravings Coach")

# Input section
col1, col2 = st.columns([3, 1])
with col1:
    craving_input = st.text_input("What are you craving?", placeholder="e.g., chips, chocolate...")
with col2:
    if st.button("📝 Log Craving", type="primary", use_container_width=True):
        if craving_input and craving_input.strip():
            st.session_state.current_craving = craving_input
            st.session_state.show_actions = True
            st.rerun()
        else:
            st.warning("Enter a craving")

# Action buttons (shown only when needed)
if st.session_state.show_actions and st.session_state.current_craving:
    st.subheader(f"What to do about **{st.session_state.current_craving}**?")

    a1, a2, a3 = st.columns(3)

    with a1:
        if st.button("💪 Pushups", key="push", use_container_width=True):
            if save_craving(st.session_state.user.id, st.session_state.current_craving, "pushups"):
                st.session_state.cravings = load_cravings(st.session_state.user.id)
                st.success("✅ Saved! Do 10 pushups")
                st.session_state.show_actions = False
                st.session_state.current_craving = ""
                st.rerun()

    with a2:
        if st.button("💧 Water", key="water", use_container_width=True):
            if save_craving(st.session_state.user.id, st.session_state.current_craving, "water"):
                st.session_state.cravings = load_cravings(st.session_state.user.id)
                st.success("✅ Saved! Drink water")
                st.session_state.show_actions = False
                st.session_state.current_craving = ""
                st.rerun()

    with a3:
        if st.button("🥜 Healthy Snack", key="snack", use_container_width=True):
            if save_craving(st.session_state.user.id, st.session_state.current_craving, "healthy snack"):
                st.session_state.cravings = load_cravings(st.session_state.user.id)
                st.success("✅ Saved! Have a healthy snack")
                st.session_state.show_actions = False
                st.session_state.current_craving = ""
                st.rerun()

# Dashboard
st.divider()
st.subheader("📊 Your Cravings")

if st.session_state.cravings:
    df = pd.DataFrame(st.session_state.cravings)

    # Show table
    if 'craving_item' in df.columns:
        show_df = df[['craving_item', 'created_at', 'action_taken']].copy()
        show_df['created_at'] = pd.to_datetime(show_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        show_df.columns = ['Craving', 'Time', 'Action']
        st.dataframe(show_df, use_container_width=True, hide_index=True)

    # Quick stats
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total", len(df))
    with col2:
        if 'craving_item' in df.columns:
            top = df['craving_item'].mode()[0] if len(df) > 0 else "None"
            st.metric("Top Craving", top)
else:
    st.info("No cravings yet. Log your first one above!")