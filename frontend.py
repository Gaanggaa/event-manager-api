import streamlit as st
import requests
from datetime import date

API_URL = "http://localhost:5000"

st.set_page_config(page_title="Event Manager", layout="wide")
st.title("🎉 Event Manager Dashboard")

# --- Event Section ---
st.header("📅 Events")

tab1, tab2 = st.tabs(["All Events", "Add Event"])

with tab1:
    response = requests.get(f"{API_URL}/events")
    if response.status_code == 200:
        events = response.json()
        for event in events:
            with st.expander(f"{event['name']} – {event['date']} at {event['location']}"):
                st.write("**Location:**", event['location'])
                st.write("**Date:**", event['date'])

                if st.button(f"🗑️ Delete Event {event['id']}", key=f"delete_{event['id']}"):
                    requests.delete(f"{API_URL}/events/{event['id']}")
                    st.success("Event deleted. Refresh the page.")

                # Show attendees
                attendees = requests.get(f"{API_URL}/attendees?event_id={event['id']}").json()
                st.markdown("#### 🎫 Attendees")
                for attendee in attendees:
                    col1, col2 = st.columns([3, 1])
                    col1.write(f"👤 {attendee['name']} – {attendee['email']}")
                    if col2.button("❌ Remove", key=f"remove_{attendee['id']}"):
                        requests.delete(f"{API_URL}/attendees/{attendee['id']}")
                        st.success("Attendee removed. Refresh the page.")

                # Add new attendee
                st.markdown("#### ➕ Add Attendee")
                with st.form(f"add_attendee_form_{event['id']}"):
                    name = st.text_input("Name", key=f"name_{event['id']}")
                    email = st.text_input("Email", key=f"email_{event['id']}")
                    submitted = st.form_submit_button("Add")
                    if submitted:
                        res = requests.post(f"{API_URL}/attendees", json={
                            "name": name,
                            "email": email,
                            "event_id": event['id']
                        })
                        if res.status_code == 201:
                            st.success("Attendee added. Refresh the page.")
                        else:
                            st.error("Failed to add attendee.")

with tab2:
    with st.form("create_event_form"):
        name = st.text_input("Event Name")
        location = st.text_input("Location")
        event_date = st.date_input("Date", value=date.today())
        submit = st.form_submit_button("Create Event")

        if submit:
            response = requests.post(f"{API_URL}/events", json={
                "name": name,
                "location": location,
                "date": str(event_date)
            })
            if response.status_code == 201:
                st.success("Event created successfully! Refresh the page.")
            else:
                st.error("Failed to create event.")
