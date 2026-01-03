import streamlit as st
import random
from datetime import datetime

# Import modules
from data_manager import DataManager
from profile_ui import render_profile_page
from tasks_ui import render_tasks_page
from health_ui import render_health_page
from analytics_ui import render_analytics_page
from journal_ui import render_journal_page

def main():
    st.set_page_config(page_title="LifeTracker", layout="wide", page_icon="🧬") # Added icon for polish
    
    # Initialize Data Manager
    dm = DataManager()
    
    # --- NAVIGATION ---
    st.sidebar.title("LifeTracker")
    
    # Map friendly names to page IDs or functions
    nav_options = {
        "🏠 Home": "home",
        "📝 Tasks": "tasks",
        "🍎 Health & Calorie": "health",
        "📓 Journal": "journal",
        "📊 Annual Wrapped": "analytics",
        "👤 Profile": "profile"
    }
    
    selection = st.sidebar.radio("Navigate", list(nav_options.keys()))
    page = nav_options[selection]
    
    st.sidebar.divider()
    st.sidebar.caption(f"📅 {datetime.now().strftime('%B %d, %Y')}")

    # --- ROUTING ---
    if page == "home":
        render_home_dashboard(dm)
    elif page == "tasks":
        render_tasks_page(dm)
    elif page == "health":
        render_health_page(dm)
    elif page == "journal":
        render_journal_page(dm)
    elif page == "analytics":
        render_analytics_page(dm)
    elif page == "profile":
        render_profile_page(dm)

def render_home_dashboard(manager):
    """Renders the Home Dashboard with At-a-Glance stats."""
    profile = manager.load_data("profile")
    user_name = profile.get("name", "User")
    
    st.title(f"Welcome back, {user_name}! 👋")
    
    # --- MOTIVATIONAL QUOTE ---
    quotes = [
        "The only way to do great work is to love what you do.",
        "Success is the sum of small efforts, repeated day in and day out.",
        "Don't watch the clock; do what it does. Keep going.",
        "Your future is created by what you do today, not tomorrow.",
        "Dream big. Start small. Act now.",
        "Discipline is choosing between what you want now and what you want most."
    ]
    st.markdown(f"> *{random.choice(quotes)}*")
    st.divider()
    
    # --- QUICK STATS ---
    st.subheader("At a Glance")
    
    # Calculations
    # 1. Tasks Left
    tasks = manager.load_data("tasks")
    pending_count = len([t for t in tasks if t.get("status") == "Pending"])
    
    # 2. Calories Remaining
    today_str = datetime.now().strftime("%Y-%m-%d")
    health_entry = manager.get_daily_health_entry(today_str)
    consumed_cals = sum(item["calories"] for item in health_entry.get("food_entries", []))
    limit_cals = profile.get("calorie_limit", 2000)
    remaining_cals = limit_cals - consumed_cals
    
    # Display Stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Tasks Left Today", pending_count, delta=None)
        if pending_count > 0:
            st.caption("Go to **Tasks** to knock them out!")
        else:
            st.caption("All clear! Great job.")
            
    with col2:
        # Color logic for delta: negative is bad if over limit (but metric delta usually shows increase/decrease)
        # We'll just use the value.
        st.metric("Calories Remaining", remaining_cals, delta=f"{consumed_cals} consumed today", delta_color="inverse")
        
    with col3:
        # Maybe show current weight gap?
        curr = profile.get("current_weight", 0)
        goal = profile.get("goal_weight", 0)
        gap = round(curr - goal, 1)
        st.metric("Weight Gap", f"{gap} kg", help="Difference from goal weight")

    # --- ILLUSTRATION / CALL TO ACTION ---
    st.divider()
    st.info("💡 **Tip:** Check your **Analytics** to see your monthly 'Life Score'!")

if __name__ == "__main__":
    main()
