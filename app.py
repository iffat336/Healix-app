# Healix v1.1 – AI Health & Fitness Assistant
# Developed by: Usama Bajwa & Iffat Nazir
# Powered by: Groq API (Llama 3.3)
# ----------------------------------------------------------

import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq

# --- Page Config ---
st.set_page_config(page_title="Healix – AI Health Coach", page_icon="💚", layout="wide")

# --- Initialize Session State ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Groq Client ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])  # Store your key in .streamlit/secrets.toml

# --- Custom CSS ---
st.markdown("""
    <style>
        body {
            background-color: #F8FDFB;
            font-family: 'Poppins', sans-serif;
        }
        .main-title {
            text-align: center;
            font-size: 36px;
            font-weight: 700;
            color: #00BFA6;
        }
        .sub-title {
            text-align: center;
            font-size: 18px;
            color: #555;
        }
        .chat-bubble-user {
            background-color: #DCF8C6;
            padding: 10px;
            border-radius: 15px;
            margin-bottom: 5px;
            max-width: 80%;
            float: right;
        }
        .chat-bubble-ai {
            background-color: #E6F4F1;
            padding: 10px;
            border-radius: 15px;
            margin-bottom: 5px;
            max-width: 80%;
            float: left;
        }
        footer {text-align:center; color:#777; margin-top:30px;}
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.image("https://i.imgur.com/jxWqIBf.png", use_container_width=True)
st.sidebar.title("💚 Healix Menu")
menu = st.sidebar.radio("Navigate", [
    "🏠 Dashboard",
    "💬 Chat with Healix",
    "📏 BMI & BMR Calculator",
    "🥗 AI Meal Plan",
    "🏋️‍♀️ AI Workout Plan",
    "📈 Progress Tracker",
    "🧠 AI Summary"
])

# --- Dashboard ---
if menu == "🏠 Dashboard":
    st.markdown("<h1 class='main-title'>Welcome to Healix 💚</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Your AI-powered fitness and nutrition companion</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current BMI", "22.5", "Healthy")
    with col2:
        st.metric("BMR (kcal/day)", "1420", "+2% vs last week")
    with col3:
        st.metric("Workout Streak", "5 days 🔥")

    df = pd.DataFrame({
        "Week": ["W1", "W2", "W3", "W4"],
        "Weight": [68, 67, 66.5, 66],
        "Calories": [2000, 1800, 1700, 1650]
    })
    fig = px.line(df, x="Week", y=["Weight", "Calories"], markers=True, title="Progress Overview")
    st.plotly_chart(fig, use_container_width=True)

# --- Chat with Healix ---
elif menu == "💬 Chat with Healix":
    st.markdown("<h1 class='main-title'>💬 Chat with Healix</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Ask anything about your diet, fitness, or health goals</p>", unsafe_allow_html=True)

    for sender, message in st.session_state.chat_history:
        if sender == "user":
            st.markdown(f"<div class='chat-bubble-user'>{message}</div><div style='clear:both;'></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-ai'>{message}</div><div style='clear:both;'></div>", unsafe_allow_html=True)

    user_input = st.text_input("Type your question...", key="user_input")
    if st.button("Ask Healix 🤖"):
        if user_input.strip():
            st.session_state.chat_history.append(("user", user_input))
            with st.spinner("Healix is thinking 💭..."):
                prompt = f"You are Healix, a friendly AI health coach. Reply concisely and encouragingly to: {user_input}"
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                reply = response.choices[0].message["content"]
                st.session_state.chat_history.append(("ai", reply))
                st.rerun()

# --- BMI & BMR Calculator ---
elif menu == "📏 BMI & BMR Calculator":
    st.header("📏 BMI & BMR Calculator")
    gender = st.selectbox("Gender", ["Male", "Female"])
    age = st.number_input("Age", 18, 80, 25)
    height = st.number_input("Height (cm)", 100, 250, 170)
    weight = st.number_input("Weight (kg)", 30, 200, 65)

    bmi = weight / ((height / 100) ** 2)
    st.metric("Your BMI", f"{bmi:.2f}")

    if gender == "Male":
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

    st.metric("Your BMR", f"{bmr:.0f} kcal/day")

# --- Meal Plan ---
elif menu == "🥗 AI Meal Plan":
    st.header("🥗 Personalized Meal Plan")
    goal = st.selectbox("Your Goal", ["Weight Loss", "Muscle Gain", "Maintain Fitness"])
    calories = st.slider("Daily Calorie Target", 1200, 3000, 1800, 100)
    st.write("Click below to generate your meal plan:")
    if st.button("Generate Plan 🍱"):
        with st.spinner("Generating your plan..."):
            plan_prompt = f"Create a {goal.lower()} meal plan for a day with about {calories} kcal. Include Pakistani foods."
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": plan_prompt}]
            )
            st.success(response.choices[0].message["content"])

# --- Workout Plan ---
elif menu == "🏋️‍♀️ AI Workout Plan":
    st.header("🏋️‍♀️ AI Workout Plan")
    level = st.selectbox("Your Level", ["Beginner", "Intermediate", "Advanced"])
    days = st.slider("Workout Days per Week", 1, 7, 4)
    if st.button("Generate Workout 💪"):
        with st.spinner("Preparing your plan..."):
            workout_prompt = f"Design a {level.lower()} {days}-day workout plan. Focus on home exercises with minimal equipment."
           response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": workout_prompt}]
)

try:
    st.success(response.choices[0].message.content)
except Exception as e:
    st.error(f"Error: {e}")
    st.write(response)



# --- Progress Tracker ---
elif menu == "📈 Progress Tracker":
    st.header("📈 Track Your Progress")
    uploaded = st.file_uploader("Upload your progress CSV (Week, Weight, Calories)", type="csv")
    if uploaded:
        df = pd.read_csv(uploaded)
        st.dataframe(df)
        fig = px.line(df, x="Week", y=["Weight", "Calories"], markers=True)
        st.plotly_chart(fig)

# --- AI Summary ---
elif menu == "🧠 AI Summary":
    st.header("🧠 AI Summary & Insights")
    with st.spinner("Generating summary..."):
        summary_prompt = "Provide a short motivational health summary for the user."
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": summary_prompt}]
        )
        st.success(response.choices[0].message["content"])

# --- Footer ---
st.markdown("<footer>Made with ❤️ by Usama Bajwa & Iffat Nazir – Healix v1.1</footer>", unsafe_allow_html=True)




