import streamlit as st
import pandas as pd
import json
import hashlib
from datetime import datetime, date
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Job Application Tracker",
    page_icon="💼",
    layout="wide"
)

# File paths for storing data
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
USERS_FILE = DATA_DIR / "users.json"

# Status options for dropdown
STATUS_OPTIONS = [
    "Applied",
    "Interview Scheduled",
    "Interview Done",
    "Offer Received",
    "Rejected",
    "Withdrawn"
]

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A5F;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }
    .login-header {
        font-size: 2rem;
        font-weight: 700;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .stDataFrame {
        border-radius: 10px;
    }
    div[data-testid="stForm"] {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }
    .welcome-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def hash_password(password):
    """Hash password for storage."""
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    """Load users from JSON file."""
    if USERS_FILE.exists():
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users):
    """Save users to JSON file."""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def get_user_data_file(username):
    """Get the data file path for a specific user."""
    return DATA_DIR / f"jobs_{username}.json"


def load_data(username):
    """Load job applications for a specific user."""
    data_file = get_user_data_file(username)
    if data_file.exists():
        with open(data_file, "r") as f:
            data = json.load(f)
            if data:
                df = pd.DataFrame(data)
                df["Applied Date"] = pd.to_datetime(df["Applied Date"]).dt.date
                return df
    return pd.DataFrame(columns=["Company Name", "Job Title", "Status", "Applied Date", "Package"])


def save_data(username, df):
    """Save job applications for a specific user."""
    data_file = get_user_data_file(username)
    data = df.copy()
    data["Applied Date"] = data["Applied Date"].astype(str)
    with open(data_file, "w") as f:
        json.dump(data.to_dict(orient="records"), f, indent=2)


