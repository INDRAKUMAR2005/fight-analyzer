import time

class ActionRecognizer:
    def __init__(self):
        self.state = "idle"
        self.last_action_time = 0
        self.action_cooldown = 1.0 # seconds
        
    def detect_move(self, lm_list, elbow_angle_l, elbow_angle_r, shoulder_angle_l, shoulder_angle_r):
        """
        Rule-based detection for Jab and Cross.
        Assuming user is facing the camera in an orthodox stance.
        Jab = Left hand fast extension
        Cross = Right hand fast extension
        """
        current_time = time.time()
        
        if not lm_list or len(lm_list) < 33:
            return "idle"

        if current_time - self.last_action_time < self.action_cooldown:
            return self.state

        # Landmark indices (MediaPipe)
        # Left wrist: 15, Right wrist: 16
        # Left shoulder: 11, Right shoulder: 12
        try:
            _, lw_x, lw_y, _, _ = lm_list[15]
            _, rw_x, rw_y, _, _ = lm_list[16]
            _, ls_x, _, _, _ = lm_list[11]
            _, rs_x, _, _, _ = lm_list[12]
        except IndexError:
            return "idle"

        # Heuristic: If elbow angle > 150 (extended) and arm is raised
        # For Jab (Left hand) - we use 140 to be more forgiving in MVP
        if elbow_angle_l > 140: 
            if shoulder_angle_l > 60: # Arm is somewhat raised
                 self.state = "Jab"
                 self.last_action_time = current_time
                 return self.state
        elif 70 < elbow_angle_l < 120:
            if shoulder_angle_l > 60:
                 self.state = "Left Hook"
                 self.last_action_time = current_time
                 return self.state
                 
        # For Right Hand (Cross and Right Hook)
        if elbow_angle_r > 140:
            if shoulder_angle_r > 60:
                 self.state = "Cross"
                 self.last_action_time = current_time
                 return self.state
        elif 70 < elbow_angle_r < 120:
            if shoulder_angle_r > 60:
                 self.state = "Right Hook"
                 self.last_action_time = current_time
                 return self.state

        # For Uppercuts (Heuristic: Elbow bent + wrist moving up)
        try:
            _, lw_y = lm_list[15][2], lm_list[15][2] # Using index 2 for y
            _, rw_y = lm_list[16][2], lm_list[16][2]
            _, le_y = lm_list[13][2], lm_list[13][2]
            _, re_y = lm_list[14][2], lm_list[14][2]
            
            # Left Uppercut
            if 60 < elbow_angle_l < 110:
                if lm_list[15][2] < lm_list[13][2] - 20: # Wrist above elbow
                    self.state = "Left Uppercut"
                    self.last_action_time = current_time
                    return self.state
            
            # Right Uppercut
            if 60 < elbow_angle_r < 110:
                if lm_list[16][2] < lm_list[14][2] - 20: # Wrist above elbow
                    self.state = "Right Uppercut"
                    self.last_action_time = current_time
                    return self.state
        except (IndexError, TypeError):
            pass

        # Reset state after a while
        if current_time - self.last_action_time > 1.5:
            self.state = "idle"
            
        return self.state
