# app.py
import streamlit as st
from groq import Groq
import pandas as pd
import io
import time
import json

# -------------------------
# App config
# -------------------------
st.set_page_config(page_title="Healix | AI Health Assistant", page_icon="🧠", layout="wide")

# -------------------------
# Helpers
# -------------------------
def get_response_text(response):
    """
    Safely extract text from response from different SDK shapes.
    Try multiple common patterns.
    """
    try:
        # Groq-style object with .choices[0].message.content
        return response.choices[0].message.content
    except Exception:
        pass
    try:
        # OpenAI older dict-style
        return response['choices'][0]['message']['content']
    except Exception:
        pass
    try:
        # Some completions use .choices[0].text
        return response.choices[0].text
    except Exception:
        pass
    try:
        return response['choices'][0]['text']
    except Exception:
        pass
    # last resort: stringified response
    try:
        return str(response)
    except Exception:
        return "No readable content in response."

def save_history_to_csv():
    """
    Save session history to a CSV in working directory and return bytes for download.
    """
    combined = []
    for m in st.session_state.meal_history:
        combined.append({
            "type": "meal",
            "time": m.get("time"),
            "meta": json.dumps({"weight": m.get("weight"), "goal": m.get("goal"), "activity": m.get("activity")}),
            "content": m.get("plan")
        })
    for w in st.session_state.workout_history:
        combined.append({
            "type": "workout",
            "time": w.get("time"),
            "meta": json.dumps({"level": w.get("level"), "duration": w.get("duration")}),
            "content": w.get("plan")
        })
    if not combined:
        return None
    df = pd.DataFrame(combined)
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    # Also write local file (may not persist across Streamlit restarts)
    with open("healix_history.csv", "wb") as f:
        f.write(csv_bytes)
    return csv_bytes

# -------------------------
# Initialize secrets & client
# -------------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", None)
client = None
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        st.warning("Groq client initialization failed: " + str(e))
else:
    st.warning("Please add GROQ_API_KEY in Streamlit Secrets for AI features to work.")

# -------------------------
# Session state (history + water)
# -------------------------
if "meal_history" not in st.session_state:
    st.session_state.meal_history = []
if "workout_history" not in st.session_state:
    st.session_state.workout_history = []
if "water_reminder_on" not in st.session_state:
    st.session_state.water_reminder_on = False
if "water_interval_min" not in st.session_state:
    st.session_state.water_interval_min = 60  # default 60 minutes

# -------------------------
# UI - Header + Sidebar
# -------------------------
st.title("🧠 Healix — AI Health & Wellness Assistant")
st.markdown("Generate meal plans, workouts with tutorial videos, save history, and get water reminders.")

menu = st.sidebar.radio("Navigation", ["Home", "Meal Plan", "Workout", "Progress Tracker", "History", "Water Reminder", "Settings"])

st.sidebar.markdown("---")
st.sidebar.markdown("Built with Streamlit · Groq Llama · Pandas")

# -------------------------
# HOME
# -------------------------
if menu == "Home":
    st.header("Welcome to Healix")
    st.markdown("""
    **Healix** helps you generate personalized meal and workout plans using an LLM,
    shows quick exercise videos, saves your plans to history, and can remind you to drink water.
    """)
    st.markdown("Use the sidebar to choose a feature.")

# -------------------------
# MEAL PLAN
# -------------------------
elif menu == "Meal Plan":
    st.header("🥗 Personalized Meal Plan")
    col1, col2, col3 = st.columns(3)
    with col1:
        weight = st.number_input("Weight (kg)", min_value=30, max_value=200, value=65)
    with col2:
        goal = st.selectbox("Goal", ["Lose Weight", "Maintain Weight", "Gain Muscle"])
    with col3:
        activity = st.selectbox("Activity Level", ["Low", "Moderate", "High"])

    if st.button("Generate Meal Plan"):
        if not client:
            st.error("AI client not configured. Add GROQ_API_KEY in Streamlit Secrets.")
        else:
            meal_prompt = (
                f"Create a 3-day healthy meal plan for someone weighing {weight} kg, "
                f"whose goal is to {goal.lower()}, with {activity.lower()} activity. "
                "Include meals and approximate calories."
            )
            with st.spinner("Generating meal plan..."):
                try:
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": meal_prompt}]
                    )
                except Exception as e:
                    st.error("API call failed: " + str(e))
                    response = None

            if response:
                text = get_response_text(response)
                st.success("Meal plan generated:")
                st.write(text)

                # Save to history (with timestamp)
                record = {
                    "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "weight": weight,
                    "goal": goal,
                    "activity": activity,
                    "plan": text
                }
                st.session_state.meal_history.append(record)

