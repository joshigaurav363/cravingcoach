
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
if 'history' not in st.session_state:
    # Load from Supabase on startup
    try:
        response = supabase.table("cravings").select("*").order("created_at", desc=True).execute()
        st.session_state.history = response.data
    except Exception as e:
        st.error(f"Error loading: {e}")
        st.session_state.history = []

if 'awaiting_action' not in st.session_state:
    st.session_state.awaiting_action = False
if 'current_craving' not in st.session_state:
    st.session_state.current_craving = ""
if 'temp_craving' not in st.session_state:
    st.session_state.temp_craving = ""

# Title
st.title("🍽️ Cravings Coach")

# DEBUG: Show current state
st.write("DEBUG - Awaiting action:", st.session_state.awaiting_action)
st.write("DEBUG - Current craving:", st.session_state.current_craving)

# Create two columns for layout
left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("Log Your Craving")

    # Input section - store in temp_craving first
    craving = st.text_input("What are you craving?", value=st.session_state.temp_craving, key="craving_input")
    st.session_state.temp_craving = craving
    st.write("DEBUG - You typed:", craving)

    # Only log when they click "Log It" button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Log Craving", use_container_width=True):
            st.write("DEBUG - Log button clicked")
            if craving and craving.strip():
                st.write("DEBUG - Setting current craving to:", craving)
                st.session_state.current_craving = craving
                st.session_state.awaiting_action = True
                st.session_state.temp_craving = ""  # Clear input
                st.rerun()
            else:
                st.warning("Please enter a craving first")

    with col2:
        if st.button("🔄 Clear", use_container_width=True):
            st.session_state.temp_craving = ""
            st.session_state.current_craving = ""
            st.session_state.awaiting_action = False
            st.rerun()

    # Show action buttons only when awaiting action
    if st.session_state.awaiting_action and st.session_state.current_craving:
        st.subheader(f"What will you do about **{st.session_state.current_craving}**?")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💪 Pushups", use_container_width=True):
                st.write("DEBUG - Pushups clicked")
                # Save to Supabase
                new_entry = {
                    "craving_item": st.session_state.current_craving,
                    "created_at": datetime.now().isoformat(),
                    "action_taken": "pushups",
                    "success": True
                }
                try:
                    result = supabase.table("cravings").insert(new_entry).execute()
                    st.write("DEBUG - Saved to Supabase")
                    # Refresh history
                    response = supabase.table("cravings").select("*").order("created_at", desc=True).execute()
                    st.session_state.history = response.data
                    st.success("✅ Saved! Try 10 pushups now 💪")
                except Exception as e:
                    st.error(f"Error saving: {e}")

                # Reset state
                st.session_state.awaiting_action = False
                st.session_state.current_craving = ""
                st.rerun()

        with col2:
            if st.button("💧 Water", use_container_width=True):
                st.write("DEBUG - Water clicked")
                new_entry = {
                    "craving_item": st.session_state.current_craving,
                    "created_at": datetime.now().isoformat(),
                    "action_taken": "water",
                    "success": True
                }
                try:
                    result = supabase.table("cravings").insert(new_entry).execute()
                    st.write("DEBUG - Saved to Supabase")
                    response = supabase.table("cravings").select("*").order("created_at", desc=True).execute()
                    st.session_state.history = response.data
                    st.success("✅ Saved! Drink a full glass of water 💧")
                except Exception as e:
                    st.error(f"Error saving: {e}")

                st.session_state.awaiting_action = False
                st.session_state.current_craving = ""
                st.rerun()

        with col3:
            if st.button("🥜 Healthy Snack", use_container_width=True):
                st.write("DEBUG - Snack clicked")
                new_entry = {
                    "craving_item": st.session_state.current_craving,
                    "created_at": datetime.now().isoformat(),
                    "action_taken": "healthy snack",
                    "success": True
                }
                try:
                    result = supabase.table("cravings").insert(new_entry).execute()
                    st.write("DEBUG - Saved to Supabase")
                    response = supabase.table("cravings").select("*").order("created_at", desc=True).execute()
                    st.session_state.history = response.data
                    st.success("✅ Saved! Try roasted chana or fruits 🥜")
                except Exception as e:
                    st.error(f"Error saving: {e}")

                st.session_state.awaiting_action = False
                st.session_state.current_craving = ""
                st.rerun()

with right_col:
    st.subheader("📊 Your Cravings Dashboard")

    # Show history
    if st.session_state.history:
        st.write("DEBUG - History has", len(st.session_state.history), "entries")

        # Convert to DataFrame for better display
        df = pd.DataFrame(st.session_state.history)

        # Show recent entries
        if 'craving_item' in df.columns:
            display_df = df[['craving_item', 'created_at', 'action_taken']].copy()
            display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(display_df.head(10), use_container_width=True)
        else:
            st.dataframe(df.head(10))


        # Initialize Supabase
        @st.cache_resource
        def init_supabase():
            return create_client(
                st.secrets["SUPABASE_URL"],
                st.secrets["SUPABASE_KEY"]
            )


        supabase = init_supabase()

        # Initialize session state
        if 'history' not in st.session_state:
            # Load from Supabase on startup
            try:
                response = supabase.table("cravings").select("*").order("created_at", desc=True).execute()
                st.session_state.history = response.data
                # DEBUG: Print what we got
                st.write("DEBUG - Raw data from Supabase:", response.data)
                if response.data:
                    st.write("DEBUG - First item keys:", response.data[0].keys())
            except Exception as e:
                st.error(f"Error loading: {e}")
                st.session_state.history = []

        # Simple analytics
        st.subheader("📈 Insights")

        col1, col2 = st.columns(2)
        with col1:
            # Total cravings
            st.metric("Total Cravings", len(df))

        with col2:
            # Most common craving
            if 'craving_item' in df.columns and len(df) > 0:
                top_craving = df['craving_item'].mode()[0] if not df['craving_item'].mode().empty else "None"
                st.metric("Most Common", top_craving)

        # Actions breakdown
        if 'action_taken' in df.columns and not df['action_taken'].isna().all():
            st.subheader("Actions Taken")
            action_counts = df['action_taken'].value_counts()
            st.bar_chart(action_counts)
    else:
        st.info("No cravings logged yet. Start by logging one!")

# Sidebar with stats
with st.sidebar:
    st.header("📋 Quick Stats")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.write(f"Total entries: {len(df)}")

        # Today's count
        if 'created_at' in df.columns:
            today = datetime.now().strftime('%Y-%m-%d')
            df['date'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d')
            today_count = len(df[df['date'] == today])
            st.write(f"Today: {today_count} cravings")

        # Clear button (for testing)
        if st.button("🔄 Refresh Data"):
            response = supabase.table("cravings").select("*").order("created_at", desc=True).execute()
            st.session_state.history = response.data
            st.rerun()
    else:
        st.write("No data yet")


# Add this somewhere in your app, maybe after the action buttons
with st.expander("🧪 Test Database"):
    if st.button("Test Save to Supabase"):
        test_entry = {
            "craving_item": "test craving",
            "created_at": datetime.now().isoformat(),
            "action_taken": "test",
            "success": True
        }
        try:
            result = supabase.table("cravings").insert(test_entry).execute()
            st.success(f"Test saved! Response: {result}")
        except Exception as e:
            st.error(f"Test failed: {e}")