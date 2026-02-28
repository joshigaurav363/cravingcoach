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
if 'last_craving_time' not in st.session_state:
    st.session_state.last_craving_time = None
if 'last_craving_item' not in st.session_state:
    st.session_state.last_craving_item = None
if 'temp_craving' not in st.session_state:
    st.session_state.temp_craving = ""


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


# Save a new craving with alternative
def save_craving(user_id, craving_item, alternative, did_eat_craved):
    try:
        new_entry = {
            "user_id": user_id,
            "craving_item": craving_item,
            "created_at": datetime.now().isoformat(),
            "action_taken": alternative,
            "alternative_chosen": alternative,
            "did_eat_craved": did_eat_craved,
            "success": not did_eat_craved
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

    # Success rate
    if st.session_state.cravings:
        df = pd.DataFrame(st.session_state.cravings)
        if 'did_eat_craved' in df.columns:
            success_count = len(df[df['did_eat_craved'] == False])
            success_rate = (success_count / len(df)) * 100
            st.write(f"Success rate: {success_rate:.1f}%")

    if st.button("🔄 Refresh"):
        st.session_state.cravings = load_cravings(st.session_state.user.id)
        st.rerun()

    # Smart notification
    if st.session_state.last_craving_time and st.session_state.last_craving_item:
        st.divider()
        st.header("⏰ Remember")
        current_hour = datetime.now().hour
        last_hour = st.session_state.last_craving_time

        if abs(current_hour - last_hour) <= 2:
            st.info(f"Around this time you craved **{st.session_state.last_craving_item}**")

            # Find what they chose last time
            if st.session_state.cravings:
                last_entry = st.session_state.cravings[0]
                if 'alternative_chosen' in last_entry:
                    st.caption(f"Last time: **{last_entry['alternative_chosen']}**")

                    if st.button("📝 Log same craving"):
                        st.session_state.temp_craving = st.session_state.last_craving_item
                        st.rerun()

# Main content
st.title("🍽️ Cravings Coach")

# Smart greeting
current_hour = datetime.now().hour
if current_hour < 12:
    greeting = "Morning"
elif current_hour < 17:
    greeting = "Afternoon"
else:
    greeting = "Evening"
st.caption(f"Good {greeting}, {st.session_state.user.email.split('@')[0]}")

# Input section
col1, col2 = st.columns([3, 1])
with col1:
    craving_input = st.text_input(
        "What are you craving?",
        value=st.session_state.temp_craving,
        placeholder="e.g., chips, chocolate, ice cream...",
        key="main_craving_input"
    )
with col2:
    if st.button("📝 Log Craving", type="primary", use_container_width=True):
        if craving_input and craving_input.strip():
            st.session_state.current_craving = craving_input
            st.session_state.show_actions = True
            st.session_state.temp_craving = ""
            st.rerun()
        else:
            st.warning("Enter a craving")

# Action buttons with alternatives
if st.session_state.show_actions and st.session_state.current_craving:
    st.divider()
    st.subheader(f"🌱 Instead of **{st.session_state.current_craving}**, try:")

    # Smart alternatives based on common cravings
    craving_lower = st.session_state.current_craving.lower()

    if "chip" in craving_lower or "fry" in craving_lower:
        alternatives = [
            "🥜 Roasted almonds (handful)",
            "🌰 Roasted chana",
            "🍎 Apple slices with cinnamon",
            "🥕 Carrot sticks",
            "🍿 Air-popped popcorn"
        ]
    elif "chocolate" in craving_lower or "candy" in craving_lower or "sweet" in craving_lower:
        alternatives = [
            "🍫 Dark chocolate (2 squares)",
            "🫐 Greek yogurt with berries",
            "🥜 Dates with almonds",
            "🍌 Frozen banana bites",
            "🍎 Apple with peanut butter"
        ]
    elif "ice cream" in craving_lower or "cold" in craving_lower:
        alternatives = [
            "🫐 Frozen Greek yogurt",
            "🍌 Frozen banana nice cream",
            "🥭 Frozen mango chunks",
            "🥛 Cold milk with cinnamon",
            "🧊 Flavored sparkling water"
        ]
    elif "pizza" in craving_lower or "cheese" in craving_lower:
        alternatives = [
            "🧀 Cottage cheese with herbs",
            "🍅 Roasted tomatoes with basil",
            "🥑 Avocado toast",
            "🍄 Grilled mushrooms",
            "🌮 Veggie wrap"
        ]
    else:
        alternatives = [
            "🥜 Handful of nuts",
            "🫐 Greek yogurt",
            "🍎 Fresh fruit",
            "🥕 Veggie sticks",
            "🌰 Roasted chana"
        ]

    # Add "Other" option
    alternatives.append("✨ Other (specify)")

    # Let user choose
    chosen = st.radio(
        "What will you have instead?",
        alternatives,
        key="alternative_choice",
        index=None  # No default selection
    )

    # Custom input if "Other" selected
    custom = ""
    if chosen == "✨ Other (specify)":
        custom = st.text_input(
            "What will you have?",
            placeholder="e.g., a smoothie, dates, etc.",
            key="custom_alternative"
        )

    st.divider()

    # Option to still eat the craved item
    col1, col2 = st.columns(2)
    with col1:
        eat_craved = st.checkbox(
            "😋 I'm having the real thing today",
            key="eat_craved",
            help="No judgment! Tracking honestly helps more."
        )

    with col2:
        # Show a motivational message
        if not eat_craved:
            st.caption("💪 Proud of you for trying an alternative!")
        else:
            st.caption("🌱 Next time, maybe try an alternative?")

    st.divider()

    # Save button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("✅ Save Choice", type="primary", use_container_width=True):
            # Determine final choice
            if eat_craved:
                final_choice = "Ate the craved item"
            elif chosen == "✨ Other (specify)" and custom:
                final_choice = custom
            elif chosen:
                final_choice = chosen
            else:
                st.warning("Please select an alternative or check 'having the real thing'")
                st.stop()

            # Save to database
            if save_craving(
                    st.session_state.user.id,
                    st.session_state.current_craving,
                    final_choice,
                    eat_craved
            ):
                # Refresh data
                st.session_state.cravings = load_cravings(st.session_state.user.id)

                # Store for notifications
                st.session_state.last_craving_time = datetime.now().hour
                st.session_state.last_craving_item = st.session_state.current_craving

                st.success("✅ Saved! Great job tracking.")
                st.session_state.show_actions = False
                st.session_state.current_craving = ""
                st.rerun()

    with col2:
        if st.button("↩️ Cancel", use_container_width=True):
            st.session_state.show_actions = False
            st.session_state.current_craving = ""
            st.rerun()

# Dashboard
st.divider()
st.subheader("📊 Your Cravings Journey")

if st.session_state.cravings:
    df = pd.DataFrame(st.session_state.cravings)

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Cravings", len(df))
    with col2:
        if 'did_eat_craved' in df.columns:
            resisted = len(df[df['did_eat_craved'] == False])
            st.metric("Resisted", resisted)
    with col3:
        if 'did_eat_craved' in df.columns:
            gave_in = len(df[df['did_eat_craved'] == True])
            st.metric("Gave In", gave_in)
    with col4:
        if len(df) > 0 and 'did_eat_craved' in df.columns:
            rate = (len(df[df['did_eat_craved'] == False]) / len(df)) * 100
            st.metric("Success Rate", f"{rate:.0f}%")

    # Recent entries with alternatives
    st.subheader("📝 Recent Logs")
    if 'craving_item' in df.columns and 'alternative_chosen' in df.columns:
        show_df = df[['craving_item', 'alternative_chosen', 'created_at']].copy()
        show_df['created_at'] = pd.to_datetime(show_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        show_df.columns = ['Craving', 'Chose Instead', 'Time']
        st.dataframe(show_df.head(10), use_container_width=True, hide_index=True)

    # Alternative effectiveness
    st.subheader("🥇 Top Alternatives")
    if 'alternative_chosen' in df.columns and len(df) > 0:
        alt_counts = df['alternative_chosen'].value_counts().head(5)
        for alt, count in alt_counts.items():
            if alt != "Ate the craved item":
                st.caption(f"• {alt}: {count} times")

    # Weekly pattern
    # Simple Charts - No complexity
    # Simple Charts - No complexity
    # Simple Charts
    # Simple Charts
    st.subheader("📊 Your Insights")

    if st.session_state.cravings and len(st.session_state.cravings) > 0:
        df = pd.DataFrame(st.session_state.cravings)

        if 'created_at' in df.columns:
            # Convert to datetime and extract hour
            df['datetime'] = pd.to_datetime(df['created_at'])
            df['hour'] = df['datetime'].dt.hour

            # Get hours that actually have data
            hours_with_data = sorted(df['hour'].unique())

            col1, col2 = st.columns(2)

            with col1:
                st.caption("⏰ **When cravings hit**")
                # Only show hours with data
                hour_counts = df['hour'].value_counts().sort_index()
                st.bar_chart(hour_counts)

                if not hour_counts.empty:
                    peak = hour_counts.idxmax()
                    st.info(f"🔥 Most cravings: **{peak}:00** ({hour_counts[peak]} times)")

            with col2:
                st.caption("✅ **Success by time**")
                if 'did_eat_craved' in df.columns:
                    # Calculate success rate for hours with data
                    success_data = {}
                    for hour in hours_with_data:
                        hour_data = df[df['hour'] == hour]
                        if len(hour_data) > 0:
                            success = (hour_data['did_eat_craved'] == False).sum() / len(hour_data) * 100
                            success_data[hour] = success

                    # Create dataframe for chart
                    success_df = pd.DataFrame({
                        'hour': list(success_data.keys()),
                        'success': list(success_data.values())
                    }).set_index('hour')

                    st.bar_chart(success_df)

                    # Best time
                    best_hour = max(success_data, key=success_data.get)
                    best_rate = success_data[best_hour]
                    st.success(f"💪 Best time: **{best_hour}:00** ({best_rate:.0f}%)")

            # Overall stats
            st.divider()
            col1, col2, col3 = st.columns(3)

            total = len(df)
            resisted = len(df[df['did_eat_craved'] == False]) if 'did_eat_craved' in df.columns else 0
            gave_in = len(df[df['did_eat_craved'] == True]) if 'did_eat_craved' in df.columns else 0

            with col1:
                st.metric("Total Cravings", total)
            with col2:
                if total > 0:
                    rate = (resisted / total) * 100
                    st.metric("Success Rate", f"{rate:.0f}%")
            with col3:
                st.metric("Times Resisted", resisted)

            # Show your actual data in a table
            with st.expander("📋 View your craving log"):
                if 'craving_item' in df.columns and 'alternative_chosen' in df.columns:
                    view_df = df[['datetime', 'craving_item', 'alternative_chosen']].copy()
                    view_df['datetime'] = view_df['datetime'].dt.strftime('%Y-%m-%d %H:%M')
                    view_df.columns = ['Time', 'Craving', 'Chose']
                    st.dataframe(view_df, use_container_width=True, hide_index=True)
    else:
        st.info("Log your first craving to see insights!")