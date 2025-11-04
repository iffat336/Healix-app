🧠 Healix: AI-Powered Health & Wellness Assistant
🌍 Live Demo

👉 Try Healix on Streamlit Cloud

💡 Overview

Healix is an intelligent health and wellness app powered by AI (Groq API) and Streamlit.
It generates personalized meal plans, workout routines (with animated videos), and helps users track and visualize their progress — all in one place.

Healix brings together the power of AI, fitness science, and interactive visualization to promote balanced and data-driven well-being.

🚀 Key Features
Feature	Description
🥗 AI Meal Planner	Generates 3-day personalized diet plans based on weight, goal, and activity level.
🏋️ Workout Generator	Creates tailored exercise routines (Beginner → Advanced) with YouTube demo videos.
📈 Progress Tracker	Upload progress CSV files and visualize trends with dynamic charts.
🕒 History Section	Automatically saves your previously generated plans for later review.
🤖 Powered by Groq Llama 3.3	Uses state-of-the-art LLM inference for nutrition and fitness planning.
🧩 Tech Stack

Frontend: Streamlit

Backend AI: Groq API (LLaMA 3.3 70B Versatile)

Data Handling: Pandas

Visualization: Streamlit charts

Deployment: Streamlit Cloud

⚙️ Setup Instructions

Clone this repository

git clone https://github.com/iffat336/healix-app.git
cd healix-app


Install dependencies

pip install -r requirements.txt


Add your API key
In Streamlit Cloud → Settings → Secrets, add:

GROQ_API_KEY = "your_api_key_here"


Run locally

streamlit run app.py

📸 Preview
Section	Screenshot
Home	🏠 Welcome screen with navigation
Meal Plan	🥗 AI diet plan generation
Workout	💪 Personalized workouts + embedded videos
Progress Tracker	📊 Line chart for uploaded CSV
History	🕒 Saved past plans
🌱 Future Enhancements

🔐 Persistent history (save user data to CSV or Firebase)

💬 AI chat-based fitness assistant

📊 Calorie tracking dashboard

🧬 Integration with wearable data (Fitbit / Apple Health)

👩‍💻 About the Developer

Iffat Nazir — AI researcher and aspiring data scientist passionate about using emerging technologies to improve human well-being.
📚 Background in Plant Breeding & Genetics (MS Hons.), with growing expertise in Data Science, AI, and Applied Research.

🔗 LinkedIn
 | GitHub

⭐ Support the Project

If you like this project, please consider giving it a ⭐ on GitHub
!
Your support motivates further development and research into AI-driven health systems.
