import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_avatar(current_weight, goal_weight):
    """
    Draws a 3-circle "blob" avatar.
    Dimensions are influenced by the difference between current and goal weight.
    """
    fig, ax = plt.subplots(figsize=(3, 4))
    
    # Calculate a scaling factor based on weight difference
    # If current > goal, factor > 1 (wider)
    # If current < goal, factor < 1 (slimmer)
    # Base factor is 1 when current == goal
    
    # Avoid division by zero and extreme values
    if goal_weight <= 0:
        ratio = 1.0
    else:
        ratio = current_weight / goal_weight
        
    # Dampen the effect so it's not too extreme visually
    # ratio of 1.2 (20% overweight) might translate to 1.1x width
    width_factor = 1 + (ratio - 1) * 0.5
    
    # Colors
    color_skin = '#FFCCAA'  # Simple skin tone
    
    # 1. Legs (Bottom Circle)
    # Base width = 0.6, height = 0.5, centered at (0.5, 0.25)
    legs_width = 0.6 * width_factor
    legs = patches.Ellipse((0.5, 0.2), legs_width, 0.4, color=color_skin)
    ax.add_patch(legs)
    
    # 2. Body (Middle Circle) - Most affected by weight
    # Base width = 0.7, height = 0.6, centered at (0.5, 0.55)
    body_width = 0.7 * (width_factor ** 1.2) # Body gets wider faster
    body = patches.Ellipse((0.5, 0.55), body_width, 0.55, color=color_skin)
    ax.add_patch(body)
    
    # 3. Head (Top Circle)
    # Base width = 0.4, height = 0.4, centered at (0.5, 0.85)
    # Head changes less with weight
    head_width = 0.4 * (width_factor ** 0.5) 
    head = patches.Ellipse((0.5, 0.9), head_width, 0.4, color=color_skin)
    ax.add_patch(head)
    
    # Configuration
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.2)
    ax.axis('off') # Remove axes
    
    return fig

def render_profile_page(manager):
    st.header("User Profile")
    
    profile_data = manager.load_data("profile")
    
    # Layout: Settings on Left, Avatar on Right
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Edit Details")
        with st.form("profile_form"):
            new_name = st.text_input("Name", value=profile_data.get("name", "New User"))
            new_height = st.number_input("Height (cm)", value=float(profile_data.get("height", 170.0)))
            new_weight = st.number_input("Current Weight (kg)", value=float(profile_data.get("current_weight", 70.0)))
            goal_weight = st.number_input("Goal Weight (kg)", value=float(profile_data.get("goal_weight", 65.0)))
            calories = st.number_input("Daily Calorie Limit", value=int(profile_data.get("calorie_limit", 2000)))
            
            submitted = st.form_submit_button("Save Profile")
            
            if submitted:
                updated_data = {
                    "name": new_name,
                    "height": new_height,
                    "current_weight": new_weight,
                    "goal_weight": goal_weight,
                    "calorie_limit": calories,
                    "avatar_config": profile_data.get("avatar_config", {})
                }
                manager.save_data("profile", updated_data)
                manager.log_action("PROFILE_UPDATE", f"Updated details for {new_name}")
                st.success("Profile Saved!")
                st.rerun()

    with col2:
        st.subheader("Your Avatar")
        # Visualizer
        curr = profile_data.get("current_weight", 70.0)
        goal = profile_data.get("goal_weight", 65.0)
        
        fig = draw_avatar(curr, goal)
        st.pyplot(fig)
        
        # Stats below avatar
        st.caption(f"Current: {curr} kg | Goal: {goal} kg")
        
        # Progress Bar
        if goal > 0:
            # Calculate progress. 
            # If current > goal, we want to lose weight.
            # If current < goal (bulking?), logic might differ, but assuming weight loss for now.
            # Let's visualize "closeness" to goal.
            
            diff = curr - goal
            if diff == 0:
                progress = 1.0
                st.write("🎉 Goal Reached!")
            else:
                 # Simple specific logic: assume starting from some higher point? 
                 # Or just show a static bar isn't ideal without start_weight.
                 # Let's just show a meter of specific 'goal completion' based on arbitrary range?
                 # Better: Just visualize "Goal Weight" relative to current.
                 pass
            
            # Simple "Goal Proximity" Bar?
            # Let's assume a "start weight" logic is missing, so we'll just show a visual indicator.
            # Normalizing isn't easy without a start point.
            # Let's try this: 
            # If curr > goal: Progress = goal / curr (Approaching 1)
            # If curr < goal: Progress = curr / goal (Approaching 1)
            
            if curr > goal:
               ratio = goal / curr
               st.progress(ratio, text="Proximity to Goal (Weight Loss)")
            else:
               ratio = curr / goal
               st.progress(ratio, text="Proximity to Goal (Gaining)")
