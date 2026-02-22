import streamlit as st
import pandas as pd

st.title("Cravings Logger")

# Step 1: Ask if craving
val = st.text_input("Are you having a craving? (yes/no)")

if val.lower() == "yes":

    st.subheader("When was your last meal?")

    col1, col2, col3, col4 = st.columns(4)

    #button inside column 1.
    #Streamlit reruns the entire script every time you click something.
    #So if you don’t store the value somewhere, it disappears.

    if col1.button("30 minutes ago"):
        st.session_state["meal_time"] = "30 minutes ago" #This stores the value in memory for that user session.

    if col2.button("1 hour ago"):
        st.session_state["meal_time"] = "1 hour ago"

    if col3.button("2 hours ago"):
        st.session_state["meal_time"] = "2 hours ago"

    if col4.button("4 hours ago"):
        st.session_state["meal_time"] = "4 hours ago"

    if "meal_time" in st.session_state:
        st.write("Last meal:", st.session_state["meal_time"])

        food = st.text_input("What did you eat?")

        if food:

            food_type = st.radio(
                "what did you have?",
                ["Sweet", "Meal"]
            )

        # craving_type = st.radio(
        #     "What are you craving?",
        #     ["Sweet", "Meal"]
        # )

            if food_type == "Sweet":
                type = st.radio(
                    "Which type of sweet?",
                    ["Indian sweet (e.g., rasgulla)",
                 "Bakery item (e.g., croissant)",
                 "Chocolate",
                 "Ice cream"]
                )

                st.success(f"You are craving: {type}")

            elif food_type == "Meal":
                type = st.radio(
                    "What meal?",
                    ["thali",
                    "snacks",
                    "vada paav"
                    ]
                )
                st.success(f"You are craving: {type}")

        craving_type = st.radio(
            "what are you craving now?",
            ["Sweet", "Meal"]
        )


        if craving_type == "Sweet":
            type = st.radio(
            "Which type of sweet?",
            ["Indian sweet (e.g., rasgulla)",
             "Bakery item (e.g., croissant)",
             "Chocolate",
             "Ice cream"]
            )
            st.success(f"You are craving: {type}")

        elif food_type == "Meal":
            type = st.radio(
                "What meal?",
                ["thali",
                 "snacks",
                 "vada paav"
                 ]
            )
            st.success(f"You are craving: {type}")

