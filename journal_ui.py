import streamlit as st
from datetime import datetime

def render_journal_page(manager):
    st.header("Reflections & Journal 📖")
    
    # --- WRITE SECTION ---
    with st.expander("✍️ Write New Entry", expanded=False):
        with st.form("journal_form"):
            title = st.text_input("Title / Highlight")
            # Text area with markdown instruction
            content = st.text_area("Thoughts", height=200, 
                                   help="Supports Markdown! You can add links like [Link Text](url) or **bold** text.")
            
            submitted = st.form_submit_button("Save Entry")
            if submitted and title and content:
                manager.add_journal_entry(title, content)
                st.success("Saved to Journal!")
                st.rerun()

    # --- READ SECTION ---
    entries = manager.get_journal_entries()
    
    st.divider()
    st.subheader("Timeline")
    
    if not entries:
        st.info("Your journal is empty. Start writing above!")
    else:
        for entry in entries:
            date_obj = datetime.strptime(entry["date"], "%Y-%m-%d %H:%M:%S")
            fmt_date = date_obj.strftime("%B %d, %Y - %I:%M %p")
            
            # Using Expander for clean look
            with st.expander(f"{fmt_date} | {entry['title']}"):
                st.markdown(entry["content"])
