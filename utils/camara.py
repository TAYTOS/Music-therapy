import cv2
import mediapipe as mp
import numpy as np

class Camara:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1, 
            model_complexity=0,
            min_detection_confidence=0.7, 
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Estilos de dibujo personalizados
        self.drawing_styles = mp.solutions.drawing_styles

    def obtener_frame(self, cap):
        """Captura frame, detecta la mano y devuelve si es puño y la posición"""
        ret, frame = cap.read()
        if not ret:
            print("Error: no se pudo leer frame del stream.")
            return None, False, (None, None)

        # Voltear horizontalmente para efecto espejo
        frame = cv2.flip(frame, 1)
        
        # Convertir a RGB para MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        is_fist = False
        cx, cy = None, None

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Dibujar landmarks de la mano con estilo mejorado
                self.mp_draw.draw_landmarks(
                    frame, 
                    hand_landmarks, 
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                    self.mp_draw.DrawingSpec(color=(255, 255, 255), thickness=2)
                )
                
                landmarks = hand_landmarks.landmark
                h, w, _ = frame.shape

                # Detectar si los dedos están cerrados (puño)
                # Verificar dedos índice, medio, anular y meñique
                fingers_closed = [
                    landmarks[8].y > landmarks[6].y,   # Índice
                    landmarks[12].y > landmarks[10].y, # Medio
                    landmarks[16].y > landmarks[14].y, # Anular
                    landmarks[20].y > landmarks[18].y  # Meñique
                ]
                
                # Verificar pulgar
                thumb_closed = abs(landmarks[4].x - landmarks[3].x) < 0.05

                # Es puño si todos los dedos están cerrados
                is_fist = all(fingers_closed) and thumb_closed

                # Calcular centro de la mano (entre muñeca y centro de la palma)
                cx = int((landmarks[0].x + landmarks[9].x) / 2 * w)
                cy = int((landmarks[0].y + landmarks[9].y) / 2 * h)

                # Dibujar indicador visual de puño
                if is_fist:
                    cv2.putText(frame, "PUÑO CERRADO", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                else:
                    cv2.putText(frame, "Cierra el puño", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)

        return frame, is_fist, (cx, cy)