# ai_models.py (SIMULATED FOR RENDER DEPLOYMENT - NO TENSORFLOW/NUMPY)
import random
import os # Keep this for os.path.exists if needed, but analyze_image won't use it directly

class AutismDetectionAI:
    def __init__(self):
        self.weights = {
            'eye_contact': 0.15,
            'social_interaction': 0.15,
            'repetitive_behavior': 0.1,
            'delayed_speech': 0.1,
            'echolalia': 0.1,
            'sound_sensitivity': 0.1,
            'touch_sensitivity': 0.1,
            'emotional_regulation': 0.1,
            'change_resistance': 0.1,
            'aggression': 0.1
        }
        self.image_weight = 0.3
        # REMOVED: self.model = tf.keras.models.load_model('multi_output_model_finetune_focal.h5')
        # No actual model loading for this rapid deployment test
        pass

    def analyze_image(self, image_path):
        # SIMULATE image analysis if an image path is provided
        if image_path:
            image_score = random.uniform(0, 1) # Return random score between 0 and 1
            meltdown_prob = random.uniform(0, 0.5) # Simulate a meltdown probability
            print(f"Debug: Image Analysis - Simulated Image Score: {image_score * 100}%, Simulated Meltdown Prob: {meltdown_prob * 100}%")
            return image_score, meltdown_prob
        return 0, 0 # If no image path

    def predict_symptom_score(self, symptoms):
        score = 0
        for symptom, weight in self.weights.items():
            if symptoms.get(symptom, False):
                score += weight
        print(f"Debug: Symptom Score Calculation - Symptoms: {symptoms}, Score: {score * 100}")
        return score * 100

    def adjust_for_user_info(self, symptom_score, user_info):
        adjustment = 0
        age = user_info.get('age', 0)
        gender = user_info.get('gender', 'unknown')

        if age < 3:
            adjustment += 10
        elif age >= 12:
            adjustment -= 5

        if gender == 'male':
            adjustment += 5

        adjusted_score = min(100, max(0, symptom_score + adjustment))
        return adjusted_score

    def get_risk_level(self, combined_score):
        if combined_score >= 70:
            return "High Risk"
        elif combined_score >= 40:
            return "Moderate Risk"
        else:
            return "Low Risk"

    def get_combined_prediction(self, symptoms, user_info, image_path=None):
        symptom_score = self.predict_symptom_score(symptoms)
        image_score, meltdown_prob = self.analyze_image(image_path)

        adjusted_symptom_score = self.adjust_for_user_info(symptom_score, user_info)

        if image_score > 0: # Only factor in image score if an image was provided
            combined_score = (1 - self.image_weight) * adjusted_symptom_score + self.image_weight * image_score * 100
        else:
            combined_score = adjusted_symptom_score

        risk_level = self.get_risk_level(combined_score)
        return combined_score, risk_level, adjusted_symptom_score, image_score * 100, meltdown_prob