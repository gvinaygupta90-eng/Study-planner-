import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from io import BytesIO

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="StudyOS: Student Planner", page_icon="🎓", layout="wide")

# --- SESSION STATE (The "Database") ---
# This keeps your data alive while the app is running
if 'tasks' not in st.session_state:
    st.session_state['tasks'] = []
if 'resources' not in st.session_state:
    st.session_state['resources'] = []  # Stores links and file info

# --- SIDEBAR: NAVIGATION & INPUTS ---
st.sidebar.title("🎓 StudyOS")
page = st.sidebar.radio("Go to:", ["Dashboard", "Task Planner", "Resource Hub"])

# Helper function to get subjects currently in use
def get_subjects():
    if not st.session_state['tasks']:
        return ["Math", "Physics", "History", "Biology"] # Defaults
    return list(set([t['Subject'] for t in st.session_state['tasks']]))

# --- PAGE 1: DASHBOARD (The Overview) ---
if page == "Dashboard":
    st.title("📊 Study Overview")
    
    if not st.session_state['tasks']:
        st.info("👋 Welcome! Go to the 'Task Planner' tab to add your first study goal.")
        
        # --- DEMO DATA FOR VISUALIZATION ---
        # This shows the user what the dashboard WILL look like
        st.markdown("### *Demo View (What it will look like):*")
        col1, col2, col3 = st.columns(3)
        col1.metric("Pending Tasks", "5", "-2")
        col2.metric("Study Hours", "12.5", "+3.2")
        col3.metric("Next Exam", "2 Days", "Math")
    else:
        # REAL DATA COMPUTATION
        df = pd.DataFrame(st.session_state['tasks'])
        
        # KPIs
        total_tasks = len(df)
        completed = len(df[df['Status'] == 'Done'])
        pending = total_tasks - completed
        completion_rate = int((completed / total_tasks) * 100) if total_tasks > 0 else 0
        
        # KPI Row
        c1, c2, c3 = st.columns(3)
        c1.metric("Completion Rate", f"{completion_rate}%")
        c2.metric("Pending Tasks", pending)
        c3.metric("Completed Chapters", completed)
        
        st.divider()
        
        # CHARTS
        c_left, c_right = st.columns(2)
        
        with c_left:
            st.subheader("Progress by Subject")
            # Count tasks per subject
            subj_counts = df['Subject'].value_counts().reset_index()
            subj_counts.columns = ['Subject', 'Count']
            fig_bar = px.bar(subj_counts, x='Subject', y='Count', color='Subject', template="plotly_white")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with c_right:
            st.subheader("Task Status")
            status_counts = df['Status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            fig_pie = px.pie(status_counts, values='Count', names='Status', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

# --- PAGE 2: TASK PLANNER (Calendar & To-Do) ---
elif page == "Task Planner":
    st.title("📅 Study Schedule")
    
    # 1. ADD NEW TASK FORM
    with st.expander("➕ Add New Study Task", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            subject = st.text_input("Subject (e.g., Physics)")
        with c2:
            chapter = st.text_input("Chapter (e.g., Thermodynamics)")
        with c3:
            topic = st.text_input("Topic (e.g., Heat Transfer)")
            
        c4, c5 = st.columns(2)
        with c4:
            due_date = st.date_input("Due Date", datetime.date.today())
        with c5:
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            
        if st.button("Add Task"):
            if subject and chapter:
                st.session_state['tasks'].append({
                    "Subject": subject,
                    "Chapter": chapter,
                    "Topic": topic,
                    "Due Date": due_date,
                    "Priority": priority,
                    "Status": "Pending"
                })
                st.success("Task Added!")
                st.rerun()
            else:
                st.error("Please fill in at least Subject and Chapter.")

    # 2. VIEW TASKS
    st.divider()
    st.subheader("Your To-Do List")
    
    if st.session_state['tasks']:
        df_tasks = pd.DataFrame(st.session_state['tasks'])
        
        # Simple Filter
        filter_status = st.selectbox("Filter by Status:", ["All", "Pending", "Done"])
        if filter_status != "All":
            df_tasks = df_tasks[df_tasks['Status'] == filter_status]
            
        # Display as an interactive editor
        # Users can check boxes or change status directly in the table!
        edited_df = st.data_editor(
            df_tasks,
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    help="Update status",
                    width="medium",
                    options=["Pending", "In Progress", "Done"],
                    required=True,
                ),
                "Due Date": st.column_config.DateColumn("Due Date")
            },
            num_rows="dynamic"
        )
        
        # Sync changes back to session state (Optional advanced feature)
        # For simplicity, we just display the editable table for now.
    else:
        st.info("No tasks yet. Add one above!")

# --- PAGE 3: RESOURCE HUB (PDFs, Links, Videos) ---
elif page == "Resource Hub":
    st.title("📚 Digital Library")
    
    # Organize by Subject
    subjects = get_subjects()
    if not subjects:
        subjects = ["General"]
    
    selected_subject = st.selectbox("Select Subject:", subjects)
    
    # TABS for different media types
    tab1, tab2, tab3 = st.tabs(["🔗 Web Links", "📺 YouTube/Video", "📄 Upload PDFs"])
    
    with tab1:
        st.subheader("Save Website Links")
        link_url = st.text_input("Paste URL:")
        link_desc = st.text_input("Description (e.g., Wikipedia Article):")
        if st.button("Save Link"):
            st.session_state['resources'].append({
                "Subject": selected_subject,
                "Type": "Link",
                "Content": link_url,
                "Desc": link_desc
            })
            st.success("Link Saved!")
            
        # Display Links
        st.write("---")
        for res in st.session_state['resources']:
            if res['Type'] == "Link" and res['Subject'] == selected_subject:
                st.markdown(f"🔗 **[{res['Desc']}]({res['Content']})**")

    with tab2:
        st.subheader("Embed Educational Videos")
        video_url = st.text_input("Paste YouTube URL:")
        if st.button("Add Video"):
             st.session_state['resources'].append({
                "Subject": selected_subject,
                "Type": "Video",
                "Content": video_url
            })
        
        # Display Videos
        st.write("---")
        for res in st.session_state['resources']:
            if res['Type'] == "Video" and res['Subject'] == selected_subject:
                st.video(res['Content'])

    with tab3:
        st.subheader("Upload Study Material")
        uploaded_file = st.file_uploader("Upload PDF or Image", type=['pdf', 'png', 'jpg'])
        
        if uploaded_file is not None:
            # In a real app, you save this to disk. 
            # Here we just show it immediately for the session.
            st.write(f"**Previewing: {uploaded_file.name}**")
            
            if uploaded_file.type == "application/pdf":
                # PDF Display is tricky in browsers, we provide a download button usually
                # or use an iframe. Simplest is to let them download it back.
                st.download_button(
                    label="Download PDF",
                    data=uploaded_file,
                    file_name=uploaded_file.name,
                    mime='application/pdf',
                )
            else:
                st.image(uploaded_file)

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** This app runs locally. If you close the terminal, your tasks reset (unless you add a database save function).")