# frontend.py
import streamlit as st
import requests
from datetime import date
from streamlit_calendar import calendar  # New import for interactive calendar

API_URL = "http://localhost:5000"

st.set_page_config(page_title="Event Manager", layout="wide")
st.title("🎉 Event Manager")

if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
    st.session_state.username = ""
    st.session_state.is_admin = False

def login():
    st.subheader("🔐 Login")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        res = requests.post(f"{API_URL}/login", json={
            "username": username,
            "password": password
        })
        if res.status_code == 200:
            data = res.json()
            st.session_state.is_logged_in = True
            st.session_state.username = username
            st.session_state.is_admin = data['is_admin']
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Login failed. Invalid credentials.")

def register():
    st.subheader("📝 Sign Up (New Users)")
    username = st.text_input("Choose a Username", key="reg_username")
    email = st.text_input("Email Address", key="reg_email")
    password = st.text_input("Create Password", type="password", key="reg_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
    is_admin = st.checkbox("Register as Admin", key="reg_admin")

    if st.button("Register"):
        if not username or not email or not password:
            st.error("All fields are required.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            response = requests.post(f"{API_URL}/register", json={
                "username": username,
                "email": email,
                "password": password,
                "is_admin": is_admin
            })
            if response.status_code == 201:
                st.success("🎉 Registration successful! Please log in.")
            else:
                error_message = response.json().get("error", "Registration failed.")
                st.error(f"❌ {error_message}")

def logout():
    requests.post(f"{API_URL}/logout")
    st.session_state.is_logged_in = False
    st.session_state.username = ""
    st.session_state.is_admin = False
    st.success("Logged out.")
    st.rerun()

def admin_dashboard():
    st.header("📅 Admin Dashboard")
    tab1, tab2 = st.tabs(["All Events", "Create Event"])

    with tab1:
        res = requests.get(f"{API_URL}/events")
        if res.status_code == 200:
            events = res.json()
            for event in events:
                with st.expander(f"{event['name']} – {event['date']} at {event['location']}"):
                    st.write("📍", event['location'])
                    st.write("📆", event['date'])
                    if st.button("🗑 Delete", key=f"del_{event['id']}"):
                        requests.delete(f"{API_URL}/events/{event['id']}")
                        st.success("Deleted. Refresh page.")
                    attendees = requests.get(f"{API_URL}/attendees?event_id={event['id']}").json()
                    st.markdown("#### 🎫 Attendees")
                    for attendee in attendees:
                        st.write(f"👤 {attendee['name']} – {attendee['email']}")

    with tab2:
        with st.form("create_event_form"):
            name = st.text_input("Event Name")
            location = st.text_input("Location")
            event_date = st.date_input("Date", value=date.today())
            submit = st.form_submit_button("Create Event")
            if submit:
                res = requests.post(f"{API_URL}/events", json={
                    "name": name,
                    "location": location,
                    "date": str(event_date)
                })
                if res.status_code == 201:
                    st.success("Event created!")

def user_dashboard():
    st.header("🎟 Available Events")
    res = requests.get(f"{API_URL}/events")
    if res.status_code == 200:
        events = res.json()
        for event in events:
            with st.expander(f"{event['name']} – {event['date']} at {event['location']}"):
                st.write("📍", event['location'])
                st.write("📆", event['date'])
                with st.form(f"register_{event['id']}"):
                    email = st.text_input("Your Email", key=f"email_{event['id']}")
                    submitted = st.form_submit_button("Register for this event")
                    if submitted:
                        r = requests.post(f"{API_URL}/attendees", json={
                            "name": st.session_state.username,
                            "email": email,
                            "event_id": event['id']
                        })
                        if r.status_code == 201:
                            st.success("✅ Registered!")
                        else:
                            st.error("❌ Registration failed.")

def calendar_view():
    st.header("📆 Event Calendar")
    res = requests.get(f"{API_URL}/events")
    if res.status_code == 200:
        events = res.json()
        calendar_events = [
            {
                "title": f"{event['name']} @ {event['location']}",
                "start": event["date"],
                "end": event["date"],
                "color": "#FF5733"
            }
            for event in events
        ]
        calendar_options = {
            "initialView": "dayGridMonth",
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek,timeGridDay"
            },
            "events": calendar_events
        }
        calendar(events=calendar_events, options=calendar_options)
    else:
        st.error("❌ Could not load events for calendar.")

menu = ["Login", "Register"] if not st.session_state.is_logged_in else ["Dashboard", "Logout"]
choice = st.sidebar.selectbox("Navigation", menu)

if not st.session_state.is_logged_in:
    if choice == "Login":
        login()
    elif choice == "Register":
        register()
else:
    st.sidebar.success(f"👋 Welcome, {st.session_state.username}")
    if choice == "Dashboard":
        tabs = st.tabs(["📆 Calendar", "📋 Events"])
        with tabs[0]:
            calendar_view()
        with tabs[1]:
            admin_dashboard() if st.session_state.is_admin else user_dashboard()
    elif choice == "Logout":
        logout()





