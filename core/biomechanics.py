class BiomechanicsAnalyzer:
    def __init__(self):
        # Ideal ranges for movements
        # e.g., elbow should be nearly fully extended (150-180 degrees)
        self.ideal_ranges = {
            "Jab": {
                "elbow_angle": (155, 180),
                "shoulder_angle": (75, 110)
            },
            "Cross": {
                "elbow_angle": (155, 180),
                "shoulder_angle": (75, 110)
            },
            "Left Hook": {
                "elbow_angle": (80, 110),
                "shoulder_angle": (75, 110)
            },
            "Right Hook": {
                "elbow_angle": (80, 110),
                "shoulder_angle": (75, 110)
            },
            "Left Uppercut": {
                "elbow_angle": (70, 110),
                "shoulder_angle": (40, 90)
            },
            "Right Uppercut": {
                "elbow_angle": (70, 110),
                "shoulder_angle": (40, 90)
            }
        }

    def analyze(self, action, angles):
        """
        Analyzes the form of the action.
        """
        feedback = []
        
        if action not in self.ideal_ranges:
            return feedback

        ideal = self.ideal_ranges[action]
        
        if action == "Jab":
            elbow = angles.get('elbow_l', 0)
            shoulder = angles.get('shoulder_l', 0)
            
            if elbow < ideal['elbow_angle'][0]:
                feedback.append("Jab: Extend your arm fully for more reach.")
            elif elbow > ideal['elbow_angle'][1]:
                feedback.append("Jab: Don't hyper-extend your elbow.")
                
            if shoulder < ideal['shoulder_angle'][0]:
                feedback.append("Jab: Keep your shoulder up to protect your chin.")
                
        elif action == "Cross":
            elbow = angles.get('elbow_r', 0)
            shoulder = angles.get('shoulder_r', 0)
            
            if elbow < ideal['elbow_angle'][0]:
                feedback.append("Cross: Extend right arm fully on the punch.")
            if shoulder < ideal['shoulder_angle'][0]:
                feedback.append("Cross: Keep shoulder up while punching.")
                
        elif action in ["Left Hook", "Right Hook"]:
            prefix = action.split()[0]
            elbow = angles.get('elbow_l' if prefix == "Left" else 'elbow_r', 0)
            shoulder = angles.get('shoulder_l' if prefix == "Left" else 'shoulder_r', 0)
            
            if elbow < ideal['elbow_angle'][0]:
                feedback.append(f"{action}: Open your elbow a bit more (aim for ~90 degrees).")
            elif elbow > ideal['elbow_angle'][1]:
                feedback.append(f"{action}: Keep elbow bent tighter for a powerful hook.")
            
            if shoulder < ideal['shoulder_angle'][0]:
                feedback.append(f"{action}: Keep your shoulder high to protect your chin.")

        elif action in ["Left Uppercut", "Right Uppercut"]:
            prefix = action.split()[0]
            elbow = angles.get('elbow_l' if prefix == "Left" else 'elbow_r', 0)
            shoulder = angles.get('shoulder_l' if prefix == "Left" else 'shoulder_r', 0)
            
            if elbow < ideal['elbow_angle'][0]:
                feedback.append(f"{action}: Don't cramp your elbow; aim for a ~90 degree bend.")
            elif elbow > ideal['elbow_angle'][1]:
                feedback.append(f"{action}: Keep the elbow bent for a tighter, more powerful drive.")
            
            if shoulder < ideal['shoulder_angle'][0]:
                 feedback.append(f"{action}: Drop your hips but keep your shoulder rotation engaged.")

        # Suggestion: Great form if no corrections
        if not feedback:
            feedback.append(f"Great {action} form!")
            
        return feedback
