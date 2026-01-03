import streamlit as st
import pandas as pd
from datetime import datetime

def render_health_page(manager):
    st.header("Health & Fitness Tracker")
    
    # Date Selection (Default to Today)
    # Ideally we use a date picker, but for basic reqs, let's stick to today, 
    # OR allow simple navigation. "Today" is safest for MVP.
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # We could add a date input here to view past logs
    selected_date = st.date_input("Date", value=datetime.now())
    date_str = selected_date.strftime("%Y-%m-%d")

    # Get Data
    health_entry = manager.get_daily_health_entry(date_str)
    profile = manager.load_data("profile")
    cal_limit = profile.get("calorie_limit", 2000)
    
    # --- DASHBOARD ---
    st.subheader("Daily Scoreboard")
    
    # Calculate Calories
    food_list = health_entry.get("food_entries", [])
    total_cals = sum(item["calories"] for item in food_list)
    remaining = cal_limit - total_cals
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Calories Consumed", total_cals, delta=f"{remaining} left", delta_color="normal")
        
    with col2:
        # Progress Bar
        # Normalize to 0-1
        progress = min(total_cals / cal_limit, 1.0) if cal_limit > 0 else 0
        
        # Custom color logic for bar isn't directly supported in simple st.progress without CSS hacks,
        # but we can instruct the user via text.
        bar_color = "red" if total_cals > cal_limit else "green"
        st.progress(progress, text=f"{int(progress*100)}% of Limit")
        if total_cals > cal_limit:
            st.error("Over Calorie Limit!")
            
    with col3:
        # Workout Status
        is_workout_done = health_entry.get("workout_completed", False)
        # Use a button that behaves like a toggle or just a checkbox
        # Checkbox is easier for state
        workout_check = st.checkbox("Workout Completed? 🏋️", value=is_workout_done)
        if workout_check != is_workout_done:
            manager.set_workout_status(date_str, workout_check)
            st.rerun()

    # --- FOOD LOGGING ---
    st.divider()
    col_log, col_list = st.columns([1, 1])
    
    with col_log:
        st.write("### 🍎 Log Food")
        with st.form("food_form"):
            name = st.text_input("Food Name")
            cals = st.number_input("Calories", min_value=0, step=10)
            submitted = st.form_submit_button("Add Entry")
            
            if submitted and name:
                manager.add_food_log(date_str, name, cals)
                st.success(f"Added {name}!")
                st.rerun()

        st.write("### ⚖️ Log Weight")
        with st.form("weight_form"):
            # Default to current weight if logged today, else profile weight
            current_log = health_entry.get("weight_log")
            default_weight = current_log if current_log else profile.get("current_weight", 70.0)
            
            weight_val = st.number_input("Weight (kg)", value=float(default_weight), step=0.1)
            weight_submit = st.form_submit_button("Update Weight")
            
            if weight_submit:
                manager.log_weight(date_str, weight_val)
                st.success("Weight Logged!")
                st.rerun()

    with col_list:
        st.write("### 📋 Today's Meals")
        if food_list:
            df = pd.DataFrame(food_list)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No food logged yet.")

    # --- WEIGHT TREND ---
    st.divider()
    st.subheader("Weight Trend 📉")
    history = manager.get_weight_history()
    if history:
        # Convert to DF for cleaner chart
        chart_data = pd.DataFrame(list(history.items()), columns=["Date", "Weight"])
        chart_data["Date"] = pd.to_datetime(chart_data["Date"])
        chart_data.set_index("Date", inplace=True)
        
        st.line_chart(chart_data)
    else:
        st.caption("Log your weight to see the trend line.")
