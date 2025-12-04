import cv2
import numpy as np
import time
from utils.camara import Camara
from utils.patrones import GeneradorPatrones
from utils.musica import GestorMusica
from vista import Vista


def main():
    # Configuración de la cámara IP
    cap = cv2.VideoCapture("http://192.168.1.37:4747/video")
    if not cap.isOpened():
        print("No se pudo acceder a la cámara IP.")
        return

    cam = Camara()
    vista = Vista()
    generador = GeneradorPatrones()
    musica = GestorMusica()  # Inicializar gestor de música

    score = 0
    rastro_usuario = []

    # Estado del juego
    estado = "esperando"

    # Variables de control
    posicion_anterior = None
    puntos_minimos_requeridos = 30
    mensaje_temporal = ""
    tiempo_mensaje = 0

    # Control de movimiento y ritmo
    hay_movimiento_actual = False
    combo_ritmo = 0  # Contador de beats consecutivos en ritmo
    max_combo = 0

    # Inicializar música y patrón
    musica.reiniciar_compas()

    while True:
        frame, is_fist, pos = cam.obtener_frame(cap)
        if frame is None:
            continue

        # Actualizar música y detectar beats
        hay_beat = musica.actualizar()
        progreso_beat = musica.obtener_progreso_beat()
        en_ventana_sincronizacion = musica.esta_en_ventana_sincronizacion()

        # Detectar si hay movimiento (cambio de posición significativo)
        hay_movimiento_actual = False
        if is_fist and pos[0] is not None and posicion_anterior is not None:
            distancia_movimiento = np.linalg.norm(
                np.array(pos) - np.array(posicion_anterior)
            )
            hay_movimiento_actual = distancia_movimiento > 8  # Movimiento mín de 8px

        # Verificar sincronización con el ritmo
        en_sincronizacion, perdio_ritmo = musica.verificar_sincronizacion(
            hay_movimiento_actual
        )

        # Actualizar combo
        if en_sincronizacion:
            combo_ritmo += 1
            max_combo = max(max_combo, combo_ritmo)
        elif perdio_ritmo:
            combo_ritmo = 0

        # Obtener tiempo restante según el ritmo musical
        tiempo_restante = int(musica.obtener_tiempo_restante_patron())
        beats_restantes = musica.obtener_beats_restantes()

        # LÓGICA DE ESTADOS
        if estado == "esperando":
            rastro_usuario = []
            combo_ritmo = 0

            # Verificar si está en el inicio con puño cerrado
            if is_fist and pos[0] is not None:
                distancia_inicio = generador.calcular_distancia_a_inicio(pos)
                if distancia_inicio < 50:
                    estado = "trazando"
                    rastro_usuario = [pos]
                    mensaje_temporal = "¡A bailar! Sigue el ritmo"
                    tiempo_mensaje = time.time()
                    musica.reiniciar_compas()
                    musica.reiniciar_estadisticas()

        elif estado == "trazando":
            # Solo agregar puntos si el puño está cerrado
            if is_fist and pos[0] is not None:
                if (
                    len(rastro_usuario) == 0
                    or np.linalg.norm(np.array(pos) - np.array(rastro_usuario[-1])) > 5
                ):
                    rastro_usuario.append(pos)

            # CRÍTICO: Si pierde el ritmo (3 beats), cambiar patrón
            if perdio_ritmo:
                estado = "fuera_ritmo"
                mensaje_temporal = "¡Perdiste el ritmo!"
                tiempo_mensaje = time.time()
                musica.reproducir_error()

            # Calcular progreso si hay suficientes puntos
            if len(rastro_usuario) >= 10:
                cobertura_total, llegado_al_final, porcentaje_patron = (
                    generador.calcular_progreso_detallado(rastro_usuario)
                )

                # Mostrar progreso y sincronización
                cv2.putText(
                    frame,
                    f"Cobertura: {int(cobertura_total*100)}%",
                    (10, frame.shape[0] - 140),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 0),
                    2,
                )
                cv2.putText(
                    frame,
                    f"Patron: {int(porcentaje_patron)}%",
                    (10, frame.shape[0] - 110),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (100, 200, 255),
                    2,
                )

                # COMPLETAR: Cobertura + final + mínimo de puntos
                if (
                    cobertura_total >= 0.75
                    and llegado_al_final
                    and len(rastro_usuario) >= puntos_minimos_requeridos
                ):

                    estado = "completado"
                    # Bonificación por combo y precisión
                    puntos_base = int(cobertura_total * 10)
                    # Hasta +20 por combo
                    bonus_combo = min(combo_ritmo * 2, 20)
                    precision_ritmo = musica.obtener_precision_ritmo()
                    # Hasta +10 por ritmo perfecto
                    bonus_ritmo = int(precision_ritmo / 10)

                    puntos_ganados = puntos_base + bonus_combo + bonus_ritmo
                    score += puntos_ganados

                    mensaje_temporal = (
                        f"¡PERFECTO! +{puntos_ganados} pts (Combo x{combo_ritmo})"
                    )
                    tiempo_mensaje = time.time()
                    musica.reproducir_exito()

            # Si llega al final del compás sin completar
            if musica.es_momento_de_nuevo_patron():
                if estado == "trazando":
                    estado = "fallido"
                    mensaje_temporal = "Tiempo agotado"
                    tiempo_mensaje = time.time()

        elif estado == "completado" or estado == "fallido" or estado == "fuera_ritmo":
            # Esperar al final del compás para cambiar de patrón
            if musica.es_momento_de_nuevo_patron():
                generador.generar_patron()
                rastro_usuario = []
                estado = "esperando"
                musica.reiniciar_compas()
                combo_ritmo = 0

        # DIBUJO EN PANTALLA
        # Dibujar el rastro del usuario
        if len(rastro_usuario) > 1:
            for i in range(1, len(rastro_usuario)):
                alpha = min(255, 100 + (i * 155 // len(rastro_usuario)))
                # Color según sincronización
                if en_sincronizacion:
                    color = (0, alpha, 0)  # Verde: en ritmo
                elif en_ventana_sincronizacion:
                    color = (0, alpha, alpha)  # Cian: cerca del beat
                else:
                    # Rojo-azul: fuera de ritmo
                    color = (0, int(alpha * 0.5), alpha)
                grosor = 3 if i == len(rastro_usuario) - 1 else 2
                cv2.line(frame, rastro_usuario[i - 1], rastro_usuario[i], color, grosor)

        # Dibujar la posición actual con indicador de ritmo
        if pos[0] is not None:
            if is_fist:
                # Color según sincronización
                if en_ventana_sincronizacion:
                    color_puno = (0, 255, 255) if en_sincronizacion else (0, 200, 255)
                    radio = 25 if hay_beat else 20
                else:
                    color_puno = (0, 150, 255)
                    radio = 18

                cv2.circle(frame, pos, radio, color_puno, -1)
                cv2.circle(frame, pos, radio + 3, (255, 255, 255), 3)

                # Anillo de sincronización
                if en_ventana_sincronizacion:
                    cv2.circle(frame, pos, radio + 8, (0, 255, 0), 2)
            else:
                cv2.circle(frame, pos, 12, (255, 0, 0), -1)
                cv2.circle(frame, pos, 16, (255, 255, 255), 2)

        # Dibujar el patrón objetivo
        frame = generador.dibujar_patron_en_frame(
            frame, rastro_usuario if estado == "trazando" else []
        )

        # Dibujar indicador visual de beat mejorado
        if musica.musica_activa:
            frame = vista.dibujar_indicador_beat(
                frame, progreso_beat, hay_beat, en_sincronizacion, combo_ritmo
            )

        # Dibujar interfaz con información de ritmo
        frame = vista.dibujar_interfaz(
            frame,
            score,
            tiempo_restante,
            estado,
            len(rastro_usuario),
            musica.bpm,
            musica.musica_activa,
            beats_restantes,
            combo_ritmo,
            max_combo,
            musica.obtener_precision_ritmo(),
        )

        # Mostrar mensaje temporal
        if time.time() - tiempo_mensaje < 2 and mensaje_temporal:
            h, w, _ = frame.shape
            cv2.rectangle(
                frame,
                (w // 2 - 300, h // 2 - 60),
                (w // 2 + 300, h // 2 + 60),
                (0, 0, 0),
                -1,
            )

            if estado == "completado":
                color_borde = (0, 255, 0)
            elif estado == "fuera_ritmo":
                color_borde = (0, 100, 255)
            else:
                color_borde = (0, 0, 255)

            cv2.rectangle(
                frame,
                (w // 2 - 300, h // 2 - 60),
                (w // 2 + 300, h // 2 + 60),
                color_borde,
                4,
            )

            texto_size = cv2.getTextSize(
                mensaje_temporal, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2
            )[0]
            texto_x = w // 2 - texto_size[0] // 2
            cv2.putText(
                frame,
                mensaje_temporal,
                (texto_x, h // 2 + 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2,
            )

        # Mostrar el frame
        vista.mostrar(frame)

        # Guardar posición anterior para detectar movimiento
        if pos[0] is not None:
            posicion_anterior = pos

        # Controles de teclado
        key = cv2.waitKey(1) & 0xFF

        if key == ord(" "):
            break
        elif key == ord("m") or key == ord("M"):
            if musica.musica_activa:
                musica.desactivar_musica()
            else:
                musica.activar_musica()
        elif key == ord("+") or key == ord("="):
            musica.cambiar_bpm(musica.bpm + 10)
        elif key == ord("-") or key == ord("_"):
            musica.cambiar_bpm(musica.bpm - 10)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
