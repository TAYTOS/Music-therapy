import cv2
import mediapipe as mp

# Inicializar soluciones de MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Captura de la cámara
cap = cv2.VideoCapture(0)

# Configurar MediaPipe Hands
with mp_hands.Hands(
    max_num_hands=2,                # Detectar hasta 2 manos
    min_detection_confidence=0.7,   # Umbral de confianza
    min_tracking_confidence=0.7
) as hands:

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convertir a RGB (MediaPipe usa RGB, no BGR)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Procesar el frame
        result = hands.process(rgb)

        # Dibujar landmarks si encuentra manos
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

        # Mostrar la imagen con tracking
        cv2.imshow("Hand Tracking", frame)

        # Salir con ESC
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
