import cv2
import mediapipe as mp
import time

def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("No se pudo acceder a la camara .")
        return

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        model_complexity=0,              # modelo más rápido
        min_detection_confidence=0.8,
        min_tracking_confidence=0.8
    )
    mp_draw = mp.solutions.drawing_utils

    prev_time = time.time()
    prev_pos = None
    movement_text = ""
    frame_count = 0

    while True:
        cap.grab()  # evita acumulación de frames en buffer
        ret, frame = cap.retrieve()
        if not ret:
            continue

        frame_count += 1
        frame = cv2.flip(frame, 1)

        # Procesar solo 1 de cada 2 frames (reduce lag sin perder fluidez)
        if frame_count % 2 == 0:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    landmarks = hand_landmarks.landmark

                    # --- DETECCIÓN DE PUÑO ---
                    fingers = [(landmarks[i].y < landmarks[i - 2].y) for i in [8, 12, 16, 20]]
                    thumb = landmarks[4].x < landmarks[3].x
                    is_fist = (not any(fingers)) and (not thumb)

                    if is_fist:
                        # Calcular el centro de la mano
                        cx = int((landmarks[5].x + landmarks[17].x) / 2 * frame.shape[1])
                        cy = int((landmarks[5].y + landmarks[17].y) / 2 * frame.shape[0])
                        cv2.circle(frame, (cx, cy), 6, (0, 255, 255), -1)

                        # Detectar movimiento
                        if prev_pos:
                            dx, dy = cx - prev_pos[0], cy - prev_pos[1]
                            threshold = 15
                            if abs(dx) > abs(dy):
                                if dx > threshold:
                                    movement_text = "Derecha"
                                elif dx < -threshold:
                                    movement_text = "Izquierda"
                            else:
                                if dy > threshold:
                                    movement_text = "Abajo"
                                elif dy < -threshold:
                                    movement_text = "Arriba"
                                else:
                                    movement_text = ""
                        prev_pos = (cx, cy)

                        # Dibuja el rectángulo del puño
                        h, w, _ = frame.shape
                        x_min = int(min([lm.x for lm in landmarks]) * w)
                        y_min = int(min([lm.y for lm in landmarks]) * h)
                        x_max = int(max([lm.x for lm in landmarks]) * w)
                        y_max = int(max([lm.y for lm in landmarks]) * h)
                        cv2.rectangle(frame, (x_min + 30, y_min + 40),
                                      (x_max - 30, y_max - 40), (255, 0, 0), 3)
                    else:
                        movement_text = ""
                        prev_pos = None

        # Mostrar FPS y dirección
        current_time = time.time()
        time_diff = current_time - prev_time
        fps = int(1 / time_diff) if time_diff > 0 else 0
        prev_time = current_time

        cv2.putText(frame, f"FPS: {fps}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"{movement_text}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)

        cv2.imshow("Deteccion de movimiento de puno", frame)

        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
