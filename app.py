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
# --- Workout Generator ---
elif menu == "🏋️ Workout Generator":
    st.header("🏋️ Personalized Workout Plan")

    goal = st.selectbox("Select your fitness goal", [
        "Weight Loss", "Muscle Gain", "Flexibility", "Endurance", "Women Wellness", "Yoga & Mindfulness"
    ])
    duration = st.slider("Workout duration (minutes)", 10, 90, 30)

    if st.button("Generate My Workout Plan"):
        workout_prompt = f"Generate a {duration}-minute workout plan for {goal}. Include warm-up, main exercises, and cool down."

        with st.spinner("Creating your personalized plan..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": workout_prompt}]
            )

        try:
            plan = response.choices[0].message.content
            st.success(plan)

            # --- Workout Videos Section ---
            st.subheader("🎥 Follow Along with Exercise Videos")

            # General workout video library
            videos = {
                "Weight Loss": [
                    ("Jumping Jacks", "https://media.giphy.com/media/xT0GqnYyuw8hnVfCA4/giphy.mp4"),
                    ("Burpees", "https://media.giphy.com/media/3o7TKz5d9bLrj3aYus/giphy.mp4"),
                    ("Mountain Climbers", "https://media.giphy.com/media/3o7TKtnuHOHHUjR38Y/giphy.mp4"),
                ],
                "Muscle Gain": [
                    ("Push-ups", "https://media.giphy.com/media/l3vR3z8j2T8zGmYdC/giphy.mp4"),
                    ("Squats", "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.mp4"),
                    ("Lunges", "https://media.giphy.com/media/3o7TKtnuHOHHUjR38Y/giphy.mp4"),
                ],
                "Flexibility": [
                    ("Side Stretch", "https://media.giphy.com/media/l2Sq3XKef4nFasFz2/giphy.mp4"),
                    ("Neck Rotation", "https://media.giphy.com/media/l0HlA0h2Zb0h6tBtC/giphy.mp4"),
                    ("Torso Twist", "https://media.giphy.com/media/l0MYC0LajbaPoEADu/giphy.mp4"),
                ],
                "Endurance": [
                    ("Running in Place", "https://media.giphy.com/media/xT0xeJpnrWC4XWblEk/giphy.mp4"),
                    ("Skipping Rope", "https://media.giphy.com/media/l2JhJz0v6t9J7hbQ4/giphy.mp4"),
                    ("High Knees", "https://media.giphy.com/media/26gsspf0C6H7oO0cE/giphy.mp4"),
                ],
                "Women Wellness": [
                    ("Pelvic Tilt", "https://media.giphy.com/media/3ohs7Hf7q6P6z2lWwQ/giphy.mp4"),
                    ("Glute Bridge", "https://media.giphy.com/media/l0MYsG6zF9XG5vR7q/giphy.mp4"),
                    ("Cat-Cow Stretch", "https://media.giphy.com/media/26vIfnLrCqGgV8WbO/giphy.mp4"),
                ],
                "Yoga & Mindfulness": [
                    ("Sun Salutation", "https://media.giphy.com/media/3ohhwF34cGDoFFhRfy/giphy.mp4"),
                    ("Child’s Pose", "https://media.giphy.com/media/l2SqbHjY3VQdAqYzW/giphy.mp4"),
                    ("Tree Pose", "https://media.giphy.com/media/3ov9jNziFTMfzSumAw/giphy.mp4"),
                ]
            }

            # Show relevant category videos
            if goal in videos:
                for exercise, video_url in videos[goal]:
                    st.markdown(f"**{exercise}**")
                    st.video(video_url)
            else:
                st.info("Select a goal to see exercise videos!")

        except Exception as e:
            st.error(f"Error: {e}")
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

