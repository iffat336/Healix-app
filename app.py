import streamlit as st
import pandas as pd
import datetime
import json
from groq import Groq

# --- Initialize Client ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- App Title ---
st.set_page_config(page_title="Healix - Your Smart Health Companion", page_icon="💪", layout="wide")
st.title("💪 Healix: Your Smart Health & Wellness Companion")

# --- Navigation ---
menu = st.sidebar.selectbox("Navigate", ["🏠 Home", "🥗 Meal Planner", "🏋️ Workout Generator", "📈 Progress Tracker", "💧 Water Reminder", "📜 History"])

# --- Home Section ---
if menu == "🏠 Home":
    st.subheader("Welcome to Healix 👋")
    st.write("""
    Healix helps you build a healthy lifestyle by combining AI and data-driven insights.
    
    **Features:**
    - 🥗 Personalized Meal Planning  
    - 🏋️ AI Workout Recommendations  
    - 💧 Smart Water Intake Reminders  
    - 📈 Progress Tracking  
    - 📜 Save & View Your Health History  
    """)

# --- Meal Planner ---
elif menu == "🥗 Meal Planner":
    st.header("🥗 Personalized Meal Planner")
    goal = st.selectbox("Select your goal", ["Lose Weight", "Gain Muscle", "Stay Fit"])
    dietary = st.selectbox("Any dietary preference?", ["No Preference", "Vegetarian", "Vegan", "Keto", "Low Carb"])
    calories = st.number_input("Daily calorie target", min_value=1200, max_value=4000, value=2000)

    if st.button("Generate My Meal Plan"):
        meal_prompt = f"Create a {goal} meal plan for a {dietary} person with {calories} calories per day. Include breakfast, lunch, dinner, and snacks."
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": meal_prompt}]
            )
            plan = response.choices[0].message.content
            st.success(plan)

            # Save history
            history = {"date": str(datetime.date.today()), "type": "Meal Plan", "details": plan}
            with open("history.json", "a") as f:
                f.write(json.dumps(history) + "\n")
        except Exception as e:
            st.error(f"Error generating meal plan: {e}")

# --- Workout Generator ---
elif menu == "🏋️ Workout Generator":
    st.header("🏋️ AI Workout Generator")
    level = st.selectbox("Your fitness level", ["Beginner", "Intermediate", "Advanced"])
    goal = st.selectbox("Goal", ["Fat Loss", "Muscle Gain", "Flexibility", "Endurance"])
    duration = st.slider("Workout duration (minutes)", 10, 90, 30)

    if st.button("Generate My Workout"):
        workout_prompt = f"Generate a {duration}-minute {level} workout plan focused on {goal}. Include warm-up, main sets, and cool-down."
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": workout_prompt}]
            )
            workout = response.choices[0].message.content
            st.success(workout)

            # Save history
            history = {"date": str(datetime.date.today()), "type": "Workout", "details": workout}
            with open("history.json", "a") as f:
                f.write(json.dumps(history) + "\n")
        except Exception as e:
            st.error(f"Error generating workout: {e}")

# --- Progress Tracker ---
elif menu == "📈 Progress Tracker":
    st.header("📈 Track Your Progress")
    uploaded = st.file_uploader("Upload your progress CSV (Week, Weight, Calories)", type="csv")

    if uploaded:
        df = pd.read_csv(uploaded)
        st.write("Your Progress Data:")
        st.dataframe(df)
        st.line_chart(df.set_index(df.columns[0]))

# --- Water Intake Reminder ---
elif menu == "💧 Water Reminder":
    st.header("💧 Stay Hydrated!")
    weight = st.number_input("Enter your weight (kg):", min_value=30, max_value=200, value=60)
    water_intake = round(weight * 35 / 1000, 2)
    st.success(f"You should drink approximately {water_intake} liters of water per day 💦")

    st.info("💡 Tip: Drink a glass of water every 2 hours to maintain hydration.")

# --- History Section ---
elif menu == "📜 History":
    st.header("📜 Your Saved History")
    try:
        with open("history.json", "r") as f:
            data = [json.loads(line) for line in f]
            df = pd.DataFrame(data)
            st.dataframe(df)
    except FileNotFoundError:
        st.warning("No history found yet. Generate your first plan to start tracking!")
