controlador.py
import cv2
import numpy as np
import time
from utils.camara import Camara
from utils.patrones import GeneradorPatrones
from vista import Vista

def main():
    # Configuración de la cámara IP
    cap = cv2.VideoCapture("http://192.168.1.37:4747/video")
    if not cap.isOpened():
        print("No se pudo acceder a la camara IP.")
        return

    cam = Camara()
    vista = Vista()
    generador = GeneradorPatrones()

    score = 0
    rastro_usuario = []
    tiempo_inicio_patron = time.time()
    tiempo_limite = 20  # 45 segundos para completar cada patrón
    
    # Estado del juego
    estado = "esperando"  # esperando, trazando, completado, fallido
    
    # Variables de control
    ultimo_estado_puno = False
    puntos_minimos_requeridos = 50  # Mínimo de puntos para considerar un trazo válido
    mensaje_temporal = ""
    tiempo_mensaje = 0

    while True:
        frame, is_fist, pos = cam.obtener_frame(cap)
        if frame is None:
            continue

        # LÓGICA DE ESTADOS
        if estado == "esperando":
            # Resetear el rastro
            rastro_usuario = []
            
            # Verificar si el usuario está en el punto de inicio con puño cerrado
            if is_fist and pos[0] is not None:
                distancia_inicio = generador.calcular_distancia_a_inicio(pos)
                if distancia_inicio < 50:  # Debe estar cerca del inicio
                    estado = "trazando"
                    tiempo_inicio_patron = time.time()
                    rastro_usuario = [pos]
                    mensaje_temporal = "Comenzando. Sigue todo el patron"
                    tiempo_mensaje = time.time()
        
        elif estado == "trazando":
            # Solo agregar puntos si el puño está cerrado
            if is_fist and pos[0] is not None:
                # Evitar agregar puntos duplicados muy cercanos
                if len(rastro_usuario) == 0 or \
                   np.linalg.norm(np.array(pos) - np.array(rastro_usuario[-1])) > 5:
                    rastro_usuario.append(pos)
            
            # Verificar tiempo transcurrido
            tiempo_transcurrido = time.time() - tiempo_inicio_patron
            
            # Calcular progreso continuo si hay suficientes puntos
            if len(rastro_usuario) >= 10:
                cobertura_total, llegado_al_final, porcentaje_patron = generador.calcular_progreso_detallado(rastro_usuario)
                
                # Mostrar progreso en pantalla
                cv2.putText(frame, f"Cobertura: {int(cobertura_total*100)}%", (10, frame.shape[0] - 100),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                cv2.putText(frame, f"Patron: {int(porcentaje_patron)}%", (10, frame.shape[0] - 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 200, 255), 2)
                
                # CONDICIONES ESTRICTAS PARA COMPLETAR:
                # 1. Cobertura >= 85% (pasaste por casi todo el patrón)
                # 2. Llegaste al punto final (dentro de 60px)
                # 3. Mínimo de puntos capturados
                if (cobertura_total >= 0.85 and 
                    llegado_al_final and 
                    len(rastro_usuario) >= puntos_minimos_requeridos):
                    
                    estado = "completado"
                    puntos_ganados = int(cobertura_total * 15)  # Hasta 15 puntos según precisión
                    score += puntos_ganados
                    mensaje_temporal = f"Patron completado: +{puntos_ganados} puntos"
                    tiempo_mensaje = time.time()
            
            # Tiempo límite agotado
            if tiempo_transcurrido > tiempo_limite:
                estado = "fallido"
                mensaje_temporal = "Tiempo agotado - Intenta de nuevo"
                tiempo_mensaje = time.time()
        
        elif estado == "completado" or estado == "fallido":
            # Mostrar resultado por 3 segundos
            if time.time() - tiempo_mensaje > 3:
                generador.generar_patron()
                rastro_usuario = []
                estado = "esperando"
                tiempo_inicio_patron = time.time()

        # DIBUJO EN PANTALLA
        # Dibujar el rastro del usuario con degradado
        if len(rastro_usuario) > 1:
            for i in range(1, len(rastro_usuario)):
                # Degradado: más viejo = más oscuro
                alpha = min(255, 100 + (i * 155 // len(rastro_usuario)))
                color = (0, alpha, 0)
                grosor = 3 if i == len(rastro_usuario) - 1 else 2
                cv2.line(frame, rastro_usuario[i-1], rastro_usuario[i], color, grosor)
        
        # Dibujar la posición actual
        if pos[0] is not None:
            if is_fist:
                # Puño cerrado - verde grande
                cv2.circle(frame, pos, 20, (0, 255, 0), -1)
                cv2.circle(frame, pos, 25, (255, 255, 255), 3)
            else:
                # Mano abierta - azul pequeño
                cv2.circle(frame, pos, 12, (255, 0, 0), -1)
                cv2.circle(frame, pos, 16, (255, 255, 255), 2)

        # Dibujar el patrón objetivo con puntos de progreso
        frame = generador.dibujar_patron_en_frame(frame, rastro_usuario if estado == "trazando" else [])

        # Calcular tiempo restante
        tiempo_transcurrido = time.time() - tiempo_inicio_patron
        tiempo_restante = max(0, int(tiempo_limite - tiempo_transcurrido))

        # Dibujar interfaz
        frame = vista.dibujar_interfaz(frame, score, tiempo_restante, estado, len(rastro_usuario))
        
        # Mostrar mensaje temporal (más grande y prominente)
        if time.time() - tiempo_mensaje < 2 and mensaje_temporal:
            h, w, _ = frame.shape
            # Fondo para el mensaje
            cv2.rectangle(frame, (w//2 - 300, h//2 - 60), (w//2 + 300, h//2 + 60), (0, 0, 0), -1)
            
            color_borde = (0, 255, 0) if estado == "completado" else (0, 0, 255) if estado == "fallido" else (255, 255, 0)
            cv2.rectangle(frame, (w//2 - 300, h//2 - 60), (w//2 + 300, h//2 + 60), color_borde, 4)
            
            # Texto del mensaje
            texto_size = cv2.getTextSize(mensaje_temporal, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
            texto_x = w//2 - texto_size[0]//2
            cv2.putText(frame, mensaje_temporal, (texto_x, h//2 + 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        # Mostrar el frame
        vista.mostrar(frame)
        
        # Actualizar estado anterior del puño
        ultimo_estado_puno = is_fist

        # Salir con espacio
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()