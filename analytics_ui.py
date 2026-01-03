import streamlit as st
import pandas as pd
from datetime import datetime
import calendar

def render_analytics_page(manager):
    st.header("Analytics & Monthly Wrapped 🎁")
    
    # --- CONTROLS ---
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        current_month = datetime.now().month
        selected_month = st.selectbox("Select Month", 
                                      list(range(1, 13)), 
                                      index=current_month-1, 
                                      format_func=lambda x: calendar.month_name[x])
    with col_sel2:
        current_year = datetime.now().year
        selected_year = st.number_input("Year", value=current_year)
        
    # Get Data
    stats = manager.get_monthly_analytics(selected_year, selected_month)
    
    # --- CARDS ---
    st.subheader(f"Overview for {calendar.month_name[selected_month]}")
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.metric("Task Completion", f"{int(stats['completion_rate'])}%")
    with c2:
        st.metric("Calorie Discipline", f"{stats['days_under_limit']} Days", help="Days under calorie limit")
    with c3:
        st.metric("Workouts", stats['workouts_count'])
    with c4:
        delta = stats['weight_change']
        st.metric("Weight Change", f"{delta:+.1f} kg", delta_color="inverse")

    # --- THE VERDICT (SCORE) ---
    # Simple Scoring Logic (0-100)
    # Weights: Tasks (30%), Calories (40%), Workouts (30%)
    
    # Tasks: 100% completion = 30 pts
    score_tasks = (stats['completion_rate'] / 100) * 30
    
    # Calories: Assume 25 days/month is perfect (allow cheat days) -> 40 pts
    days_cal = stats['days_under_limit']
    score_cals = min((days_cal / 25) * 40, 40)
    
    # Workouts: Assume 12 workouts/month (3x/week) is perfect -> 30 pts
    workouts = stats['workouts_count']
    score_workouts = min((workouts / 12) * 30, 30)
    
    total_score = int(score_tasks + score_cals + score_workouts)
    
    st.divider()
    
    if total_score > 80:
        st.balloons()
        st.success(f"## 🔥 Score: {total_score}/100 - You are crushing it!")
        st.write("You are consistently hitting your goals. This is the person you want to be.")
    elif total_score > 50:
        st.info(f"## 👍 Score: {total_score}/100 - Good Progress")
        st.write("You're doing well, but there's room to tighten up the discipline.")
    else:
        st.warning(f"## ⚠️ Score: {total_score}/100 - Needs Improvement")
        st.write("A bit of a slow month? Let's reset and get back on track.")

    # --- CALORIE CHART ---
    st.divider()
    st.subheader("Daily Calories vs Limit")
    
    daily_cals = stats['daily_cals']
    if daily_cals:
        # Prepare Dataframe
        df = pd.DataFrame(list(daily_cals.items()), columns=["Date", "Calories"])
        df["Date"] = pd.to_datetime(df["Date"]).dt.day # Just show day number
        df.set_index("Date", inplace=True)
        
        # Add Limit Line (We'll just plot it as a separate column for comparison)
        df["Limit"] = stats['cal_limit']
        
        st.bar_chart(df[["Calories", "Limit"]])
    else:
        st.info("No calorie data available for this month.")