# -------------------------
# WORKOUT
# -------------------------
elif menu == "Workout":
    st.header("🏋️ Workout Generator + Videos")
    fitness_level = st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"])
    duration = st.slider("Duration (minutes)", 10, 90, 30)
    goal_choice = st.selectbox("Workout Category", ["General", "Weight Loss", "Muscle Gain", "Flexibility", "Endurance", "Women Wellness", "Yoga & Mindfulness"])

    if st.button("Generate Workout"):
        if not client:
            st.error("AI client not configured. Add GROQ_API_KEY in Streamlit Secrets.")
        else:
            workout_prompt = (
                f"Create a {duration}-minute {fitness_level.lower()} workout plan for {goal_choice}. "
                "Include warm-up, main exercises, reps/duration, and cool-down."
            )
            with st.spinner("Generating workout..."):
                try:
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": workout_prompt}]
                    )
                except Exception as e:
                    st.error("API call failed: " + str(e))
                    response = None

            if response:
                text = get_response_text(response)
                st.success("Workout plan generated:")
                st.write(text)

                # Save workout to history
                wrec = {
                    "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "level": fitness_level,
                    "duration": duration,
                    "plan": text
                }
                st.session_state.workout_history.append(wrec)

                # --- Videos mapping (demo sample MP4s or YouTube embeds) ---
                st.subheader("🎥 Exercise Videos (follow along)")
                # Example reliable short MP4 URLs (demo). Replace with your own hosted videos if available.
                videos_library = {
                    "General": [
                        ("Jumping Jacks", "https://samplelib.com/lib/preview/mp4/sample-5s.mp4"),
                        ("Bodyweight Squats", "https://samplelib.com/lib/preview/mp4/sample-10s.mp4")
                    ],
                    "Weight Loss": [
                        ("Burpees", "https://samplelib.com/lib/preview/mp4/sample-15s.mp4"),
                        ("Mountain Climbers", "https://samplelib.com/lib/preview/mp4/sample-10s.mp4")
                    ],
                    "Muscle Gain": [
                        ("Push-ups", "https://samplelib.com/lib/preview/mp4/sample-10s.mp4"),
                        ("Lunges", "https://samplelib.com/lib/preview/mp4/sample-15s.mp4")
                    ],
                    "Flexibility": [
                        ("Side Stretch", "https://samplelib.com/lib/preview/mp4/sample-5s.mp4"),
                        ("Torso Twist", "https://samplelib.com/lib/preview/mp4/sample-10s.mp4")
                    ],
                    "Endurance": [
                        ("High Knees", "https://samplelib.com/lib/preview/mp4/sample-15s.mp4"),
                        ("Skipping", "https://samplelib.com/lib/preview/mp4/sample-10s.mp4")
                    ],
                    "Women Wellness": [
                        ("Glute Bridge", "https://samplelib.com/lib/preview/mp4/sample-10s.mp4"),
                        ("Cat-Cow Stretch", "https://samplelib.com/lib/preview/mp4/sample-15s.mp4")
                    ],
                    "Yoga & Mindfulness": [
                        ("Sun Salutation", "https://samplelib.com/lib/preview/mp4/sample-10s.mp4"),
                        ("Child Pose", "https://samplelib.com/lib/preview/mp4/sample-5s.mp4")
                    ]
                }

                if goal_choice in videos_library:
                    for ex_name, video_url in videos_library[goal_choice]:
                        st.markdown(f"**{ex_name}**")
                        st.video(video_url)
                else:
                    st.info("No videos available for this category.")

