import cv2
import numpy as np

class Vista:
    def __init__(self):
        self.colores = {
            'fondo_panel': (20, 20, 40),
            'texto_principal': (255, 255, 255),
            'texto_score': (0, 255, 100),
            'texto_tiempo': (100, 200, 255),
            'borde': (100, 100, 200)
        }

    def dibujar_interfaz(self, frame, score, tiempo_restante, estado, num_puntos):
        """Dibuja la interfaz del juego sobre el frame"""
        h, w, _ = frame.shape
        
        # Crear overlay semi-transparente para el panel superior
        overlay = frame.copy()
        
        # Panel superior con información
        cv2.rectangle(overlay, (0, 0), (w, 100), (30, 30, 60), -1)
        frame = cv2.addWeighted(frame, 0.6, overlay, 0.4, 0)
        
        # Puntaje
        cv2.putText(frame, f"Puntaje: {score}", (20, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, self.colores['texto_score'], 3)
        
        # Tiempo restante con color dinámico
        if tiempo_restante > 15:
            color_tiempo = (0, 255, 0)
        elif tiempo_restante > 5:
            color_tiempo = (0, 255, 255)
        else:
            color_tiempo = (0, 0, 255)
            
        cv2.putText(frame, f"Tiempo: {tiempo_restante}s", (w - 280, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, color_tiempo, 3)
        
        # Instrucciones según el estado
        instrucciones = {
            "esperando": "Coloca tu puno cerrado en el circulo verde",
            "completado": "Patron completado",
            "fallido": "Tiempo agotado. Intenta completar todo el patron"
        }
        
        texto_estado = instrucciones.get(estado, "")
        
        # Panel inferior con instrucciones
        overlay2 = frame.copy()
        cv2.rectangle(overlay2, (0, h-70), (w, h), (30, 30, 60), -1)
        frame = cv2.addWeighted(frame, 0.6, overlay2, 0.4, 0)
        
        # Color del texto según el estado
        if estado == "completado":
            color_texto = (0, 255, 0)
        elif estado == "fallido":
            color_texto = (0, 0, 255)
        else:
            color_texto = self.colores['texto_principal']
        
        cv2.putText(frame, texto_estado, (20, h - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_texto, 2)
        
        return frame

    def mostrar(self, frame):
        """Muestra el frame en pantalla"""
        cv2.namedWindow("Music - Therapy", cv2.WINDOW_NORMAL)
        cv2.imshow("Music - Therapy", frame)