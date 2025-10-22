import streamlit as st
import pandas as pd
import time
import random
import numpy as np
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from uuid import uuid4

# Imports for Real-Time Video Processing
import cv2 
from PIL import Image
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase 

# --- Configuration and Utility Functions ---

# Set wide page configuration
st.set_page_config(layout="wide", page_title="Real-Time Safety Detection", page_icon="🛡️")

# --- STYLING ---
def set_styles():
    st.markdown("""
        <style>
        .stApp {
            background-color: #0F172A; /* Slate 900 */
        }
        /* Custom styling for primary button (Simulate Incident) */
        .stButton>button:first-child {
            background-color: #DC2626; /* Red 600 */
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            transition: all 0.3s;
            font-weight: bold;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            border: none;
        }
        .stButton>button:first-child:hover {
            background-color: #B91C1C; /* Red 700 */
            transform: scale(1.02);
        }
        /* Style for the list buttons to look like clickable cards */
        .incident-card-button button {
            background-color: #1E293B; /* Slate 800 */
            color: white;
            text-align: left;
            border: none;
            border-left: 5px solid #64748B;
            border-radius: 8px;
            width: 100%;
            margin-bottom: 8px;
            padding: 15px;
            transition: background-color 0.2s;
        }
        .incident-card-button button:hover {
            background-color: #334155; /* Slate 700 */
            border-left-color: #4CAF50; /* Green highlight on hover */
        }
        </style>
        """, unsafe_allow_html=True)

# Generate a mock incident for demonstration
def generate_incident(incident_type, location, score):
    return {
        'id': str(uuid4())[:8],
        'type': incident_type,
        'location': location,
        'status': 'New',
        'timestamp': datetime.now(),
        'deescalation_score': score,
        'notifications_sent': 0,
        'wellness_required': 2,
        'description': f"Deep Learning Model detected **{incident_type}** at {location} with {score}% confidence.",
        'notification_log': []
    }

def send_alert_email(incident_details):
    """
    Placeholder function to simulate sending a real-time email alert.
    """
    try:
        RECIPIENT_EMAIL = "security@university.edu"
        # We only simulate the successful logging of the email here
        st.success(f"EMAIL ALERT SENT successfully to {RECIPIENT_EMAIL} for Incident {incident_details['id']}!")
    except Exception as e:
        st.error(f"Simulated email failure: Could not connect to SMTP server. Error: {e}")
        
    incident_details['notification_log'].append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'recipient': 'Email Alert System'
    })

# --- Streamlit-Webrtc Real-Time Processor ---