# -------------------------
# Progress Tracker
# -------------------------
elif menu == "Progress Tracker":
    st.header("📈 Progress Tracker")
    uploaded = st.file_uploader("Upload progress CSV (Week,Weight,Calories,...)", type="csv")
    if uploaded:
        try:
            df = pd.read_csv(uploaded)
            st.dataframe(df)
            # use first column as x-axis if possible
            idx_col = df.columns[0]
            st.line_chart(df.set_index(idx_col))
        except Exception as e:
            st.error("Failed to read CSV: " + str(e))
    else:
        st.info("Upload a CSV file to visualize progress.")

# -------------------------
# History
# -------------------------
elif menu == "History":
    st.header("🕒 Saved History")
    if not st.session_state.meal_history and not st.session_state.workout_history:
        st.info("No saved history yet. Generate a meal or workout to save it.")
    else:
        if st.session_state.meal_history:
            st.subheader("🥗 Meal History")
            for i, rec in enumerate(reversed(st.session_state.meal_history), 1):
                with st.expander(f"Meal #{i} — {rec['time']} — {rec['goal']}"):
                    st.write(rec["plan"])
                    st.markdown(f"**Weight:** {rec['weight']} kg — **Activity:** {rec['activity']}")

        if st.session_state.workout_history:
            st.subheader("🏋️ Workout History")
            for i, rec in enumerate(reversed(st.session_state.workout_history), 1):
                with st.expander(f"Workout #{i} — {rec['time']} — {rec['level']}"):
                    st.write(rec["plan"])
                    st.markdown(f"**Duration:** {rec['duration']} mins")

        # Download CSV
        csv_bytes = save_history_to_csv()
        if csv_bytes:
            st.download_button(label="Download history CSV", data=csv_bytes, file_name="healix_history.csv", mime="text/csv")

# -------------------------
# Water Reminder
# -------------------------
elif menu == "Water Reminder":
    st.header("💧 Water Intake Reminder")
    st.markdown("Set a browser notification reminder to drink water at a chosen interval. Streamlit will ask for permission to show notifications in your browser.")

    interval = st.number_input("Reminder interval (minutes)", min_value=15, max_value=240, value=st.session_state.water_interval_min)
    st.session_state.water_interval_min = interval

    if st.button("Start Water Reminders"):
        st.session_state.water_reminder_on = True
        st.success(f"Water reminder started: every {interval} minutes (browser notifications).")
    if st.button("Stop Water Reminders"):
        st.session_state.water_reminder_on = False
        st.info("Water reminders stopped.")

    # Client-side JS for browser notifications (runs in the page)
    if st.session_state.water_reminder_on:
        js = f"""
        <script>
        // request permission
        if (Notification.permission !== "granted") {{
            Notification.requestPermission();
        }}
        // clear old interval
        if (window.healixWaterInterval) {{
            clearInterval(window.healixWaterInterval);
        }}
        const minutes = {interval};
        function showReminder() {{
            if (Notification.permission === "granted") {{
                new Notification("Healix — Time to drink water 💧", {{
                    body: "Stay hydrated — drink a glass of water now!",
                    icon: "https://cdn-icons-png.flaticon.com/512/727/727845.png"
                }});
            }} else {{
                console.log("Notification permission not granted.");
            }}
        }}
        // show first reminder after 'minutes'
        window.healixWaterInterval = setInterval(showReminder, minutes * 60 * 1000);
        // optional immediate reminder once started
        showReminder();
        </script>
        """
        st.components.v1.html(js, height=0, scrolling=False)

# -------------------------
# Settings
# -------------------------
elif menu == "Settings":
    st.header("⚙️ Settings & About")
    st.markdown("API and deployment settings.")
    if GROQ_API_KEY:
        st.success("GROQ API key configured.")
    else:
        st.warning("No GROQ API key found. Add it in Streamlit Secrets as `GROQ_API_KEY`.")

    st.markdown("**Developer:** Iffat Nazir — Healix project")
    st.markdown("If you want persistent history across app restarts, I can add cloud storage options (Google Drive / Firebase / simple GitHub file commits).")

# -------------------------
# End
# -------------------------
