import cv2
import time
import streamlit as st
from core.pose_module import PoseDetector
from core.action_recognition import ActionRecognizer
from core.biomechanics import BiomechanicsAnalyzer

st.set_page_config(page_title="Fight Analyzer MVP", layout="wide", page_icon="🥊")

st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    h1 {
        color: #00ffcc;
        text-shadow: 2px 2px 4px #000000;
    }
    h3 {
        color: #ff0055 !important;
    }
    hr {
        border-color: #333333;
    }
</style>
""", unsafe_allow_html=True)

st.title("🥊 Fight Analyzer Dashboard")
st.markdown("*Real-time pose tracking → action recognition → biomechanics feedback.*")

col1, col2 = st.columns([2.5, 1.5])

with col1:
    st.subheader("Live Feed")
    
    input_source = st.selectbox("Select Input Source", ["Webcam (Default)", "Webcam (Index 1)", "Webcam (Index 2)", "Video File"])
    
    video_path = None
    if input_source == "Video File":
        uploaded_file = st.file_uploader("Upload a video", type=["mp4", "mov", "avi"])
        if uploaded_file is not None:
            import tempfile
            tfile = tempfile.NamedTemporaryFile(delete=False) 
            tfile.write(uploaded_file.read())
            video_path = tfile.name

    run_detection = st.checkbox("Start Analysis")
    FRAME_WINDOW = st.image([])

with col2:
    st.markdown("### Key Metrics")
    st.markdown("---")
    m1, m2 = st.columns(2)
    with m1:
        action_placeholder = st.empty()
    with m2:
        fps_placeholder = st.empty()
        
    st.markdown("### Correction Engine")
    st.markdown("---")
    feedback_placeholder = st.empty()

detector = PoseDetector()
recognizer = ActionRecognizer()
analyzer = BiomechanicsAnalyzer()

if run_detection:
    if input_source == "Webcam (Default)":
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    elif input_source == "Webcam (Index 1)":
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    elif input_source == "Webcam (Index 2)":
        cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)
    elif input_source == "Video File" and video_path is not None:
        cap = cv2.VideoCapture(video_path)
    else:
        st.warning("Please select a camera or upload a video.")
        st.stop()
    p_time = 0
    current_action = "idle"
    feedback_msgs = []
    feedback_time = 0

    while cap.isOpened() and run_detection:
        success, img = cap.read()
        if not success:
            if input_source != "Video File":
                st.warning("Failed to grab user webcam. Ensure you have given permission and no other app is using it.")
            else:
                st.info("Video processing complete.")
            break
        
        img = cv2.flip(img, 1) # Mirror

        # 1. Pose Estimation
        img = detector.find_pose(img, draw=False)
        lm_list = detector.find_position(img, draw=False)
        
        if len(lm_list) != 0:
            # Angles
            elbow_angle_l = detector.find_angle(img, lm_list, 11, 13, 15, draw=True)
            shoulder_angle_l = detector.find_angle(img, lm_list, 23, 11, 13, draw=False)
            
            elbow_angle_r = detector.find_angle(img, lm_list, 12, 14, 16, draw=True)
            shoulder_angle_r = detector.find_angle(img, lm_list, 24, 12, 14, draw=False)
            
            # Action Recognition
            action = recognizer.detect_move(
                lm_list, 
                elbow_angle_l, elbow_angle_r, 
                shoulder_angle_l, shoulder_angle_r
            )
            
            # Biomechanics
            if action != "idle" and action != current_action:
                current_action = action
                angles_dict = {
                    'elbow_l': elbow_angle_l,
                    'elbow_r': elbow_angle_r,
                    'shoulder_l': shoulder_angle_l,
                    'shoulder_r': shoulder_angle_r
                }
                feedback_msgs = analyzer.analyze(action, angles_dict)
                feedback_time = time.time()
                
        # Clear feedback
        if time.time() - feedback_time > 2.0:
            current_action = "idle"
            feedback_msgs = []

        # FPS
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time
        
        # Display Info (Sidebar info update)
        action_placeholder.metric(label="Current Action", value=current_action)
        fps_placeholder.metric(label="System FPS", value=int(fps))
        
        # Display Text Feedback natively in Streamlit
        feedback_md = ""
        if feedback_msgs:
            for msg in feedback_msgs:
                if "Great" in msg:
                    feedback_md += f"<div style='background-color:#0f5132; color:#75b798; padding:10px; border-radius:5px; margin-bottom:10px; font-weight:bold;'>✅ {msg}</div>"
                else:
                    feedback_md += f"<div style='background-color:#842029; color:#ea868f; padding:10px; border-radius:5px; margin-bottom:10px; font-weight:bold;'>⚠️ {msg}</div>"
        else:
            feedback_md = "<div style='color:#6c757d; font-style:italic; padding:10px;'>Awaiting movement validation...</div>"
            
        feedback_placeholder.markdown(feedback_md, unsafe_allow_html=True)
        
        # Convert BGR to RGB for Streamlit rendering
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        FRAME_WINDOW.image(img)

    cap.release()
else:
    st.write("Configured input and click 'Start Analysis' to begin.")