# This class simulates the Deep Learning model running on each frame.
class RealTimeDetector(VideoProcessorBase):
    def __init__(self):
        self.violence_score = 0
        self.frame_counter = 0
        self.detection_triggered = False

    def recv(self, frame):
        # Convert the frame to a NumPy array for OpenCV/DL simulation
        img = frame.to_ndarray(format="bgr")
        
        # --- SIMULATED DEEP LEARNING LOGIC ---
        if self.frame_counter < 100:
            self.violence_score = min(100, self.frame_counter)
            self.frame_counter += 1

        # Check for VIOLENCE THRESHOLD
        if self.violence_score >= 90 and not self.detection_triggered:
            # Set the global state flag to trigger the incident logging in main()
            if 'violation_detected' not in st.session_state or not st.session_state.violation_detected:
                st.session_state.violation_detected = True
            
            # Draw a bounding box (simulating detection)
            cv2.rectangle(img, (200, 150), (450, 350), (0, 0, 255), 5) # Red box
            cv2.putText(img, "VIOLENCE DETECTED!", (200, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            self.detection_triggered = True

        elif self.detection_triggered:
            # Continue drawing box after detection
            cv2.rectangle(img, (200, 150), (450, 350), (0, 0, 255), 5) 
            cv2.putText(img, "ALERT ACTIVE!", (200, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        else:
            # Normal scanning state
            cv2.putText(img, f"Scanning... ({self.violence_score}%)", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return img

# --- State Initialization (remains unchanged) ---
def initialize_state():
    if 'incidents' not in st.session_state:
        st.session_state.incidents = []
        
    if 'active_incident_id' not in st.session_state:
        st.session_state.active_incident_id = None
        
    if 'risk_zones' not in st.session_state:
        st.session_state.risk_zones = [
            {'location': 'Cafeteria Exit', 'score': 92, 'trend': 'up'},
            {'location': 'Back Parking Lot', 'score': 85, 'trend': 'up'},
            {'location': '4th Floor Hallway', 'score': 65, 'trend': 'down'},
        ]
        
    if 'violation_detected' not in st.session_state:
        st.session_state.violation_detected = False
        
    if 'email_sent_for_last_detection' not in st.session_state:
        st.session_state.email_sent_for_last_detection = False
        
# --- Incident List Panel (remains unchanged) ---
def incident_list_panel():
    st.subheader("🚨 Recent Incidents")
    st.caption("Click an incident to view details and manage response.")

    sorted_incidents = sorted(
        st.session_state.incidents,
        key=lambda x: (x['status'] != 'New', x['timestamp']),
        reverse=True
    )
    
    if not sorted_incidents:
        st.info("No active incidents detected. Start the real-time feed!")
        return

    for incident in sorted_incidents:
        status_color = {'New': '#DC2626', 'Investigating': '#F59E0B', 'Resolved': '#10B981', 'Closed': '#3B82F6'}
        
        with st.container(border=False):
            button_label = f"{incident['type']} at {incident['location']} ({incident['status']})"
            
            st.markdown(f'<div class="incident-card-button" style="border-left: 5px solid {status_color.get(incident["status"], "#64748B")};">', unsafe_allow_html=True)
            if st.button(
                button_label, 
                key=f"select_{incident['id']}", 
                help="View Details", 
                use_container_width=True
            ):
                 st.session_state.active_incident_id = incident['id']
                 st.rerun() 
            st.markdown('</div>', unsafe_allow_html=True)

# --- Incident Detail Panel Handlers (remains unchanged) ---

def handle_update(incident_id, key, value):
    for incident in st.session_state.incidents:
        if incident['id'] == incident_id:
            incident[key] = value
            break
    st.session_state.active_incident_id = None 
    st.session_state.active_incident_id = incident_id
    st.rerun() 

def send_notification_action(incident_id):
    for incident in st.session_state.incidents:
        if incident['id'] == incident_id:
            incident['notifications_sent'] += 1
            recipient = 'Admin/Security' if incident['notifications_sent'] == 1 else 'Parents/Counselors'
            incident['notification_log'].append({
                'time': datetime.now().strftime('%H:%M:%S'),
                'recipient': recipient
            })
            st.toast(f"Notification sent to {recipient} for Incident {incident_id}!", icon="🔔")
            break
    st.rerun() 

def incident_detail_panel():
    incident_id = st.session_state.active_incident_id
    if not incident_id:
        st.subheader("Incident Details")
        st.info("Select an incident from the left panel to view details and manage the response.")
        return

    incident = next((i for i in st.session_state.incidents if i['id'] == incident_id), None)
    if not incident:
        st.error("Incident not found.")
        st.session_state.active_incident_id = None
        st.rerun() 
        return

    st.subheader(f"Incident {incident['id']} | {incident['type']}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Location", incident['location'])
    col2.metric("Time Detected", incident['timestamp'].strftime('%H:%M:%S'))
    col3.metric("Detection Confidence", f"{incident['deescalation_score']}%", delta="Confirmed")

    st.markdown("---")
    
    st.markdown(f"**AI Description:** *{incident['description']}*")
    
    st.markdown("---")

    st.markdown("### 🛠️ Response Actions")
    
    colA, colB = st.columns([1, 2])
    
    with colA:
        status_options = ['New', 'Investigating', 'Resolved', 'Closed']
        current_index = status_options.index(incident['status'])
        
        st.selectbox(
            "Update Status",
            status_options,
            index=current_index,
            key=f"status_{incident_id}",
            on_change=lambda: handle_update(incident_id, 'status', st.session_state[f"status_{incident_id}"])
        )
    
    with colB:
        st.markdown("<p style='font-weight: bold; margin-bottom: -5px;'>Immediate Notifications</p>", unsafe_allow_html=True)
        st.button(
            f"🔔 Send Tactical Alert ({incident['notifications_sent']} Sent)", 
            key=f"send_alert_{incident_id}", 
            on_click=send_notification_action, 
            args=[incident_id]
        )
        if incident['notifications_sent'] > 0:
            st.caption(f"Last sent to {incident['notification_log'][-1]['recipient']} at {incident['notification_log'][-1]['time']}")
        
    st.markdown("---")
    
    st.markdown("### ❤️ Follow-up & Support Protocols")
    
    colC, colD = st.columns(2)
    
    with colC:
        st.info(f"**Wellness Checks Required:** {incident['wellness_required']}")
        
        if incident['wellness_required'] > 0:
            st.button("Launch Confidential Check-in Protocol", key=f"wellness_{incident_id}")
            st.caption("Routes victims/witnesses to counseling resources.")

    with colD:
        st.warning("Notification Log")
        log_text = "\n".join([f"**[{entry['time']}]** - Sent to {entry['recipient']}" for entry in incident['notification_log']])
        if log_text:
            st.markdown(log_text)
        else:
            st.markdown("*No alerts logged yet.*")

def proactive_panel():
    st.subheader("🛡️ Proactive De-escalation Zones")
    st.caption("AI-driven risk assessment based on behavioral and environmental data.")

    for zone in st.session_state.risk_zones:
        with st.container(border=True):
            st.markdown(f"#### {zone['location']}")
            
            metric_delta_color = 'inverse' if zone['trend'] == 'up' else 'normal'

            c1, c2 = st.columns([2, 1])
            
            with c1:
                st.metric("Risk Score", f"{zone['score']}%", 
                          delta=zone['trend'].capitalize(), 
                          delta_color=metric_delta_color)
            
            with c2:
                action = "Deploy staff immediately" if zone['score'] > 90 else "Increase casual presence"
                text_color_style = 'color: #DC2626;' if zone['score'] > 90 else 'color: #F59E0B;'
                
                st.markdown(f"**Recommendation:**\n<span style='{text_color_style} font-weight: bold;'>{action}</span>", unsafe_allow_html=True)

# --- NEW FILE ANALYSIS FUNCTIONS ---

def process_uploaded_image(uploaded_file):
    st.markdown("### Image Analysis Result")
    
    # Read image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    # Simulated Detection Logic for Image
    simulated_violence_score = random.randint(70, 100)
    
    if simulated_violence_score >= 80:
        # Draw bounding box and text annotation
        cv2.rectangle(img, (100, 100), (500, 400), (0, 0, 255), 5)
        cv2.putText(img, "VIOLENCE DETECTED (95%)", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        st.error(f"🚨 **VIOLATION DETECTED!** Confidence: {simulated_violence_score}%")
        
        if st.button("Log Incident and Send Alert", key="log_image_incident"):
            new_incident = generate_incident(
                incident_type="Image Upload Violence", 
                location=f"File: {uploaded_file.name}", 
                score=simulated_violence_score
            )
            st.session_state.incidents.append(new_incident)
            st.session_state.active_incident_id = new_incident['id']
            send_alert_email(new_incident)
            st.toast("File incident logged and alert sent!", icon="✅")
            st.rerun()
    else:
        st.success(f"✅ No Violation Detected. Confidence: {simulated_violence_score}%")
        
    # FIX: Replaced deprecated use_column_width with use_container_width
    st.image(img, channels="BGR", use_container_width=True) 

def process_uploaded_video(uploaded_file):
    st.markdown("### Video Analysis")
    
    # Display video player
    st.video(uploaded_file)
    
    # Button to initiate analysis (simulating background processing)
    if st.button("Run Full Video Detection Analysis", key="run_video_analysis"):
        
        with st.spinner('Analyzing video footage for violent activity... This may take a few seconds...'):
            time.sleep(3) # Simulate processing time

        simulated_violence_score = random.randint(85, 99)
        
        if simulated_violence_score >= 85:
            st.error(f"🚨 **VIOLATION DETECTED in Video!** Confidence: {simulated_violence_score}%")
            
            # Log and alert
            new_incident = generate_incident(
                incident_type="Video Footage Violence", 
                location=f"Video: {uploaded_file.name}", 
                score=simulated_violence_score
            )
            st.session_state.incidents.append(new_incident)
            st.session_state.active_incident_id = new_incident['id']
            send_alert_email(new_incident)
            st.toast("Video incident logged and alert sent!", icon="✅")
            st.rerun()
        else:
            st.success(f"✅ No Significant Violation Detected in video. Confidence: {simulated_violence_score}%")

def file_analysis_panel():
    st.subheader("Upload Static Footage for Analysis")
    st.caption("Supports Image (.jpg, .png) and Video (.mp4, .mov) file uploads for retroactive analysis.")

    uploaded_file = st.file_uploader(
        "Upload a file", 
        type=["mp4", "mov", "jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        file_type = uploaded_file.type.split('/')[0]
        
        if file_type == 'image':
            process_uploaded_image(uploaded_file)
        
        elif file_type == 'video':
            process_uploaded_video(uploaded_file)
        
        else:
            st.warning("Unsupported file type detected.")

# --- Main Application Logic ---

def main():
    set_styles()
    initialize_state()

    st.title("🛡️ Real-Time Campus Safety Detection")
    st.caption("Deep Learning integration with real-time alerts and incident management.")
    
    st.markdown("---")

    # Check for detection trigger flag set by the RealTimeDetector class (for live feed)
    if st.session_state.violation_detected and not st.session_state.email_sent_for_last_detection:
        new_incident = generate_incident(
            incident_type="Confirmed Live Violence", 
            location="Live Camera Feed", 
            score=95
        )
        st.session_state.incidents.append(new_incident)
        st.session_state.active_incident_id = new_incident['id']
        
        send_alert_email(new_incident)
        
        st.session_state.email_sent_for_last_detection = True
        st.session_state.violation_detected = False
        
        st.toast("🔥 Real-Time VIOLENCE ALERT! Incident Logged.", icon="🚨")
        st.rerun() 


    # Main two-column layout
    col1, col2 = st.columns([1, 2])

    # Left Column: Incident List
    with col1:
        incident_list_panel()

    # Right Column: Tabs for Detection and Proactive System
    with col2:
        tab1, tab2, tab3 = st.tabs([" Real-Time Video Feed", " File Analysis", " Proactive Risk Management"])
        
        with tab1:
            st.subheader("Live Deep Learning Feed")
            st.warning("Note: Your camera will start automatically when this tab is selected.")
            
            webrtc_ctx = webrtc_streamer(
                key="real-time-detector",
                video_processor_factory=RealTimeDetector,
                rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
                media_stream_constraints={"video": True, "audio": False},
            )
            
            if webrtc_ctx.video_processor:
                status = "VIOLATION DETECTED!" if webrtc_ctx.video_processor.detection_triggered else f"Simulated Score: {webrtc_ctx.video_processor.violence_score}%"
                
                if webrtc_ctx.video_processor.detection_triggered:
                    st.error(f"🔴 {status}", icon="‼️")
                else:
                    st.info(f"🟢 Scanning... {status}", icon="🔍")

        with tab2:
            file_analysis_panel()
            
        with tab3:
            proactive_panel()
            
    # Auto-refresh mechanism (simulates real-time updates)
    time.sleep(1)
    st.rerun()


if __name__ == "__main__":
    main()
