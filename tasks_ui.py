import streamlit as st

def render_tasks_page(manager):
    st.header("Task Tracker")

    # --- INPUT SECTION ---
    with st.expander("Add New Task", expanded=True):
        with st.form("new_task_form"):
            col1, col2 = st.columns([2, 1])
            with col1:
                task_name = st.text_input("Task Name")
            with col2:
                category = st.selectbox("Category", ["Daily Goal", "Work", "Study"])
            
            submitted = st.form_submit_button("Add Task")
            if submitted and task_name:
                manager.add_task(task_name, category)
                st.success(f"Added: {task_name}")
                st.rerun()

    # --- DISPLAY SECTION ---
    tasks = manager.load_data("tasks")
    
    # Separate lists for display (not by modifying the original list in place yet)
    # We need to map UI indices back to original list indices for simple updates,
    # OR we handle updates by finding the specific task.
    # Simpler approach: iterate through entire list, but display in different columns.
    
    st.subheader("Your Agenda")
    
    col_goals, col_work = st.columns(2)
    
    with col_goals:
        st.write("### 🌞 Today's Goals")
        _render_task_list(manager, tasks, "Daily Goal")
        
    with col_work:
        st.write("### 💼 Work & Study")
        _render_task_list(manager, tasks, ["Work", "Study"])

    # --- CLEANUP SECTION ---
    st.divider()
    if st.button("Clear Completed Tasks"):
        count = manager.archive_completed_tasks()
        if count > 0:
            st.success(f"Archived {count} tasks!")
            st.rerun()
        else:
            st.info("No completed tasks to clear.")

def _render_task_list(manager, all_tasks, category_filter):
    """Helper to render checks for a specific category."""
    # Handle list of categories or single string
    if isinstance(category_filter, str):
        categories = [category_filter]
    else:
        categories = category_filter

    # We need to preserve the ORIGINAL index to update the correct task
    for i, task in enumerate(all_tasks):
        if task.get("category") in categories:
            is_done = task.get("status") == "Done"
            
            # Label formatting
            label = task.get("name")
            if is_done:
                label = f"~~{label}~~"
                
            # Checkbox
            # Key must be unique: task_id_{i}
            checked = st.checkbox(label, value=is_done, key=f"task_{i}")
            
            # Logic: If UI state != Data state, update and rerun
            if checked != is_done:
                new_status = "Done" if checked else "Pending"
                manager.update_task_status(i, new_status)
                st.rerun()
