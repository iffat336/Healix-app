# app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sqlite3
import hashlib
import openai

st.set_page_config(page_title="Healix AI", layout="wide")

# --- CONFIG: OpenAI key from Streamlit secrets ---
# Add in Streamlit Cloud: Settings → Secrets
# OPENAI_API_KEY="sk-..."
openai.api_key = st.secrets.get("OPENAI_API_KEY", None)

# --- DATABASE SETUP (demo-friendly) ---
# NOTE: SQLite on Streamlit Cloud is ephemeral and not recommended for production.
# For production use: Supabase/Postgres/Firestore/etc.
@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect("healix_users.db", check_same_thread=False)
    c = conn.cursor()
    # users table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        date_joined TEXT
    )
    """)
    # history table
    c.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        type TEXT,
        content TEXT,
        timestamp TEXT
    )
    """)
    conn.commit()
    return conn

conn = get_db_connection()
c = conn.cursor()

# --- UTILITIES ---
def hash_password(password: str) -> str:
    # Demo-only hashing. For production use bcrypt (salt + work factor).
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def signup(username, password):
    try:
        pwd_hash = hash_password(password)
        c.execute("INSERT INTO users (username, password_hash, date_joined) VALUES (?, ?, ?)",
                  (username, pwd_hash, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        st.success("Account created! Please login.")
    except sqlite3.IntegrityError:
        st.error("Username already exists.")

def login(username, password):
    pwd_hash = hash_password(password)
    c.execute("SELECT * FROM users WHERE username=? AND password_hash=?", (username, pwd_hash))
    return c.fetchone()

def save_activity(username, type_, content):
    c.execute("INSERT INTO history (username, type, content, timestamp) VALUES (?, ?, ?, ?)",
              (username, type_, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

# --- SESSION STATE DEFAULTS ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- SIDEBAR: LOGIN / SIGNUP ---
st.sidebar.title("User Access")
choice = st.sidebar.selectbox("Login / Signup", ["Login", "Signup"])

if choice == "Signup":
    st.sidebar.subheader("Create Account")
    new_user = st.sidebar.text_input("Username", key="su_user")
    new_pass = st.sidebar.text_input("Password", type="password", key="su_pass")
    if st.sidebar.button("Sign Up"):
        if new_user and new_pass:
            signup(new_user.strip(), new_pass)
        else:
            st.sidebar.warning("Enter both username and password.")
elif choice == "Login":
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Username", key="li_user")
    password = st.sidebar.text_input("Password", type="password", key="li_pass")
    if st.sidebar.button("Login"):
        user = login(username.strip(), password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = username.strip()
            st.success(f"Logged in as {st.session_state.username}")
        else:
            st.error("Incorrect username or password")

# --- APP LAYOUT ---
st.title("🤖 Healix AI Health Companion")

# Menu - disable protected features if not logged in
menu = st.sidebar.selectbox("Menu", ["🏠 Home", "🥗 Meal Plan", "💪 Workout Generator",
                                     "💧 Water Tracker", "📈 Progress Tracker", "👤 Profile"])

# --- PROFILE & HISTORY ---
if st.session_state.logged_in and menu == "👤 Profile":
    st.header(f"👤 Profile: {st.session_state.username}")
    c.execute("SELECT date_joined FROM users WHERE username=?", (st.session_state.username,))
    res = c.fetchone()
    join_date = res[0] if res else "Unknown"
    st.write(f"Member since: {join_date}")

    st.subheader("📝 Activity History")
    c.execute("SELECT type, content, timestamp FROM history WHERE username=? ORDER BY timestamp DESC",
              (st.session_state.username,))
    history_data = c.fetchall()
    if history_data:
        df_history = pd.DataFrame(history_data, columns=["Type", "Content", "Timestamp"])
        st.dataframe(df_history)
    else:
        st.write("No history yet.")

    st.subheader("Add Activity")
    activity_type = st.selectbox("Type", ["Meal Plan", "Workout", "Water Intake"])
    activity_content = st.text_area("Content")
    if st.button("Save Activity"):
        if activity_content.strip():
            save_activity(st.session_state.username, activity_type, activity_content.strip())
            st.success("Activity saved!")
        else:
            st.warning("Enter some content to save.")

# --- HOME ---
if menu == "🏠 Home":
    st.write("Welcome to Healix! Use the sidebar to navigate your health companion features.")

# --- MEAL PLAN GENERATOR ---
elif menu == "🥗 Meal Plan":
    if not st.session_state.logged_in:
        st.warning("Please log in to generate a meal plan.")
    else:
        st.header("🥗 Personalized Meal Plan")
        user_goal = st.selectbox("Select your goal", ["Weight Loss", "Muscle Gain", "Maintenance"])
        if st.button("Generate Meal Plan"):
            meal_prompt = f"Generate a detailed meal plan for {user_goal}."
            if not openai.api_key:
                st.error("OpenAI API key not configured. Add OPENAI_API_KEY to Streamlit secrets.")
            else:
                try:
                    with st.spinner("Generating..."):
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": meal_prompt}],
                            max_tokens=600,
                        )
                        meal_text = response.choices[0].message.content
                    st.markdown(meal_text)
                    save_activity(st.session_state.username, "Meal Plan", meal_text)
                except Exception as e:
                    st.error(f"Error generating meal plan: {e}")

# --- WORKOUT GENERATOR ---
elif menu == "💪 Workout Generator":
    if not st.session_state.logged_in:
        st.warning("Please log in to generate a workout.")
    else:
        st.header("💪 Personalized Workout Plan")
        workout_goal = st.selectbox("Select your goal", ["Strength", "Cardio", "Flexibility"])
        if st.button("Generate Workout"):
            workout_prompt = f"Generate a workout routine for {workout_goal}."
            if not openai.api_key:
                st.error("OpenAI API key not configured. Add OPENAI_API_KEY to Streamlit secrets.")
            else:
                try:
                    with st.spinner("Generating..."):
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": workout_prompt}],
                            max_tokens=600,
                        )
                        workout_text = response.choices[0].message.content
                    st.markdown(workout_text)
                    save_activity(st.session_state.username, "Workout", workout_text)
                except Exception as e:
                    st.error(f"Error generating workout: {e}")

# --- WATER TRACKER ---
elif menu == "💧 Water Tracker":
    if not st.session_state.logged_in:
        st.warning("Please log in to save water intake.")
    else:
        st.header("💧 Water Intake Tracker")
        water = st.number_input("Enter glasses of water drank today", min_value=0, step=1)
        if st.button("Save Water Intake"):
            save_activity(st.session_state.username, "Water Intake", f"{water} glasses")
            st.success("Water intake saved!")

# --- PROGRESS TRACKER ---
elif menu == "📈 Progress Tracker":
    if not st.session_state.logged_in:
        st.warning("Please log in to upload progress data.")
    else:
        st.header("📈 Track Your Progress")
        uploaded = st.file_uploader("Upload your progress CSV (Week, Weight, Calories)", type="csv")
        if uploaded is not None:
            df_progress = pd.read_csv(uploaded)
            st.dataframe(df_progress)
            # Attempt to set Week as index if it exists
            if "Week" in df_progress.columns:
                st.line_chart(df_progress.set_index("Week"))
            else:
                st.line_chart(df_progress)
