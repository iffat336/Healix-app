import streamlit as st
from groq import Groq
import pandas as pd

# --- App Configuration ---
st.set_page_config(page_title="Healix | AI Health Assistant", page_icon="🧠", layout="wide")

# --- Initialize session state for history ---
if "meal_history" not in st.session_state:
    st.session_state.meal_history = []
if "workout_history" not in st.session_state:
    st.session_state.workout_history = []

# --- Title ---
st.title("🧠 Healix – Your AI Health & Wellness Assistant")
st.markdown("### Get personalized meal plans, workouts (with videos 🎥), and track your progress!")

# --- Sidebar Menu ---
menu = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "🥗 Meal Plan", "🏋️ Workout Plan", "📈 Progress Tracker", "🕒 History"]
)

# --- Initialize Groq API Client ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", None)
if not GROQ_API_KEY:
    st.warning("⚠️ Please add your GROQ_API_KEY in Streamlit Secrets.")
else:
    client = Groq(api_key=GROQ_API_KEY)

# --- HOME ---
if menu == "🏠 Home":
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966486.png", width=120)
    st.markdown("""
    Welcome to **Healix**, your AI-powered fitness and nutrition guide.  
    Choose an option from the sidebar to get started:
    - 🥗 **Meal Plan:** Generate a personalized diet plan  
    - 🏋️ **Workout Plan:** AI workouts + animated video demos  
    - 📈 **Progress Tracker:** Visualize your improvements  
    - 🕒 **History:** Review your previous plans
    """)

# --- MEAL PLAN SECTION ---
elif menu == "🥗 Meal Plan":
    st.header("🥗 Personalized Meal Plan")
    weight = st.number_input("Enter your weight (kg):", min_value=30, max_value=200, step=1)
    goal = st.selectbox("Select your goal:", ["Lose Weight", "Maintain Weight", "Gain Muscle"])
    activity = st.selectbox("Select activity level:", ["Low", "Moderate", "High"])

    if st.button("Generate My Meal Plan 🍱"):
        meal_prompt = (
            f"Create a 3-day healthy meal plan for someone weighing {weight}kg "
            f"with a goal to {goal.lower()} and {activity.lower()} activity level. "
            "Include breakfast, lunch, dinner, and snacks with calories."
        )

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": meal_prompt}]
            )
            meal_plan = response.choices[0].message.content
            st.success(meal_plan)

            # Save to history
            st.session_state.meal_history.append({"weight": weight, "goal": goal, "activity": activity, "plan": meal_plan})
        except Exception as e:
            st.error(f"⚠️ Error generating meal plan: {e}")

# --- WORKOUT PLAN SECTION ---
elif menu == "🏋️ Workout Plan":
    st.header("🏋️ Personalized Workout Plan")
    fitness_level = st.selectbox("Select your fitness level:", ["Beginner", "Intermediate", "Advanced"])
    duration = st.slider("Workout duration (minutes):", 10, 90, 30)

    # Example animated workout videos (YouTube embeds)
    workout_videos = {
        "Push-Ups": "https://www.youtube.com/embed/IODxDxX7oi4",
        "Squats": "https://www.youtube.com/embed/aclHkVaku9U",
        "Plank": "https://www.youtube.com/embed/pSHjTRCQxIw",
        "Lunges": "https://www.youtube.com/embed/QOVaHwm-Q6U",
        "Burpees": "https://www.youtube.com/embed/TU8QYVW0gDU"
    }

    if st.button("Generate My Workout 💪"):
        workout_prompt = (
            f"Create a {duration}-minute {fitness_level.lower()} workout plan "
            "including warm-up, main exercises, and cool-down."
        )

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": workout_prompt}]
            )
            workout_plan = response.choices[0].message.content
            st.success(workout_plan)

            # Display exercise videos dynamically
            st.markdown("### 🎥 Example Workout Videos:")
            cols = st.columns(2)
            for i, (exercise, url) in enumerate(workout_videos.items()):
                with cols[i % 2]:
                    st.markdown(f"**{exercise}**")
                    st.video(url)

            # Save to history
            st.session_state.workout_history.append({"level": fitness_level, "duration": duration, "plan": workout_plan})
        except Exception as e:
            st.error(f"⚠️ Error generating workout: {e}")

# --- PROGRESS TRACKER SECTION ---
elif menu == "📈 Progress Tracker":
    st.header("📈 Track Your Progress")
    uploaded = st.file_uploader("Upload your progress CSV (Week, Weight, Calories)", type="csv")

    if uploaded:
        df = pd.read_csv(uploaded)
        st.dataframe(df)
        st.line_chart(df.set_index(df.columns[0]))
        st.success("✅ Progress chart generated successfully!")
    else:
        st.info("Upload a CSV file to visualize your progress.")

# --- HISTORY SECTION ---
elif menu == "🕒 History":
    st.header("🕒 Your Saved History")

    if not st.session_state.meal_history and not st.session_state.workout_history:
        st.info("No history yet. Generate a meal or workout plan first.")
    else:
        if st.session_state.meal_history:
            st.subheader("🥗 Meal Plan History")
            for i, record in enumerate(st.session_state.meal_history[::-1]):
                with st.expander(f"Meal Plan #{len(st.session_state.meal_history)-i} — {record['goal']} ({record['activity']})"):
                    st.write(record["plan"])

        if st.session_state.workout_history:
            st.subheader("🏋️ Workout History")
            for i, record in enumerate(st.session_state.workout_history[::-1]):
                with st.expander(f"Workout #{len(st.session_state.workout_history)-i} — {record['level']} ({record['duration']} mins)"):
                    st.write(record["plan"])
