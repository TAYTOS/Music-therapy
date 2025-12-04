import mediapipe as mp
import cv2


class HandDetector:
    def __init__(self, max_hands=1, detection_confidence=0.7):
        self.hands_module = mp.solutions.hands
        self.hands = self.hands_module.Hands(
            max_num_hands=max_hands, min_detection_confidence=detection_confidence
        )
        self.drawer = mp.solutions.drawing_utils

    def detectar_mano(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.drawer.draw_landmarks(
                    frame, hand_landmarks, self.hands_module.HAND_CONNECTIONS
                )
                return hand_landmarks
        return None

    def detectar_puno(self, landmarks, frame):
        h, w, _ = frame.shape
        puntos = [(int(p.x * w), int(p.y * h)) for p in landmarks.landmark]
        dedos = [8, 12, 16, 20]
        abierto = 0

        for d in dedos:
            if puntos[d][1] < puntos[d - 2][1]:
                abierto += 1
        if abierto == 0:
            return True
        return False
