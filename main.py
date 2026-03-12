import cv2
import time
from core.pose_module import PoseDetector
from core.action_recognition import ActionRecognizer
from core.biomechanics import BiomechanicsAnalyzer

def main():
    cap = cv2.VideoCapture(0)
    # If webcam fails, the user can try a video file:
    # cap = cv2.VideoCapture("video.mp4")
    
    detector = PoseDetector()
    recognizer = ActionRecognizer()
    analyzer = BiomechanicsAnalyzer()

    p_time = 0
    
    current_action = "idle"
    feedback_msgs = []
    feedback_time = 0

    print("Starting Fight Analyzer...")
    
    while True:
        success, img = cap.read()
        if not success:
            print("Failed to grab frame. Is the webcam connected?")
            break

        img = cv2.flip(img, 1) # Mirror image
        
        # 1. Pose Estimation
        img = detector.find_pose(img, draw=False)
        lm_list = detector.find_position(img, draw=False)
        
        if len(lm_list) != 0:
            # 2. Extract Key Angles
            
            # Left arm (Hip: 23, Shoulder: 11, Elbow: 13, Wrist: 15)
            elbow_angle_l = detector.find_angle(img, lm_list, 11, 13, 15, draw=True)
            shoulder_angle_l = detector.find_angle(img, lm_list, 23, 11, 13, draw=False)
            
            # Right arm (Hip: 24, Shoulder: 12, Elbow: 14, Wrist: 16)
            elbow_angle_r = detector.find_angle(img, lm_list, 12, 14, 16, draw=True)
            shoulder_angle_r = detector.find_angle(img, lm_list, 24, 12, 14, draw=False)
            
            # 3. Action Recognition
            action = recognizer.detect_move(
                lm_list, 
                elbow_angle_l, elbow_angle_r, 
                shoulder_angle_l, shoulder_angle_r
            )
            
            # If a new action is detected, run biomechanics
            if action != "idle" and action != current_action:
                current_action = action
                angles_dict = {
                    'elbow_l': elbow_angle_l,
                    'elbow_r': elbow_angle_r,
                    'shoulder_l': shoulder_angle_l,
                    'shoulder_r': shoulder_angle_r
                }
                # 4. Biomechanics Analysis
                feedback_msgs = analyzer.analyze(action, angles_dict)
                feedback_time = time.time()
                
        # Clear feedback after 2 seconds
        if time.time() - feedback_time > 2.0:
            current_action = "idle"
            feedback_msgs = []

        # FPS Calculation
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time
        
        # Display Info
        cv2.putText(img, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        cv2.putText(img, f'Action: {current_action}', (10, 70), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 0), 2)
        
        y_offset = 110
        for msg in feedback_msgs:
            # Red color if it's a correction, green if it's praise
            color = (0, 255, 0) if "Great" in msg else (0, 0, 255)
            cv2.putText(img, msg, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_offset += 30

        cv2.imshow("Fight Analyzer MVP", img)
        
        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