def login_page():
    """Display login/register page."""
    st.markdown('<p class="main-header">💼 Job Application Tracker</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Track your job applications with ease</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            with st.form("login_form"):
                st.subheader("Welcome Back!")
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                login_btn = st.form_submit_button("Login", use_container_width=True, type="primary")
                
                if login_btn:
                    if username and password:
                        users = load_users()
                        if username in users and users[username]["password"] == hash_password(password):
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.session_state.display_name = users[username].get("display_name", username)
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
                    else:
                        st.error("Please enter both username and password")
        
        with tab2:
            with st.form("register_form"):
                st.subheader("Create Account")
                new_username = st.text_input("Username", placeholder="Choose a username", key="reg_user")
                new_display_name = st.text_input("Display Name", placeholder="Your name", key="reg_display")
                new_password = st.text_input("Password", type="password", placeholder="Create a password", key="reg_pass")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password", key="reg_confirm")
                register_btn = st.form_submit_button("Register", use_container_width=True, type="primary")
                
                if register_btn:
                    if new_username and new_password and new_display_name:
                        if new_password != confirm_password:
                            st.error("❌ Passwords do not match")
                        elif len(new_password) < 4:
                            st.error("❌ Password must be at least 4 characters")
                        else:
                            users = load_users()
                            if new_username in users:
                                st.error("❌ Username already exists")
                            else:
                                users[new_username] = {
                                    "password": hash_password(new_password),
                                    "display_name": new_display_name,
                                    "created_at": datetime.now().isoformat()
                                }
                                save_users(users)
                                st.success("✅ Account created! Please login.")
                    else:
                        st.error("Please fill in all fields")


def main_app():
    """Main application after login."""
    username = st.session_state.username
    display_name = st.session_state.display_name
    
    # Header with user info
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown('<p class="main-header">💼 Job Application Tracker</p>', unsafe_allow_html=True)
    with col2:
        st.markdown(f"**👤 {display_name}**")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.display_name = None
            st.session_state.pop("jobs_df", None)
            st.rerun()
    
    st.markdown('<p class="sub-header">Keep track of all your job applications in one place</p>', unsafe_allow_html=True)
    
    # Initialize session state for this user
    if "jobs_df" not in st.session_state or st.session_state.get("current_user") != username:
        st.session_state.jobs_df = load_data(username)
        st.session_state.current_user = username
    
    # Sidebar for adding new applications
    with st.sidebar:
        st.header("➕ Add New Application")
        
        with st.form("add_job_form", clear_on_submit=True):
            company_name = st.text_input("Company Name*", placeholder="e.g., Google")
            job_title = st.text_input("Job Title*", placeholder="e.g., Software Engineer")
            status = st.selectbox("Status", STATUS_OPTIONS)
            applied_date = st.date_input("Applied Date", value=date.today())
            package = st.text_input("Package/Salary", placeholder="e.g., ₹15 LPA or $120,000")
            
            submitted = st.form_submit_button("Add Application", use_container_width=True, type="primary")
            
            if submitted:
                if company_name and job_title:
                    new_row = pd.DataFrame([{
                        "Company Name": company_name,
                        "Job Title": job_title,
                        "Status": status,
                        "Applied Date": applied_date,
                        "Package": package
                    }])
                    st.session_state.jobs_df = pd.concat([st.session_state.jobs_df, new_row], ignore_index=True)
                    save_data(username, st.session_state.jobs_df)
                    st.success("✅ Application added!")
                    st.rerun()
                else:
                    st.error("Please fill in Company Name and Job Title")
    
    # Main content area
    st.divider()
    
    # Filters section
    st.subheader("🔍 Filter Applications")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input(
            "Search by Company or Job Title",
            placeholder="Type to search...",
            label_visibility="collapsed"
        )
    
    with col2:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All"] + STATUS_OPTIONS,
            label_visibility="collapsed"
        )
    
    with col3:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.session_state.jobs_df = load_data(username)
            st.rerun()
    
    # Apply filters
    filtered_df = st.session_state.jobs_df.copy()
    
    if search_query:
        mask = (
            filtered_df["Company Name"].str.contains(search_query, case=False, na=False) |
            filtered_df["Job Title"].str.contains(search_query, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["Status"] == status_filter]
    
    st.divider()
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    total_apps = len(st.session_state.jobs_df)
    with col1:
        st.metric("📊 Total Applications", total_apps)
    with col2:
        interview_count = len(st.session_state.jobs_df[st.session_state.jobs_df["Status"].str.contains("Interview", na=False)])
        st.metric("🎯 Interviews", interview_count)
    with col3:
        offers = len(st.session_state.jobs_df[st.session_state.jobs_df["Status"] == "Offer Received"])
        st.metric("🎉 Offers", offers)
    with col4:
        pending = len(st.session_state.jobs_df[st.session_state.jobs_df["Status"] == "Applied"])
        st.metric("⏳ Pending", pending)
    
    st.divider()
    
    # Job applications table
    st.subheader("📋 Your Applications")
    
    if filtered_df.empty:
        st.info("No job applications found. Add your first application using the sidebar!")
    else:
        # Add index for selection
        filtered_df_display = filtered_df.reset_index(drop=True)
        
        # Editable dataframe
        edited_df = st.data_editor(
            filtered_df_display,
            column_config={
                "Company Name": st.column_config.TextColumn(
                    "Company Name",
                    width="medium",
                    required=True
                ),
                "Job Title": st.column_config.TextColumn(
                    "Job Title",
                    width="medium",
                    required=True
                ),
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=STATUS_OPTIONS,
                    width="medium",
                    required=True
                ),
                "Applied Date": st.column_config.DateColumn(
                    "Applied Date",
                    format="DD/MM/YYYY",
                    width="small"
                ),
                "Package": st.column_config.TextColumn(
                    "Package",
                    width="medium"
                )
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            key="job_editor"
        )
        
        # Save changes button
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            if st.button("💾 Save Changes", type="primary", use_container_width=True):
                st.session_state.jobs_df = edited_df.copy()
                save_data(username, st.session_state.jobs_df)
                st.success("✅ Changes saved successfully!")
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear All", type="secondary", use_container_width=True):
                st.session_state.show_confirm = True
        
        # Confirmation dialog for clearing all data
        if st.session_state.get("show_confirm", False):
            st.warning("⚠️ Are you sure you want to delete ALL applications?")
            col_yes, col_no, _ = st.columns([1, 1, 4])
            with col_yes:
                if st.button("Yes, Delete All", type="primary"):
                    st.session_state.jobs_df = pd.DataFrame(columns=["Company Name", "Job Title", "Status", "Applied Date", "Package"])
                    save_data(username, st.session_state.jobs_df)
                    st.session_state.show_confirm = False
                    st.rerun()
            with col_no:
                if st.button("Cancel"):
                    st.session_state.show_confirm = False
                    st.rerun()
    
    # Footer
    st.divider()
    st.markdown(
        "<p style='text-align: center; color: #888;'>💡 Tip: Use the data editor above to edit or delete individual rows. "
        "Click on a cell to edit, and use the row actions to delete.</p>",
        unsafe_allow_html=True
    )


def main():
    """Main entry point."""
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    # Show login or main app based on state
    if st.session_state.logged_in:
        main_app()
    else:
        login_page()


if __name__ == "__main__":
    main()
