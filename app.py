import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sqlite3
import openai  # or your existing LLM client

# --- DATABASE SETUP ---
conn = sqlite3.connect("healix_users.db", check_same_thread=False)
c = conn.cursor()

# Users table
c.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    date_joined TEXT
)
""")

# Activity/history table
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

# --- FUNCTIONS ---
def signup(username, password):
    try:
        c.execute("INSERT INTO users (username, password, date_joined) VALUES (?, ?, ?)",
                  (username, password, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        st.success("Account created! Please login.")
    except sqlite3.IntegrityError:
        st.error("Username already exists.")

def login(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return c.fetchone()

def save_activity(username, type_, content):
    c.execute("INSERT INTO history (username, type, content, timestamp) VALUES (?, ?, ?, ?)",
              (username, type_, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

# --- SIDEBAR LOGIN/SIGNUP ---
st.sidebar.title("User Access")
choice = st.sidebar.selectbox("Login / Signup", ["Login", "Signup"])

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if choice == "Signup":
    st.sidebar.subheader("Create Account")
    new_user = st.sidebar.text_input("Username")
    new_pass = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Sign Up"):
        if new_user and new_pass:
            signup(new_user, new_pass)
        else:
            st.sidebar.warning("Enter both username and password.")

elif choice == "Login":
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        user = login(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Logged in as {username}")
        else:
            st.error("Incorrect username or password")

# --- MAIN APP ---
st.title("🤖 Healix AI Health Companion")

# Menu
menu = st.sidebar.selectbox("Menu", ["🏠 Home", "🥗 Meal Plan", "💪 Workout Generator",
                                     "💧 Water Tracker", "📈 Progress Tracker", "👤 Profile"])

# --- PROFILE & HISTORY ---
if st.session_state.logged_in and menu == "👤 Profile":
    st.header(f"👤 Profile: {st.session_state.username}")

    # User info
    c.execute("SELECT date_joined FROM users WHERE username=?", (st.session_state.username,))
    join_date = c.fetchone()[0]
    st.write(f"Member since: {join_date}")

    # Activity history
    st.subheader("📝 Activity History")
    c.execute("SELECT type, content, timestamp FROM history WHERE username=? ORDER BY timestamp DESC",
              (st.session_state.username,))
    history_data = c.fetchall()
    if history_data:
        df_history = pd.DataFrame(history_data, columns=["Type", "Content", "Timestamp"])
        st.dataframe(df_history)
    else:
        st.write("No history yet.")

    # Manual activity add (optional)
    st.subheader("Add Activity")
    activity_type = st.selectbox("Type", ["Meal Plan", "Workout", "Water Intake"])
    activity_content = st.text_area("Content")
    if st.button("Save Activity"):
        if activity_content.strip():
            save_activity(st.session_state.username, activity_type, activity_content)
            st.success("Activity saved!")
        else:
            st.warning("Enter some content to save.")

# --- HOME ---
if menu == "🏠 Home":
    st.write("Welcome to Healix! Use the sidebar to navigate your health companion features.")

# --- MEAL PLAN GENERATOR ---
elif menu == "🥗 Meal Plan" and st.session_state.logged_in:
    st.header("🥗 Personalized Meal Plan")
    user_goal = st.selectbox("Select your goal", ["Weight Loss", "Muscle Gain", "Maintenance"])
    if st.button("Generate Meal Plan"):
        meal_prompt = f"Generate a detailed meal plan for {user_goal}."
        try:
            # Replace with your LLM client
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": meal_prompt}]
            )
            meal_text = response.choices[0].message.content
            st.success(meal_text)
            save_activity(st.session_state.username, "Meal Plan", meal_text)
        except Exception as e:
            st.error(f"Error generating meal plan: {e}")

# --- WORKOUT GENERATOR ---
elif menu == "💪 Workout Generator" and st.session_state.logged_in:
    st.header("💪 Personalized Workout Plan")
    workout_goal = st.selectbox("Select your goal", ["Strength", "Cardio", "Flexibility"])
    if st.button("Generate Workout"):
        workout_prompt = f"Generate a workout routine for {workout_goal}."
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": workout_prompt}]
            )
            workout_text = response.choices[0].message.content
            st.success(workout_text)
            save_activity(st.session_state.username, "Workout", workout_text)
        except Exception as e:
            st.error(f"Error generating workout: {e}")

# --- WATER TRACKER ---
elif menu == "💧 Water Tracker" and st.session_state.logged_in:
    st.header("💧 Water Intake Tracker")
    water = st.number_input("Enter glasses of water drank today", min_value=0, step=1)
    if st.button("Save Water Intake"):
        save_activity(st.session_state.username, "Water Intake", f"{water} glasses")
        st.success("Water intake saved!")

# --- PROGRESS TRACKER ---
elif menu == "📈 Progress Tracker" and st.session_state.logged_in:
    st.header("📈 Track Your Progress")
    uploaded = st.file_uploader("Upload your progress CSV (Week, Weight, Calories)", type="csv")
    if uploaded is not None:
        df_progress = pd.read_csv(uploaded)
        st.dataframe(df_progress)
        st.line_chart(df_progress.set_index("Week"))
