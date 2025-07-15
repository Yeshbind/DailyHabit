import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import date, datetime

# --- File Setup ---
DATA_FILE = "data/habits.csv"
CHART_DIR = "charts"
os.makedirs("data", exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)

# --- Page Setup ---
st.set_page_config(page_title="🌙 Habit Tracker", layout="wide")

# --- DARK MODE ONLY STYLING ---
background_color = "#1e1e1e"
text_color = "#ffffff"
plot_color = "#90ee90"

st.markdown(f"""
    <style>
    body {{
        background-color: {background_color};
        color: {text_color};
    }}
    .stApp {{
        background-color: {background_color};
        color: {text_color};
    }}
    div[data-testid="stSidebar"] {{
        background-color: #2c2c2c;
        color: {text_color};
    }}
    h1, h2, h3, .stMarkdown {{
        color: {text_color};
    }}
    .stButton>button {{
        background-color: #90ee90;
        color: black;
        border-radius: 10px;
    }}
    .stButton>button:hover {{
        background-color: #75d67a;
        color: white;
    }}
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("🌙 Habit Tracker")

user_name = st.sidebar.text_input("👤 Your Name")
start_date = st.sidebar.date_input("📅 From", datetime(2025, 7, 1))
end_date = st.sidebar.date_input("📅 To", datetime.today())

# --- Greeting ---
st.title("🌿 Personal Habit Tracker")
if user_name:
    st.markdown(f"👋 Hello, **{user_name}**!")
else:
    st.markdown("👋 Welcome! Start logging your habits below.")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📅 Log Habits", "📊 Progress", "📈 Charts"])

# --- Tab 1: Log Habits ---
with tab1:
    st.header("📅 Today's Habit Entry")

    today = date.today()
    sleep = st.number_input("💤 Sleep Hours", 0.0, 24.0, step=0.5)
    study = st.number_input("📚 Study Hours", 0.0, 24.0, step=0.5)
    exercise = st.number_input("🏋️ Exercise (minutes)", 0, 300, step=5)
    water = st.number_input("🚰 Water (liters)", 0.0, 10.0, step=0.1)
    screen = st.number_input("📱 Screen Time (hours)", 0.0, 24.0, step=0.5)

    if st.button("✅ Save Entry"):
        new_data = pd.DataFrame([[today, sleep, study, exercise, water, screen]],
            columns=["Date", "Sleep Hours", "Study Hours", "Exercise (min)", "Water Intake (liters)", "Screen Time (hrs)"]
        )

        if os.path.exists(DATA_FILE):
            old_data = pd.read_csv(DATA_FILE)
            df = pd.concat([old_data, new_data], ignore_index=True)
        else:
            df = new_data

        df.to_csv(DATA_FILE, index=False)
        st.success("✅ Entry saved!")

# --- Tab 2: Progress ---
with tab2:
    st.header("🎯 Daily Goals and Progress")

    goals = {
        "Sleep Hours": st.slider("Sleep Goal (hrs)", 4.0, 12.0, 8.0),
        "Study Hours": st.slider("Study Goal (hrs)", 0.0, 10.0, 4.0),
        "Exercise (min)": st.slider("Exercise Goal", 0, 120, 30),
        "Water Intake (liters)": st.slider("Water Goal (L)", 0.0, 5.0, 2.5),
        "Screen Time (hrs)": st.slider("Max Screen Time (hrs)", 0.0, 12.0, 4.0)
    }

    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        today_data = df[df["Date"] == pd.to_datetime(today)].tail(1)

        if not today_data.empty:
            st.subheader("📊 Today's Progress")
            for habit in goals:
                value = today_data[habit].values[0]
                goal = goals[habit]

                # ✅ Safe clamped progress
                if habit == "Screen Time (hrs)":
                    progress = 1.0 - (value / goal)
                else:
                    progress = value / goal

                progress = max(0.0, min(progress, 1.0))  # Clamp between 0 and 1

                st.progress(progress, f"{habit}: {value} / {goal}")
        else:
            st.info("No data for today yet. Log your habits in the first tab.")

        # Weekly Summary
        st.subheader("📅 Weekly Summary")
        df["Week"] = df["Date"].dt.to_period("W").astype(str)
        summary = df.groupby("Week")[list(goals.keys())].mean().round(2)
        st.dataframe(summary.reset_index(), use_container_width=True)
    else:
        st.info("📂 No data found. Add habits first!")

# --- Tab 3: Charts ---
with tab3:
    st.header("📈 Habit Trends Over Time")

    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")
        df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]

        habit_list = df.columns[1:]
        selected_habit = st.radio("📌 Select Habit", habit_list, horizontal=True)

        fig, ax = plt.subplots()
        ax.plot(df["Date"], df[selected_habit], marker='o', color=plot_color)
        ax.set_title(f"{selected_habit} Over Time", fontsize=14, color=text_color)
        ax.set_xlabel("Date", color=text_color)
        ax.set_ylabel(selected_habit, color=text_color)
        ax.tick_params(axis='x', colors=text_color)
        ax.tick_params(axis='y', colors=text_color)
        ax.grid(True, linestyle='--', alpha=0.6)
        st.pyplot(fig)

        filename = f"{CHART_DIR}/{selected_habit.replace(' ', '_')}_chart.png"
        if st.button("💾 Save Chart as PNG"):
            fig.savefig(filename)
            st.success(f"✅ Chart saved to {filename}")
    else:
        st.info("📉 No data to show. Please log habits.")
